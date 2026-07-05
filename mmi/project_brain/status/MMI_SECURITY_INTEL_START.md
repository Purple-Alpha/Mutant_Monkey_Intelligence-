# MMI Security Intel — Lane Start

Date: 2026-06-29  
Authority: Matt (Super)

---

## Decision

Matt chose **A** for both Gemini research briefs:

1. Polymorphic ransomware / adversarial email fraud  
2. SMB threat landscape  

**Meaning:** Activate **MMI Security Intel** as a bounded product lane — not archive-only.

---

## Files created

| File | Role |
|------|------|
| `lanes/RESEARCH_polymorphic_ransomware_delivery_2026-06.md` | Research artifact 1 |
| `lanes/RESEARCH_smb_threat_landscape_2026-06.md` | Research artifact 2 |
| `lanes/MMI_SECURITY_INTEL_LANE.md` | Lane routing |
| `architecture/MMI_SECURITY_INTEL_PRODUCT_SCOPE.md` | Product boundaries |
| `status/MMI_SECURITY_INTEL_START.md` | This record |

---

## Current core MMI pipe (unchanged priority)

**Active:** `mmi-war-room-v1` → Codex (complete before intel MVP spec)

**Queued next:**

| Task id | Owner | Output |
|---------|-------|--------|
| `mmi-security-intel-mvp-architecture` | Claude | `architecture/MMI_SECURITY_INTEL_MVP_ARCHITECTURE.md` |
| `mmi-security-intel-research-verify` | ChatGPT | `lanes/RESEARCH_VERIFICATION_2026-06.md` |

---

## Matt action

None required until war room completes. Then route **Claude** tab with pipeline task for MVP architecture.
