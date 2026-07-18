"""Parse the deliberately small Markdown format used by the baseline corpora."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from .models import BaselineEvidence, SourceCitation


URL_RE = re.compile(r"https?://[^\s)]+")
SOURCE_LINE_RE = re.compile(r"^\s*\d+\.\s+(.*)$")


def _strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Parse flat YAML-like frontmatter without silently accepting nesting."""

    if not text.startswith("---\n"):
        raise ValueError("Expected Markdown frontmatter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("Unterminated Markdown frontmatter")

    values: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            raise ValueError(f"Unsupported frontmatter line: {line!r}")
        key, value = line.split(":", 1)
        values[key.strip()] = _strip_quotes(value)
    return values, text[end + 5 :]


def split_sections(body: str) -> dict[str, str]:
    """Return second-level Markdown sections keyed by normalized heading."""

    sections: dict[str, list[str]] = {}
    current = "preamble"
    sections[current] = []
    for line in body.splitlines():
        if line.startswith("## "):
            current = line[3:].strip().lower()
            sections.setdefault(current, [])
        else:
            sections[current].append(line)
    return {key: "\n".join(lines).strip() for key, lines in sections.items()}


def source_class(citation: str, urls: tuple[str, ...]) -> str:
    """Apply a broad, non-evaluative citation classification heuristic."""

    text = f"{citation} {' '.join(urls)}".lower()
    if any(
        token in text
        for token in (
            "doi.org",
            "pubmed",
            "pmc.ncbi",
            "nature.com/articles",
            "science.org",
            "pnas.org",
            "journals.asm.org",
            "thelancet.com",
            "academic.oup.com",
        )
    ):
        return "scholarly_publication"
    if "arxiv" in text or "preprint" in text:
        return "preprint"
    if any(token in text for token in (".gov", "who.int", "odni", "darpa", "house.gov")):
        return "government_or_intergovernmental"
    if "wikipedia" in text or "wikisource" in text:
        return "reference_work"
    if any(
        token in text
        for token in (
            "reuters",
            "npr.org",
            "cnn.com",
            "bbc.",
            "nytimes.com",
            "washingtonpost.com",
            "wsj.com",
            "newsweek.com",
            "nbcnews.com",
            "cbsnews.com",
        )
    ):
        return "journalism"
    if any(token in text for token in ("substack", "blog", "usrtk.org", "public.news")):
        return "commentary_or_advocacy"
    return "unclassified"


def _source_id(citation: str, urls: tuple[str, ...]) -> str:
    key = urls[0].rstrip(".,;") if urls else citation.casefold().strip()
    return "src_" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:12]


def parse_sources(section: str) -> tuple[SourceCitation, ...]:
    citations: list[SourceCitation] = []
    for line in section.splitlines():
        match = SOURCE_LINE_RE.match(line)
        if not match:
            continue
        citation = match.group(1).strip()
        urls = tuple(url.rstrip(".,;") for url in URL_RE.findall(citation))
        citations.append(
            SourceCitation(
                source_id=_source_id(citation, urls),
                citation=citation,
                urls=urls,
                source_class=source_class(citation, urls),
            )
        )
    return tuple(citations)


def parse_evidence(path: Path, relative_to: Path) -> BaselineEvidence:
    metadata, body = parse_frontmatter(path.read_text(encoding="utf-8"))
    sections = split_sections(body)
    confidence_text = metadata.get("claim_confidence", "")
    try:
        confidence = float(confidence_text)
    except ValueError:
        confidence = None

    return BaselineEvidence(
        evidence_id=metadata.get("slug", path.stem),
        title=metadata.get("title", path.stem),
        direction=metadata.get("direction", "unspecified"),
        evidence_type=metadata.get("evidence_type", "unspecified"),
        claim_confidence=confidence,
        support_strength=metadata.get("support_strength", "unspecified"),
        claim=sections.get("claim", ""),
        evidence_quality=sections.get("evidence quality", ""),
        strongest_counterargument=sections.get("strongest counterargument", ""),
        confidence_assessment=sections.get("confidence assessment", ""),
        source_path=str(path.relative_to(relative_to)),
        citations=parse_sources(sections.get("sources", "")),
    )


def load_corpus(root: Path) -> list[BaselineEvidence]:
    evidence_dir = root / "evidence"
    if not evidence_dir.is_dir():
        raise ValueError(f"Missing evidence directory: {evidence_dir}")
    return [parse_evidence(path, root) for path in sorted(evidence_dir.glob("*.md"))]
