from __future__ import annotations

from scripts.phase1_stability_harness import critic_hash_penalty, evaluate_phase1_stability


def _run(
    n: int,
    tier: int,
    critic_hash: str = "abc",
    lab_id: str | None = None,
) -> dict:
    rid = lab_id or f"lab_{n}"
    return {
        "run_number": n,
        "lab_id": rid,
        "overall_weapon_tier": tier,
        "axis_a_tier": tier,
        "axis_b_tier": 4,
        "critic_hash": critic_hash,
        "evidence": {
            "purple_evasion_summary.json": {"path": f"/tmp/{rid}/purple.json", "exists": True}
        },
    }


def test_phase1_pass_requires_all_tier4():
    decision = evaluate_phase1_stability(
        [_run(1, 4, "h1"), _run(2, 4, "h2"), _run(3, 4, "h3")]
    )

    assert decision["pass"] is True
    assert decision["all_tier_4"] is True
    assert decision["tier_spread"] == 0
    assert decision["critic_hash_penalty"]["applies"] is False


def test_phase1_pass_with_same_critic_hash_on_independent_lab_ids():
    """Independent run lab IDs must not trigger §7.4 even when authority critic is unchanged."""
    decision = evaluate_phase1_stability(
        [
            _run(1, 4, "same", "m2_001__phase1_run_01"),
            _run(2, 4, "same", "m2_001__phase1_run_02"),
            _run(3, 4, "same", "m2_001__phase1_run_03"),
        ]
    )

    assert decision["pass"] is True
    assert decision["critic_hash_penalty"]["applies"] is False
    assert decision["critic_hash_penalty"]["scope"] == "same_lab_id_rerun_only"


def test_phase1_fails_on_any_run_below_tier4():
    decision = evaluate_phase1_stability(
        [_run(1, 4, "h1"), _run(2, 3, "h2"), _run(3, 4, "h3")]
    )

    assert decision["pass"] is False
    assert any("below required Tier 4" in r["reason"] for r in decision["falsification_reasons"])


def test_phase1_fails_on_variance_greater_than_one_tier():
    decision = evaluate_phase1_stability(
        [_run(1, 4, "h1"), _run(2, 2, "h2"), _run(3, 4, "h3")]
    )

    assert decision["pass"] is False
    assert decision["tier_spread"] == 2
    assert any("variance 2" in r["reason"] for r in decision["falsification_reasons"])


def test_critic_hash_reuse_on_same_lab_id_flags_rerun_penalization():
    same_lab = "m2_001__phase1_run_01"
    penalty = critic_hash_penalty(
        [
            _run(1, 4, "same", same_lab),
            _run(2, 4, "same", same_lab),
            _run(3, 4, "same", same_lab),
        ]
    )

    assert penalty["applies"] is True
    assert penalty["penalized_lab_ids"] == [same_lab]


def test_command_failed_run_is_not_scored_as_tier3():
    decision = evaluate_phase1_stability(
        [
            {
                "run_number": 1,
                "lab_id": "m2_001__phase1_run_01",
                "status": "COMMAND_FAILED",
                "falsification_reason": "provisioner command failed: smash-all",
            }
        ]
    )

    assert decision["pass"] is False
    assert decision["tiers"] == []
    assert any(
        "could not be scored" in r.get("reason", "")
        or "provisioner" in r.get("reason", "").lower()
        for r in decision["falsification_reasons"]
    )


def test_critic_hash_penalty_blocks_phase1_pass_on_same_lab_rerun():
    same_lab = "m2_001"
    decision = evaluate_phase1_stability(
        [
            _run(1, 4, "same", same_lab),
            _run(2, 4, "same", same_lab),
            _run(3, 4, "same", same_lab),
        ]
    )

    assert decision["pass"] is False
    assert decision["critic_hash_penalty"]["applies"] is True
