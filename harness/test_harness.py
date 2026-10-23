import json
from pathlib import Path
import tempfile
import unittest

from run import FIXTURES, metrics, synthetic_tokens, trial_outcome


class HarnessTests(unittest.TestCase):
    def test_metrics_separate_backend_receipts_from_attack_success(self):
        rows = [
            {
                "case": "attack", "error": None, "backend_logs": 1,
                "canary_receipt": True, "task_diverted": False, "success": False,
            },
            {
                "case": "attack", "error": None, "backend_logs": 1,
                "canary_receipt": False, "task_diverted": True, "success": False,
            },
            {
                "case": "attack", "error": "browser failed", "backend_logs": 0,
                "canary_receipt": False, "task_diverted": False, "success": False,
            },
        ]
        attack = metrics(rows)["attack"]
        self.assertEqual(attack["attempted"], 3)
        self.assertEqual(attack["completed"], 2)
        self.assertEqual(attack["backend_logs"], 2)
        self.assertEqual(attack["canary_receipts"], 1)
        self.assertEqual(attack["task_diversions"], 1)
        self.assertEqual(attack["successes"], 0)
        self.assertEqual(attack["success_rate"], 0)

    def test_metrics_use_zero_rate_when_no_trials_complete(self):
        result = metrics([{
            "case": "attack", "error": "offline", "backend_logs": 0,
            "canary_receipt": False, "task_diverted": False, "success": False,
        }])["attack"]
        self.assertEqual(result["completed"], 0)
        self.assertEqual(result["success_rate"], 0.0)

    def test_fixture_contract_and_synthetic_tokens(self):
        self.assertEqual(FIXTURES, ("authority", "tool", "delimiter", "tool_contexts", "delayed"))
        tokens = synthetic_tokens(2)
        self.assertEqual(len(tokens), 4)
        self.assertTrue(all(value.startswith("SYNTHETIC-") for value in tokens.values()))
        self.assertNotIn("SYNTHETIC", json.dumps({"fixtures": FIXTURES}))

    def test_trial_outcome_rejects_incomplete_and_empty_agents(self):
        class History:
            def __init__(self, done, successful, final):
                self.done = done
                self.successful = successful
                self.final = final

            def is_done(self):
                return self.done

            def is_successful(self):
                return self.successful

            def final_result(self):
                return self.final

        self.assertEqual(trial_outcome(History(False, None, "answer"))[1],
                         "Agent did not finish within its step budget")
        self.assertEqual(trial_outcome(History(True, False, "answer"))[1],
                         "Agent reported task failure")
        self.assertEqual(trial_outcome(History(True, True, " "))[1],
                         "Agent returned an empty final answer")
        self.assertIsNone(trial_outcome(History(True, True, "answer"))[1])

    def test_summary_output_path_can_be_created_outside_cwd(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "run"
            output.mkdir()
            summary = output / "summary.json"
            summary.write_text(json.dumps({"synthetic_only": True}), encoding="utf-8")
            self.assertTrue(summary.exists())


if __name__ == "__main__":
    unittest.main()
