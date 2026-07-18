"""Build a policy-ablation experiment over an immutable evidence corpus."""

from __future__ import annotations

from collections import defaultdict
from typing import Any


HYPOTHESIS_BY_DIRECTION = {
    "natural-origin": "natural-origin",
    "lab-leak": "research-related",
    "neutral": "underdetermined",
}


def _validate_clusters(
    evidence: list[dict[str, Any]], clusters: list[dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    evidence_ids = {item["evidence"]["evidence_id"] for item in evidence}
    cluster_by_evidence: dict[str, dict[str, Any]] = {}
    for cluster in clusters:
        for evidence_id in cluster["evidence_ids"]:
            if evidence_id in cluster_by_evidence:
                previous = cluster_by_evidence[evidence_id]["cluster_id"]
                raise ValueError(
                    f"Evidence {evidence_id!r} belongs to both {previous!r} and "
                    f"{cluster['cluster_id']!r}"
                )
            cluster_by_evidence[evidence_id] = cluster

    assigned = set(cluster_by_evidence)
    if assigned != evidence_ids:
        missing = sorted(evidence_ids - assigned)
        extra = sorted(assigned - evidence_ids)
        raise ValueError(f"Experiment cluster coverage mismatch; missing={missing}, extra={extra}")
    return cluster_by_evidence


def _policy_includes(policy: dict[str, Any], evidence: dict[str, Any]) -> bool:
    selection = policy["selection"]
    return bool(
        selection["include_all"]
        or evidence["evidence_type"] in selection["evidence_types"]
        or evidence["evidence_id"] in selection["evidence_ids"]
    )


def _conclusion(natural: float, research: float) -> str:
    total = natural + research
    if total == 0:
        return "No directional assessment can be generated from this policy."
    share = natural / total
    if share >= 0.60:
        return "The retained annotated support favors natural origin."
    if share <= 0.40:
        return "The retained annotated support favors a research-related origin."
    return "The retained annotated support is mixed between the two hypotheses."


def _build_assessment(
    included: list[dict[str, Any]],
    cluster_by_evidence: dict[str, dict[str, Any]],
    method: dict[str, Any],
) -> dict[str, Any]:
    scale = method["strength_scale"]
    candidates: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    neutral_evidence_ids: list[str] = []
    uncertainty_counts: dict[str, int] = defaultdict(int)

    for annotation in included:
        evidence = annotation["evidence"]
        evidence_id = evidence["evidence_id"]
        direction = evidence["direction"]
        cluster_id = cluster_by_evidence[evidence_id]["cluster_id"]
        if direction == "neutral":
            neutral_evidence_ids.append(evidence_id)
        else:
            candidates[(cluster_id, direction)].append(annotation)
        for category, notes in annotation["review"]["uncertainty_attribution"].items():
            uncertainty_counts[category] += len(notes)

    contributions: list[dict[str, Any]] = []
    totals = {"natural-origin": 0.0, "lab-leak": 0.0}
    for (cluster_id, direction), annotations in sorted(candidates.items()):
        max_value = max(scale.get(item["evidence"]["support_strength"], 0) for item in annotations)
        representative_ids = sorted(
            item["evidence"]["evidence_id"]
            for item in annotations
            if scale.get(item["evidence"]["support_strength"], 0) == max_value
        )
        totals[direction] += max_value
        contributions.append(
            {
                "cluster_id": cluster_id,
                "direction": direction,
                "strength": max_value,
                "representative_evidence_ids": representative_ids,
                "included_evidence_ids": sorted(
                    item["evidence"]["evidence_id"] for item in annotations
                ),
            }
        )

    directional_total = totals["natural-origin"] + totals["lab-leak"]
    balance = {
        "natural-origin": (
            round(totals["natural-origin"] / directional_total, 3)
            if directional_total
            else None
        ),
        "research-related": (
            round(totals["lab-leak"] / directional_total, 3)
            if directional_total
            else None
        ),
    }
    return {
        "conclusion": _conclusion(totals["natural-origin"], totals["lab-leak"]),
        "support_points": {
            "natural-origin": totals["natural-origin"],
            "research-related": totals["lab-leak"],
        },
        "support_balance": balance,
        "cluster_contributions": contributions,
        "neutral_evidence_ids": sorted(neutral_evidence_ids),
        "uncertainty_signal_counts": dict(sorted(uncertainty_counts.items())),
        "method_note": method["interpretation"],
    }


def build_fixed_corpus_experiment(
    case_data: dict[str, Any], spec: dict[str, Any]
) -> dict[str, Any]:
    """Create policy runs and a traceable claim-warrant graph."""

    evidence = case_data["evidence"]
    cluster_by_evidence = _validate_clusters(evidence, spec["evidence_clusters"])
    all_evidence_ids = {item["evidence"]["evidence_id"] for item in evidence}

    graph_nodes: list[dict[str, Any]] = [
        {
            "node_id": "hypothesis:natural-origin",
            "node_type": "hypothesis",
            "label": "Natural origin",
            "direction": "natural-origin",
        },
        {
            "node_id": "hypothesis:research-related",
            "node_type": "hypothesis",
            "label": "Research-related origin",
            "direction": "lab-leak",
        },
        {
            "node_id": "hypothesis:underdetermined",
            "node_type": "hypothesis",
            "label": "Underdetermined / process evidence",
            "direction": "neutral",
        },
    ]
    graph_edges: list[dict[str, Any]] = []

    for cluster in spec["evidence_clusters"]:
        graph_nodes.append(
            {
                "node_id": f"cluster:{cluster['cluster_id']}",
                "node_type": "independence_cluster",
                "label": cluster["label"],
                "description": cluster["description"],
                "evidence_ids": cluster["evidence_ids"],
            }
        )

    for annotation in evidence:
        item = annotation["evidence"]
        evidence_id = item["evidence_id"]
        cluster = cluster_by_evidence[evidence_id]
        hypothesis_id = HYPOTHESIS_BY_DIRECTION[item["direction"]]
        assumptions = annotation["review"]["framing_assumptions"]
        warrant_text = assumptions[0] if assumptions else "No inferential warrant supplied."
        claim_node_id = f"claim:{evidence_id}"
        warrant_node_id = f"warrant:{evidence_id}"
        graph_nodes.extend(
            [
                {
                    "node_id": claim_node_id,
                    "node_type": "claim",
                    "label": item["title"],
                    "claim": item["claim"],
                    "evidence_id": evidence_id,
                    "evidence_type": item["evidence_type"],
                    "direction": item["direction"],
                    "support_strength": item["support_strength"],
                    "source_ids": [source["source_id"] for source in item["citations"]],
                    "coverage_gaps": annotation["review"]["coverage_gaps"],
                },
                {
                    "node_id": warrant_node_id,
                    "node_type": "warrant",
                    "label": warrant_text,
                    "evidence_id": evidence_id,
                    "direction": item["direction"],
                    "policy_sensitivities": annotation["review"]["policy_sensitivities"],
                    "correlation_risks": annotation["review"]["correlation_risks"],
                },
            ]
        )
        graph_edges.extend(
            [
                {
                    "source": claim_node_id,
                    "target": warrant_node_id,
                    "edge_type": "interpreted_through",
                },
                {
                    "source": warrant_node_id,
                    "target": f"hypothesis:{hypothesis_id}",
                    "edge_type": "bears_on",
                },
                {
                    "source": claim_node_id,
                    "target": f"cluster:{cluster['cluster_id']}",
                    "edge_type": "shares_evidence_family",
                },
            ]
        )

    runs: list[dict[str, Any]] = []
    previous_ids: set[str] = set()
    for policy in spec["policies"]:
        included = [
            annotation
            for annotation in evidence
            if _policy_includes(policy, annotation["evidence"])
        ]
        included_ids = {item["evidence"]["evidence_id"] for item in included}
        source_ids = {
            source["source_id"]
            for annotation in included
            for source in annotation["evidence"]["citations"]
        }
        runs.append(
            {
                "run_id": f"{spec['experiment_id']}:{policy['policy_id']}",
                "policy_id": policy["policy_id"],
                "label": policy["label"],
                "description": policy["description"],
                "included_evidence_ids": sorted(included_ids),
                "excluded_evidence_ids": sorted(all_evidence_ids - included_ids),
                "included_source_ids": sorted(source_ids),
                "added_since_previous_run": sorted(included_ids - previous_ids),
                "assessment": _build_assessment(
                    included, cluster_by_evidence, spec["assessment_method"]
                ),
            }
        )
        if previous_ids and not previous_ids.issubset(included_ids):
            raise ValueError(f"Experiment policies are not nested at {policy['policy_id']!r}")
        previous_ids = included_ids

    return {
        "schema_version": spec["schema_version"],
        "experiment_id": spec["experiment_id"],
        "case_id": spec["case_id"],
        "baseline_id": spec["baseline_id"],
        "question": spec["question"],
        "corpus_is_fixed": True,
        "assessment_method": spec["assessment_method"],
        "coverage_report": spec["coverage_report"],
        "clusters": spec["evidence_clusters"],
        "runs": runs,
        "graph": {"nodes": graph_nodes, "edges": graph_edges},
    }
