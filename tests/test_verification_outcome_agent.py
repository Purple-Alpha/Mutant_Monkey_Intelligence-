from __future__ import annotations

import json
import unittest

from ops.verification_outcome_agent import (
    VerificationOutcomeAgent,
)


class VerificationOutcomeAgentTest(unittest.TestCase):
    def test_verify_pass_records_signed_unbuilt_state(self) -> None:
        agent = VerificationOutcomeAgent()

        outcome = agent.verify_pass(
            lane="Cursor -> Codex pre-build -> Cursor build",
            scoreboard_commit="6ef6211",
            evidence=["scoreboard reconcile"],
        )

        self.assertEqual(outcome.task_id, "#48")
        self.assertEqual(outcome.outcome, "PASS")
        self.assertEqual(outcome.lifecycle, "SIGNED_UNBUILT")
        self.assertEqual(outcome.status, "done")
        self.assertEqual(outcome.gate_label, "PASS")
        self.assertEqual(outcome.drift_blocks, 0)
        self.assertEqual(outcome.scoreboard_commit, "6ef6211")
        self.assertEqual(outcome.to_dict()["evidence"], ["scoreboard reconcile"])

    def test_pass_with_drift_is_not_done(self) -> None:
        agent = VerificationOutcomeAgent()

        outcome = agent.verify_pass(
            lane="Cursor -> Codex pre-build -> Cursor build",
            drift_blocks=1,
        )

        self.assertEqual(outcome.outcome, "DRIFT")
        self.assertEqual(outcome.status, "error")
        self.assertEqual(outcome.gate_label, "DRIFT")

    def test_blocked_outcome_maps_to_blocked_status(self) -> None:
        agent = VerificationOutcomeAgent()

        outcome = agent.verify(
            outcome="BLOCKED",
            lifecycle="SIGNED_UNBUILT",
            lane="Cursor -> Codex pre-build -> Cursor build",
            summary="Waiting on external gate.",
        )

        self.assertEqual(outcome.status, "blocked")
        self.assertEqual(outcome.gate_label, "BLOCKED")

    def test_invalid_lifecycle_is_rejected(self) -> None:
        agent = VerificationOutcomeAgent()

        with self.assertRaisesRegex(ValueError, "Unsupported lifecycle"):
            agent.verify(
                outcome="PASS",
                lifecycle="UNTRACKED",
                lane="Cursor -> Codex pre-build -> Cursor build",
            )

    def test_run_returns_queue_compatible_payload(self) -> None:
        agent = VerificationOutcomeAgent()

        result = agent.run("Build Verification Outcome (#48)", ["BUILD_QUEUE.json"])

        self.assertEqual(result["agent"], "VerificationOutcomeAgent")
        self.assertEqual(result["status"], "done")
        self.assertEqual(result["files"], [])
        self.assertEqual(result["outcome"]["task_id"], "#48")
        self.assertEqual(result["outcome"]["scoreboard_commit"], "6ef6211")
        self.assertEqual(result["outcome"]["lifecycle"], "SIGNED_UNBUILT")
        json.dumps(result)


if __name__ == "__main__":
    unittest.main()
