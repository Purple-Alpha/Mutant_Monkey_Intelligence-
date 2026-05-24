# Phase 1.2 — Ransomware Precursor Detection Deep Dive

**Phase reference:** `Fraud_Ransomware_Specialization_Roadmap.md` §1.2.
**Roadmap month:** `12_Month_Specialization_Roadmap.md` Month 3 (August 2026 in calendar terms).
**Status:** First runtime landing complete 2026-05-21. Gate verified by test (see §6).
**Predecessors that must already be in place:** Month 1 attachment schema (`AttachmentClass`, `extracted_text`, `sha256`), Month 1.5 attachment inspector hook, Month 2 fraud-scoring payload (`EmailAnalysisRiskAnalysis` with four new dimensions) + locked `NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT`.

## §0 Purpose

Phase 1.1 made Inbox Shield score *fraud*. Phase 1.2 makes it score *ransomware-precursor signals* — the earliest detectable artefacts of a ransomware attack *before* the payload detonates: malicious attachments, obfuscated URLs, credential-harvesting lures, and MFA-fatigue pushes. The product position is "we stop the attack before it becomes an incident"; Phase 1.2 is the runtime version of that promise on the human-layer side.

Crucially, Phase 1.2 is **deterministic**. The LLM produces fraud scores (Phase 1.1); the precursor block is computed by pure-function detectors in `core/precursor/` and overlaid onto the LLM output. This protects three things at once:

1. The Month 2 fraud-detection gate (`grok-4` 36/40, 100% fraud precision, 0% legit FPR) — the LLM prompt and the fraud-dataset contract are not touched.
2. Audit and reproducibility — every precursor sub-score is traceable to a named rule, not an LLM inference.
3. Cost — no extra LLM tokens are spent on the precursor block.

## §1 Threat Coverage

### §1.1 Malicious attachments

Ransomware initial access in 2022–2026 has been dominated by attachment-borne payloads, in descending order of observed prevalence:

- ISO / IMG / VHD disk images (used to evade mark-of-the-web).
- Macro-enabled Office documents (`.docm`, `.xlsm`, `.xlsb`).
- Encrypted ZIP / 7Z archives with social-engineering filenames.
- Directly-executable filenames (`.exe`, `.scr`, `.lnk`, `.hta`, `.js`, `.vbs`, `.wsh`).
- Double-extension trick filenames (e.g. `invoice.pdf.exe`, `statement.docx.scr`).
- HTML smuggling carriers (`.html`, `.svg` rendering attacker JavaScript locally).

### §1.2 Obfuscated URLs

Phishing URLs evade casual review by:

- Punycode / IDN host names (`xn--paypl-9wa.com`).
- Cyrillic / Greek homoglyph host names (e.g. Cyrillic `а` U+0430 in place of Latin `a`).
- URL shorteners (`bit.ly`, `tinyurl.com`, `t.co`, etc.).
- Credential-bearing URLs (`https://user:password@host/...`).
- Suspicious TLDs (`.zip`, `.mov`, `.tk`, `.top`, `.gq`, `.cf`, `.ml`, `.ga`).
- IP-address hosts (`http://203.0.113.42/login`).
- Phishing-kit login paths (`/login`, `/signin`, `/verify`, `/auth`, `/secure`).

### §1.3 Credential-harvesting lures

Language patterns that push the recipient to "verify your account" or "reset your password" via a link.

### §1.4 MFA-fatigue / verification-code lures

Push-fatigue attacks ("approve the sign-in request") and code-relay attacks ("your verification code is 482910 — enter the code on the next screen").

## §2 Schema Delta

Landed in `core/blackboard/models.py` (also re-exported from `core.blackboard`):

```text
PrecursorIndicator: TypeAlias = Literal[
    "macro_enabled_office_document",
    "executable_attachment",
    "iso_or_disk_image_attachment",
    "double_extension_attachment",
    "encrypted_archive_attachment",
    "html_smuggling_attachment",
    "credential_bearing_url",
    "url_shortener_present",
    "punycode_url_present",
    "homoglyph_url_present",
    "suspicious_tld_present",
    "ip_address_url_present",
    "login_path_url_present",
    "credential_reset_language",
    "account_verification_language",
    "mfa_push_language",
    "verification_code_language",
]

class EmailAnalysisRansomwarePrecursorAnalysis(StrictModel):
    attachment_risk_score: int = Field(ge=0, le=100)
    url_obfuscation_score: int = Field(ge=0, le=100)
    credential_harvesting_score: int = Field(ge=0, le=100)
    mfa_fatigue_score: int = Field(ge=0, le=100)
    precursor_indicators: list[PrecursorIndicator] = Field(default_factory=list)

class EmailAnalysisPayload(StrictModel):
    ...
    ransomware_precursor_analysis: EmailAnalysisRansomwarePrecursorAnalysis | None = None
```

Same schema-versioning discipline as `AttachmentClass` and `BehavioralDeviationFlag`: detectors cannot invent freeform indicators, and adding a new indicator requires a deliberate schema change with test pinning (see `test_precursor_indicator_literal_exact_set`).

The new `ransomware_precursor_analysis` field is **optional** so Month 1 / Month 2 fixtures that constructed `EmailAnalysisPayload` directly without precursor data still validate. Production paths always overlay a non-`None` block (zero sub-scores when there is no signal).

## §3 Detector Architecture

All detectors live under `core/precursor/`:

| Module | Detector | Public surface |
|---|---|---|
| `attachment_classifier.py` | Per-attachment static classifier + risk scorer | `attachment_inspector` (plugs into Month 1.5 ingest hook), `classify_attachment`, `score_attachment_risk`, `AttachmentRiskAssessment` |
| `url_obfuscation_detector.py` | URL parser + obfuscation scorer | `extract_urls`, `score_url_obfuscation`, `UrlRiskAssessment` |
| `body_signal_detector.py` | Credential-harvest + MFA-fatigue body-language scorer | `score_credential_harvesting`, `score_mfa_fatigue`, `BodySignalAssessment` |
| `analysis.py` | Overlay builder that combines all three into the block | `build_precursor_overlay`, `PrecursorOverlay` |

### §3.1 Hard Safety Boundary

Per the 12-month roadmap Month 3 risk/dependency note:

> Attachment inspection has to stay sandbox-safe — under no circumstances does the inspector execute attachment content. Static analysis only.

This is enforced architecturally:

- The detectors take `bytes | None` plus metadata and return scores; they never call `subprocess`, `exec`, `eval`, or any file-format renderer that could execute attacker-controlled code.
- The URL detector never resolves DNS, never fetches the URL.
- The body-language detector never executes regex with untrusted patterns; the phrase lists are constants compiled into the module.

### §3.2 Sub-Score Bands

| Detector | Score band → meaning |
|---|---|
| attachment | 0–20 routine, 21–50 container/archive without explicit malicious indicator, 51–80 macro-enabled Office / encrypted-archive social-engineering / HTML smuggling, 81–100 directly executable / disk image / double-extension |
| URL | 0 no URLs, 30–50 shortener / suspicious TLD / login path, 60–75 IP host / punycode / homoglyph, 80–100 credential-bearing URL |
| credential harvest | 0 no signal, 60+ verify-account language, 70+ reset-your-password / unusual-sign-in language |
| MFA fatigue | 0 no signal, 55+ verification-code lure, 65+ push-approval language, 75+ verification-code with explicit numeric OTP pattern |

Per-email aggregation: each sub-score is the **max** across the email's contributing signals (so the worst URL drives the URL score, not the count). `precursor_indicators` is the deduplicated, source-order-stable union of indicators that fired.

## §4 Scoring-Agent Overlay

`run_email_risk_scoring_cycle` (`core/scoring/email_risk_scoring_agent.py`) gains an overlay step:

1. LLM call as before → JSON → `EmailAnalysisPayload.model_validate(...)`.
2. **(new)** `overlay = build_precursor_overlay(inbound_payload)`.
3. **(new)** `final_risk = max(llm_risk, overlay.recommended_risk_floor)`.
4. **(new)** `analysis_payload = analysis_payload.model_copy(update={"risk_analysis": ..., "ransomware_precursor_analysis": overlay.block})`.
5. `submit_email_analysis(...)` as before.

The floor is **one-directional**: precursor scores can only LIFT `risk_score`, never lower it. A confident LLM that rates a fraud case at 95 stays at 95 even when the precursor floor would be 0 (test: `test_scoring_agent_overlay_does_not_lower_high_llm_risk_score`).

Opt-out: `EmailRiskScoringConfig.enable_ransomware_precursor_overlay: bool = True`. The Month 2 fraud-eval harness can pass `False` to evaluate bare LLM output without the deterministic floor (test: `test_scoring_agent_overlay_can_be_disabled_for_pure_llm_baseline`).

## §5 Out of Scope (Deferred to Later Months / Years)

These are intentionally **not** in Phase 1.2 scope:

- Sandbox detonation of attachments (executing files to observe behavior). Phase 1.2 is static only.
- DNS / threat-intel lookups on extracted URLs (would require external network calls and an allowlist policy).
- Deep PDF / Office text extraction (`extracted_text` population). Foundations are in the schema but no Phase 1.2 detector populates `extracted_text` — that requires format-aware parsing libraries and a sandbox decision (Month 4+).
- Adversarial generation of Red-side ransomware-precursor cases. Sandbox training pit is Month 4 (Phase 1.3).
- Tenant-memory model for "this attachment hash has been seen before, this URL has been seen before". No memory in Phase 1.2.
- Mutation-engine specialization for `attachment_classifier_boost` / `url_obfuscation_sensitivity`. Month 5 (Phase 1.4).
- Outbound email scanning. Year 2+.

## §6 Gate Verification

Roadmap gate from `12_Month_Specialization_Roadmap.md` Month 3:

> A synthetic ransomware-precursor email (malicious attachment + obfuscated URL + credential lure) scored ≥85 risk_score with all four precursor sub-scores populated, on a deterministic LLM client run reproducing across CI.

Gate test: `tests/test_ransomware_precursor.py::test_scoring_agent_month_3_gate_synthetic_ransomware_precursor_email`.

Test fixture: synthetic email with sender `security@identity.example`, subject `"Unusual sign-in activity — reset your password"`, body containing `"We detected unusual sign-in activity ... reset your password at https://xn--paypl-9wa.com/login ..."`, two attachments (`secure_account.iso` and `instructions.pdf.exe`). The LLM is intentionally under-scored at `risk_score=20` to prove the deterministic overlay lifts the final score to ≥ 85.

Assertions:

- `parsed.risk_analysis.risk_score >= 85`
- `parsed.ransomware_precursor_analysis is not None`
- `attachment_risk_score > 0`, `url_obfuscation_score > 0`, `credential_harvesting_score > 0` (the three signal axes the synthetic email exercises)
- Indicators include at least one of `iso_or_disk_image_attachment` / `executable_attachment` / `double_extension_attachment`
- Indicators include at least one of `punycode_url_present` / `login_path_url_present`
- Indicators include `credential_reset_language`

Verification:

```text
python -m pytest tests/test_ransomware_precursor.py -v
27 passed in 0.15s
exit code 0

python -m pytest tests -q
359 passed in 6.22s
exit code 0
```

**Gate verdict:** PASS (deterministic, CI-reproducible).

## §7 Month 3 Implementation Contract

This section is the receipt for the Month 3 work. Everything below is landed.

### §7.1 Files Changed

| Path | Change |
|---|---|
| `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/blackboard/models.py` | Added `PrecursorIndicator` Literal (17 values) + `EmailAnalysisRansomwarePrecursorAnalysis` model + optional field on `EmailAnalysisPayload` |
| `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/blackboard/__init__.py` | Re-exported new symbols |
| `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/precursor/__init__.py` | Module bootstrap + re-exports |
| `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/precursor/attachment_classifier.py` | Sandbox-safe classifier + `AttachmentInspector` implementation + risk scorer |
| `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/precursor/url_obfuscation_detector.py` | URL parser + obfuscation scorer |
| `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/precursor/body_signal_detector.py` | Credential-harvest + MFA-fatigue scorer |
| `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/precursor/analysis.py` | Overlay builder |
| `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/scoring/email_risk_scoring_agent.py` | Wired overlay into `run_email_risk_scoring_cycle`; new opt-out config flag |
| `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/tests/test_ransomware_precursor.py` | 27 new tests (schema, classifier, URL, body, overlay, agent integration, **gate**, FPR-protection, opt-out) |
| `4. Product_Roadmap/Phase_1_2_Ransomware_Precursor_Deep_Dive.md` | This doc |
| `4. Product_Roadmap/Q1_Checkpoint_2026.md` | Q1 checkpoint document (Months 1–3 closeout) |
| `4. Product_Roadmap/Month_2_Closeout_Readiness.md` | Month 2 gate-PASS closeout |
| `MASTER_INDEX.md` | New files indexed |
| `PROJECT_HANDSHAKE.md`, `PROJECT_ACTIVITY_LOG.md` | Item 159 + 2026-05-21 entry |

### §7.2 Test Counts

- Pre-Month-3 baseline: 332 tests passing.
- Post-Month-3: **359 tests passing** (+27 net).
- Gate test included in the +27.

### §7.3 What Phase 1.2 Does NOT Promise

- Phase 1.2 is **not** a tenant-data-trained classifier. There is no learned model, no tenant memory, no historical attachment-hash check.
- Phase 1.2 does **not** scan attachment binary content. It looks at filename, content type, size, and the metadata the connector / inspector chain already populated.
- Phase 1.2 does **not** introduce a separate Ransomware Defense product surface. That is Phase 2.2 (Month 6).
- Phase 1.2 does **not** re-evaluate the Month 2 fraud-detection gate. The LLM prompt and dataset are untouched.

## §8 Cross-References

- `4. Product_Roadmap/Fraud_Ransomware_Specialization_Roadmap.md` §1.2 — strategic intent.
- `4. Product_Roadmap/12_Month_Specialization_Roadmap.md` Month 3 — operational gate.
- `4. Product_Roadmap/Phase_1_1_Fraud_Prevention_Deep_Dive.md` §5 — the Phase 1.2 surface was listed as out-of-scope for Month 2, now landed.
- `4. Product_Roadmap/Q1_Checkpoint_2026.md` — Months 1–3 retrospective.
- `4. Product_Roadmap/Month_1_Closeout_Readiness.md` / `Month_2_Closeout_Readiness.md` — prior monthly closeouts.
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/precursor/` — runtime modules.
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/tests/test_ransomware_precursor.py` — gate test + 26 detector tests.

## Last Updated

2026-05-21
