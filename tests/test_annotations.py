from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


class AnnotationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        schema = load_json(ROOT / "schemas" / "evidence-annotation.schema.json")
        cls.validator = Draft202012Validator(schema)
        cls.covid_paths = sorted(
            (ROOT / "data" / "annotations" / "covid-origins" / "evidence").glob("*.json")
        )
        cls.covid_annotations = [load_json(path) for path in cls.covid_paths]

    def test_all_covid_annotations_conform_to_schema(self) -> None:
        self.assertEqual(len(self.covid_annotations), 40)
        for path, annotation in zip(self.covid_paths, self.covid_annotations, strict=True):
            with self.subTest(path=path.name):
                errors = sorted(self.validator.iter_errors(annotation), key=lambda error: list(error.path))
                self.assertEqual(errors, [], "\n".join(error.message for error in errors))

    def test_every_covid_item_has_substantive_structural_review(self) -> None:
        for annotation in self.covid_annotations:
            with self.subTest(evidence_id=annotation["evidence"]["evidence_id"]):
                self.assertEqual(annotation["annotation_status"], "provisionally_reviewed")
                self.assertEqual(annotation["review"]["review_basis"], "baseline_document_only")
                self.assertEqual(annotation["review"]["verification_status"], "not_checked")
                self.assertTrue(annotation["review"]["framing_assumptions"])
                self.assertTrue(annotation["review"]["policy_sensitivities"])
                self.assertTrue(annotation["review"]["coverage_gaps"])
                self.assertTrue(annotation["review"]["correlation_risks"])
                self.assertTrue(annotation["review"]["capability_limits"])

    def test_source_registry_is_complete_and_marks_reuse(self) -> None:
        sources = load_json(ROOT / "data" / "annotations" / "covid-origins" / "sources.json")
        self.assertEqual(len(sources), 173)
        self.assertTrue(all(source["review"]["quality_assessment"] for source in sources))
        self.assertTrue(all(source["review"]["verification_status"] == "not_checked" for source in sources))
        reused = [source for source in sources if source["review"]["independence_notes"]]
        self.assertGreaterEqual(len(reused), 1)
        self.assertTrue(all(len(source["occurrences"]) > 1 for source in reused))

    def test_declared_source_policies_conform_to_schema(self) -> None:
        schema = load_json(ROOT / "schemas" / "source-policy.schema.json")
        validator = Draft202012Validator(schema)
        policies = sorted((ROOT / "data" / "policies").glob("*.json"))
        self.assertTrue(policies)
        for path in policies:
            with self.subTest(path=path.name):
                errors = list(validator.iter_errors(load_json(path)))
                self.assertEqual(errors, [], "\n".join(error.message for error in errors))

    def test_fixed_corpus_experiment_conforms_and_covers_every_covid_record(self) -> None:
        schema = load_json(ROOT / "schemas" / "fixed-corpus-experiment.schema.json")
        spec = load_json(ROOT / "data" / "experiments" / "covid-fixed-corpus-v1.json")
        errors = list(Draft202012Validator(schema).iter_errors(spec))
        self.assertEqual(errors, [], "\n".join(error.message for error in errors))

        clustered_ids = [
            evidence_id
            for cluster in spec["evidence_clusters"]
            for evidence_id in cluster["evidence_ids"]
        ]
        expected_ids = {
            annotation["evidence"]["evidence_id"] for annotation in self.covid_annotations
        }
        self.assertEqual(len(clustered_ids), len(set(clustered_ids)))
        self.assertEqual(set(clustered_ids), expected_ids)

    def test_generated_policy_runs_are_nested_and_graph_is_traceable(self) -> None:
        catalog = load_json(ROOT / "site" / "data" / "catalog.json")
        experiment = catalog["experiments"][0]
        runs = experiment["runs"]
        self.assertEqual([len(run["included_evidence_ids"]) for run in runs], [23, 37, 40])
        self.assertTrue(set(runs[0]["included_evidence_ids"]) < set(runs[1]["included_evidence_ids"]))
        self.assertTrue(set(runs[1]["included_evidence_ids"]) < set(runs[2]["included_evidence_ids"]))

        nodes = {node["node_id"]: node for node in experiment["graph"]["nodes"]}
        self.assertEqual(len([node for node in nodes.values() if node["node_type"] == "claim"]), 40)
        self.assertEqual(len([node for node in nodes.values() if node["node_type"] == "warrant"]), 40)
        for edge in experiment["graph"]["edges"]:
            self.assertIn(edge["source"], nodes)
            self.assertIn(edge["target"], nodes)


if __name__ == "__main__":
    unittest.main()
