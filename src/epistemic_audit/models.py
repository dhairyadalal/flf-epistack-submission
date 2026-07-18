"""Small data objects shared by ingestion and export.

The JSON Schema files are the interoperability contract. These dataclasses keep
the Python implementation explicit without introducing a validation framework.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


SCHEMA_VERSION = "0.1.0"


@dataclass(frozen=True)
class SourceCitation:
    """A source citation extracted from one baseline evidence document."""

    source_id: str
    citation: str
    urls: tuple[str, ...]
    source_class: str
    classification_method: str = "citation_text_heuristic"
    verification_status: str = "not_checked"
    language: str = "unknown"
    access_status: str = "unknown"

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["urls"] = list(self.urls)
        return value


@dataclass(frozen=True)
class BaselineEvidence:
    """An evidence item as asserted by a baseline corpus."""

    evidence_id: str
    title: str
    direction: str
    evidence_type: str
    claim_confidence: float | None
    support_strength: str
    claim: str
    evidence_quality: str
    strongest_counterargument: str
    confidence_assessment: str
    source_path: str
    citations: tuple[SourceCitation, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class EvidenceAnnotation:
    """Our annotation wrapper around a baseline evidence assertion."""

    annotation_id: str
    case_id: str
    baseline_id: str
    evidence: BaselineEvidence
    upstream_author: str
    upstream_generation_method: str
    annotation_status: str = "extracted_not_verified"

    def to_dict(self) -> dict[str, Any]:
        evidence = asdict(self.evidence)
        evidence["citations"] = [citation.to_dict() for citation in self.evidence.citations]
        return {
            "schema_version": SCHEMA_VERSION,
            "annotation_id": self.annotation_id,
            "case_id": self.case_id,
            "baseline_id": self.baseline_id,
            "provenance": {
                "upstream_author": self.upstream_author,
                "upstream_generation_method": self.upstream_generation_method,
                "annotation_method": "deterministic_extraction_and_provisional_classification",
            },
            "annotation_status": self.annotation_status,
            "evidence": evidence,
            "review": {
                "verification_status": "not_checked",
                "review_basis": "baseline_document_only",
                "framing_assumptions": [],
                "policy_sensitivities": [],
                "coverage_gaps": [],
                "correlation_risks": [],
                "capability_limits": [],
                "uncertainty_attribution": {
                    "evidential": [],
                    "ingestion_conditional": [],
                    "capability_conditional": [],
                    "framing_conditional": [],
                    "unattributed": [
                        "The baseline assessment has not yet been independently audited."
                    ],
                },
                "notes": [
                    "Baseline prose and scores are preserved as claims by the upstream run, not adopted as our judgments."
                ],
            },
        }
