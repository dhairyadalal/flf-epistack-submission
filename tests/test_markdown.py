from __future__ import annotations

import unittest
from pathlib import Path

from epistemic_audit.markdown import load_corpus, parse_frontmatter, source_class


ROOT = Path(__file__).resolve().parents[1]


class FrontmatterTests(unittest.TestCase):
    def test_flat_frontmatter_is_parsed(self) -> None:
        metadata, body = parse_frontmatter('---\ntitle: "Example"\nscore: 0.8\n---\n\nBody')
        self.assertEqual(metadata, {"title": "Example", "score": "0.8"})
        self.assertEqual(body.strip(), "Body")

    def test_unterminated_frontmatter_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            parse_frontmatter("---\ntitle: Example\n")


class CorpusTests(unittest.TestCase):
    def test_imported_covid_corpus_has_expected_shape(self) -> None:
        corpus = load_corpus(ROOT / "flf-epistack-contest-main")
        self.assertEqual(len(corpus), 40)
        self.assertTrue(all(item.claim for item in corpus))
        self.assertTrue(all(item.citations for item in corpus))

    def test_eggs_corpus_spans_four_framings(self) -> None:
        corpus = load_corpus(ROOT / "data" / "baselines" / "eggs")
        self.assertEqual(len(corpus), 4)
        self.assertEqual(
            {item.direction for item in corpus},
            {"health-population", "health-individual", "animal-welfare", "environmental-impact"},
        )

    def test_source_class_is_broad_not_a_quality_score(self) -> None:
        self.assertEqual(
            source_class("Example", ("https://doi.org/10.1000/example",)),
            "scholarly_publication",
        )
        self.assertEqual(
            source_class("Example", ("https://www.npr.org/example",)),
            "journalism",
        )


if __name__ == "__main__":
    unittest.main()

