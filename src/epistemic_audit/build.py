"""Build canonical annotations and browser-ready data from baseline Markdown."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .experiment import build_fixed_corpus_experiment, build_framing_experiment
from .markdown import load_corpus
from .models import EvidenceAnnotation, SCHEMA_VERSION


ROOT = Path(__file__).resolve().parents[2]


CASES = (
    {
        "case_id": "covid-origins",
        "baseline_id": "carlo-claude-unattended-2026-06-25",
        "root": ROOT / "carlo-baseline",
        "upstream_author": "Claude (baseline supplied by Carlo)",
        "generation_method": "23-minute unattended Claude Code swarm",
    },
    {
        "case_id": "eggs",
        "baseline_id": "audit-lower-layers-eggs-starter-2026-07-18",
        "root": ROOT / "data" / "baselines" / "eggs",
        "upstream_author": "Audit the Lower Layers team",
        "generation_method": "curated starter baseline with declared framings",
    },
)


SOURCE_CLASS_NOTES = {
    "scholarly_publication": "Scholarly publication or index record. Peer-review status, study design, and relevance still require content checking.",
    "preprint": "Preprint or explicitly non-peer-reviewed research. Treat conclusions as provisional and check for later versions or replies.",
    "government_or_intergovernmental": "Official or intergovernmental source. Useful for institutional facts, but not automatically independent or scientifically dispositive.",
    "journalism": "Journalistic source. Useful for attributed statements and document discovery; generally secondary evidence for scientific claims.",
    "commentary_or_advocacy": "Commentary or advocacy source. Perspective and source discovery may be useful, but incentives and primary-document support need explicit checking.",
    "reference_work": "Reference work. Useful for orientation, not a substitute for the underlying sources.",
    "unclassified": "Source class could not be established from citation text alone.",
}


CAPABILITY_LIMITS = {
    "epidemiological": "Assessing sampling, ascertainment, and spatial or temporal inference requires raw data and specialist statistical review beyond the supplied summary.",
    "genomic": "Assessing phylogenetic or genomic inference requires sequence-level analysis and domain expertise beyond the supplied summary.",
    "virological": "Assessing experimental virology requires checking methods, model systems, and replication in the cited studies.",
    "documentary": "Document interpretation depends on completeness, provenance, surrounding context, and access to the original record.",
    "intelligence-assessment": "Most underlying intelligence is unavailable, preventing independent evaluation of source quality and analytic tradecraft.",
    "circumstantial": "Circumstantial patterns are especially sensitive to base rates, alternative explanations, and selection of which coincidences are noticed.",
    "biosafety": "Evaluating biosafety relevance requires facility-specific procedures and incident records that are not present in the supplied corpus.",
}


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_review_catalog(case_id: str) -> dict[str, Any] | None:
    path = ROOT / "data" / "reviews" / f"{case_id}-v1.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def apply_review_catalog(
    annotations: list[dict[str, Any]], catalog: dict[str, Any] | None
) -> None:
    if catalog is None:
        return

    reviews = catalog["reviews"]
    evidence_ids = {item["evidence"]["evidence_id"] for item in annotations}
    if set(reviews) != evidence_ids:
        missing = sorted(evidence_ids - set(reviews))
        extra = sorted(set(reviews) - evidence_ids)
        raise ValueError(f"Review coverage mismatch; missing={missing}, extra={extra}")

    for annotation in annotations:
        evidence = annotation["evidence"]
        supplied = reviews[evidence["evidence_id"]]
        annotation["annotation_status"] = "provisionally_reviewed"
        annotation["provenance"]["reviewer"] = catalog["reviewer"]
        annotation["provenance"]["review_method"] = catalog["review_method"]
        review = annotation["review"]
        supplied_fields = dict(supplied)
        uncertainty = supplied_fields.pop("uncertainty_attribution", {})
        review.update(supplied_fields)
        review["uncertainty_attribution"].update(uncertainty)
        review["verification_status"] = "not_checked"
        review["review_basis"] = "baseline_document_only"
        review["capability_limits"] = [
            CAPABILITY_LIMITS.get(
                evidence["evidence_type"],
                "The supplied summary was reviewed without a systematic full-text audit of every cited source.",
            ),
            *review.get("capability_limits", []),
        ]
        review["notes"] = [
            *review.get("notes", []),
            "This is a substantive structural annotation of the supplied evidence note, not an independent finding that its factual claim is true.",
        ]


def build_case(config: dict[str, Any], annotations_root: Path) -> dict[str, Any]:
    evidence_items = load_corpus(config["root"])
    review_catalog = load_review_catalog(config["case_id"])
    annotations: list[dict[str, Any]] = []
    source_registry: dict[str, dict[str, Any]] = {}

    output_dir = annotations_root / config["case_id"]
    for evidence in evidence_items:
        annotation = EvidenceAnnotation(
            annotation_id=f"ann_{config['case_id']}_{evidence.evidence_id}_v1",
            case_id=config["case_id"],
            baseline_id=config["baseline_id"],
            evidence=evidence,
            upstream_author=config["upstream_author"],
            upstream_generation_method=config["generation_method"],
        ).to_dict()
        annotations.append(annotation)

        for source in evidence.citations:
            record = source_registry.setdefault(
                source.source_id,
                {
                    "schema_version": SCHEMA_VERSION,
                    **source.to_dict(),
                    "occurrences": [],
                    "review": {
                        "verification_status": "not_checked",
                        "quality_assessment": None,
                        "independence_notes": [],
                        "limitations": [],
                    },
                },
            )
            record["occurrences"].append(
                {"evidence_id": evidence.evidence_id, "case_id": config["case_id"]}
            )

    apply_review_catalog(annotations, review_catalog)
    for annotation in annotations:
        evidence_id = annotation["evidence"]["evidence_id"]
        write_json(output_dir / "evidence" / f"{evidence_id}.json", annotation)

    sources = sorted(source_registry.values(), key=lambda item: item["source_id"])
    for source in sources:
        occurrence_count = len(source["occurrences"])
        source["review"]["quality_assessment"] = SOURCE_CLASS_NOTES[source["source_class"]]
        if occurrence_count > 1:
            source["review"]["independence_notes"].append(
                f"Reused across {occurrence_count} evidence items; repeated citation is not independent confirmation."
            )
        if not source["urls"]:
            source["review"]["limitations"].append(
                "No directly extractable URL was supplied, so source identity and access require manual resolution."
            )
        source["review"]["limitations"].append(
            "Classification is based on citation text only; source content has not been independently checked."
        )
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "case_id": config["case_id"],
        "baseline_id": config["baseline_id"],
        "evidence_count": len(annotations),
        "unique_source_count": len(sources),
        "annotation_status": (
            "provisionally_reviewed"
            if review_catalog is not None
            else "extracted_not_verified"
        ),
    }
    write_json(output_dir / "manifest.json", manifest)
    write_json(output_dir / "sources.json", sources)
    return {"manifest": manifest, "evidence": annotations, "sources": sources}


def build(annotations_root: Path, site_output: Path) -> dict[str, Any]:
    cases = [build_case(config, annotations_root) for config in CASES]
    policies = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((ROOT / "data" / "policies").glob("*.json"))
    ]
    experiments = []
    for path in sorted((ROOT / "data" / "experiments").glob("*.json")):
        spec = json.loads(path.read_text(encoding="utf-8"))
        case_data = next(case for case in cases if case["manifest"]["case_id"] == spec["case_id"])
        if spec["experiment_type"] == "fixed_corpus_ablation":
            experiments.append(build_fixed_corpus_experiment(case_data, spec))
        elif spec["experiment_type"] == "framing_comparison":
            experiments.append(build_framing_experiment(case_data, spec, policies))
        else:
            raise ValueError(f"Unsupported experiment type: {spec['experiment_type']}")

    catalog = {
        "schema_version": SCHEMA_VERSION,
        "generated_from": "versioned baseline Markdown and explicit policy fixtures",
        "cases": cases,
        "policies": policies,
        "experiments": experiments,
    }
    write_json(site_output / "catalog.json", catalog)
    return catalog


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--annotations-root",
        type=Path,
        default=ROOT / "data" / "annotations",
    )
    parser.add_argument(
        "--site-output",
        type=Path,
        default=ROOT / "site" / "data",
    )
    args = parser.parse_args()
    catalog = build(args.annotations_root, args.site_output)
    totals = [case["manifest"] for case in catalog["cases"]]
    print(
        "Built "
        + ", ".join(
            f"{item['case_id']}: {item['evidence_count']} evidence / {item['unique_source_count']} sources"
            for item in totals
        )
    )


if __name__ == "__main__":
    main()
