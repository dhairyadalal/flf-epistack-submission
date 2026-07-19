from __future__ import annotations

import json
import unittest

from epistemic_audit.server import (
    MAX_HISTORY_MESSAGES,
    SYSTEM_INSTRUCTIONS,
    build_case_context,
    build_messages,
    load_catalog,
    validate_history,
)


class ServerContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = load_catalog()

    def test_complete_covid_case_is_attached(self) -> None:
        context, receipt = build_case_context(self.catalog, "covid-origins")
        payload = json.loads(context)

        self.assertEqual(receipt["evidence_records"], 40)
        self.assertEqual(receipt["source_records"], 173)
        self.assertEqual(len(payload["case"]["evidence"]), 40)
        self.assertEqual(len(payload["case"]["sources"]), 173)
        self.assertEqual(len(receipt["context_sha256"]), 64)
        self.assertEqual(receipt["context_characters"], len(context))

    def test_system_prompt_has_concrete_default_length_limits(self) -> None:
        self.assertIn("150–250 words", SYSTEM_INSTRUCTIONS)
        self.assertIn("at most four bullets", SYSTEM_INSTRUCTIONS)
        self.assertIn("two to four most relevant records", SYSTEM_INSTRUCTIONS)
        self.assertIn("only when the user explicitly asks", SYSTEM_INSTRUCTIONS)

    def test_complete_eggs_case_is_attached(self) -> None:
        context, receipt = build_case_context(self.catalog, "eggs")
        payload = json.loads(context)

        self.assertEqual(receipt["evidence_records"], 4)
        self.assertEqual(receipt["source_records"], 11)
        self.assertEqual(len(payload["experiments"]), 1)
        self.assertEqual(len(payload["policies"]), 4)

    def test_messages_include_context_history_and_current_page_state(self) -> None:
        messages = build_messages(
            context='{"case":"complete"}',
            question="What changes?",
            history=[
                {"role": "user", "content": "First question"},
                {"role": "assistant", "content": "First answer"},
            ],
            page_state={"run_id": "strict-public-evidence"},
        )

        self.assertEqual([message["role"] for message in messages], ["system", "user", "assistant", "user"])
        self.assertIn('FULL_CASE_CONTEXT_JSON:\n{"case":"complete"}', messages[0]["content"])
        self.assertIn('"run_id":"strict-public-evidence"', messages[-1]["content"])
        self.assertIn("What changes?", messages[-1]["content"])

    def test_history_must_be_complete_alternating_turns(self) -> None:
        with self.assertRaisesRegex(ValueError, "alternate"):
            validate_history([{"role": "assistant", "content": "No prior user"}])
        with self.assertRaisesRegex(ValueError, "end with an assistant"):
            validate_history([{"role": "user", "content": "Unanswered"}])
        with self.assertRaisesRegex(ValueError, "at most"):
            validate_history(
                [
                    {"role": "user" if index % 2 == 0 else "assistant", "content": "x"}
                    for index in range(MAX_HISTORY_MESSAGES + 2)
                ]
            )


if __name__ == "__main__":
    unittest.main()
