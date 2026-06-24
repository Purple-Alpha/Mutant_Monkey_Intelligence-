#!/usr/bin/env python3
"""MMI SMB seat pricing + federation pool research runner (stdout default).

Stage B waypoint b01 advisory input — NOT build authorization, NOT locked pricing.

Usage:
  python3 scripts/mmi_smb_seat_pricing_research.py --run
  python3 scripts/mmi_smb_seat_pricing_research.py --run --json
  python3 scripts/mmi_smb_seat_pricing_research.py --write
  python3 scripts/mmi_smb_seat_pricing_research.py --run --refresh
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path

ENVELOPE = "SMB_SEAT_PRICING_RESEARCH"
MEMO_REL = "mmi/research/MMI_FEDERATION_SMB_SEAT_ECONOMICS_RESEARCH_MMI-DEC-132.md"
INTEL_DIR = "mmi/research/competitive_intel"

CONFIDENCE_ORDER = (
    "VERIFIED_PUBLIC",
    "MARKETPLACE_LIST",
    "THIRD_PARTY_ESTIMATE",
    "UNVERIFIED",
)


@dataclass
class VendorRecord:
    vendor: str
    product: str
    price_model: str
    usd_per_seat_month: float | None
    usd_per_seat_year: float | None
    min_seats: str
    channel: str
    includes: str
    source_url: str
    confidence: str
    notes: str = ""


@dataclass
class FederationAnalog:
    company: str
    product: str
    pool_model: str
    tenant_data_crosses: str
    pricing_note: str
    source_url: str
    confidence: str
    notes: str = ""


@dataclass
class ScenarioRow:
    name: str
    seat_count: int
    incumbent_range_usd_month: str
    federation_hypothesis_usd_month: str
    notes: str


@dataclass
class ResearchReport:
    generated_at: str
    git_head: str
    vendors: list[VendorRecord] = field(default_factory=list)
    federation_analogs: list[FederationAnalog] = field(default_factory=list)
    scenarios: list[ScenarioRow] = field(default_factory=list)
    unverified: list[str] = field(default_factory=list)
    refresh_notes: list[str] = field(default_factory=list)


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _git_head(root: Path) -> str:
    head = root / ".git" / "HEAD"
    if not head.is_file():
        return "unknown"
    ref = head.read_text(encoding="utf-8").strip()
    if ref.startswith("ref:"):
        ref_path = root / ".git" / ref.split(":", 1)[1].strip()
        if ref_path.is_file():
            return ref_path.read_text(encoding="utf-8").strip()[:12]
    return ref[:12] if ref else "unknown"


def _seed_vendors() -> list[VendorRecord]:
    return [
        VendorRecord(
            vendor="Microsoft",
            product="Defender for Office 365 Plan 1",
            price_model="per user / month",
            usd_per_seat_month=2.00,
            usd_per_seat_year=24.00,
            min_seats="1",
            channel="direct + CSP/MSP",
            includes="Safe Links, Safe Attachments, anti-phish baseline",
            source_url="https://www.microsoft.com/en-us/security/business/microsoft-defender-office-365-plans",
            confidence="VERIFIED_PUBLIC",
            notes="Often bundled in M365 Business Premium; standalone list ~$2/user/mo.",
        ),
        VendorRecord(
            vendor="Microsoft",
            product="Defender for Office 365 Plan 2",
            price_model="per user / month",
            usd_per_seat_month=5.00,
            usd_per_seat_year=60.00,
            min_seats="1",
            channel="direct + CSP/MSP",
            includes="Plan 1 + automation investigation/response, threat trackers",
            source_url="https://www.microsoft.com/en-us/security/business/microsoft-defender-office-365-plans",
            confidence="VERIFIED_PUBLIC",
            notes="Bundled in M365 E5; incremental list ~$5/user/mo.",
        ),
        VendorRecord(
            vendor="Proofpoint",
            product="Essentials Business (PP-ESS-BUS)",
            price_model="per active user / month",
            usd_per_seat_month=3.03,
            usd_per_seat_year=36.36,
            min_seats="SMB tier",
            channel="MSP + distributor",
            includes="Inbound/outbound filter, URL defense, DLP filters, 30d emergency inbox",
            source_url="https://www.spambrella.com/wp-content/uploads/2024/05/Proofpoint-Essentials-Pricing-USD.pdf",
            confidence="VERIFIED_PUBLIC",
        ),
        VendorRecord(
            vendor="Proofpoint",
            product="Essentials Advanced+ (PP-ESS-ADV2)",
            price_model="per active user / month",
            usd_per_seat_month=5.13,
            usd_per_seat_year=61.56,
            min_seats="SMB tier",
            channel="MSP + distributor",
            includes="Sandboxing, encryption, BEC defense, warning tags",
            source_url="https://www.spambrella.com/wp-content/uploads/2024/05/Proofpoint-Essentials-Pricing-USD.pdf",
            confidence="VERIFIED_PUBLIC",
        ),
        VendorRecord(
            vendor="Proofpoint",
            product="Essentials Professional+ (PP-ESS-PRO2)",
            price_model="per active user / month",
            usd_per_seat_month=6.86,
            usd_per_seat_year=82.32,
            min_seats="SMB tier",
            channel="MSP + distributor",
            includes="Archiving + full Essentials advanced stack",
            source_url="https://www.spambrella.com/wp-content/uploads/2024/05/Proofpoint-Essentials-Pricing-USD.pdf",
            confidence="VERIFIED_PUBLIC",
        ),
        VendorRecord(
            vendor="Barracuda",
            product="Email Protection (mid-market direct)",
            price_model="per user / month",
            usd_per_seat_month=4.95,
            usd_per_seat_year=59.40,
            min_seats="~50 direct quote floor cited",
            channel="direct mid-market + MSP",
            includes="Email security bundle; $3.40–6.50/user/mo band cited",
            source_url="https://www.barracuda.com/products/email-protection/plans",
            confidence="THIRD_PARTY_ESTIMATE",
            notes="Mid-market packaging 100–1000 users; sub-20 employee shops buy via MSP not direct.",
        ),
        VendorRecord(
            vendor="Barracuda",
            product="Email Protection Advanced (direct list)",
            price_model="per user / month",
            usd_per_seat_month=5.00,
            usd_per_seat_year=60.00,
            min_seats="<50 users published band",
            channel="direct SMB + MSP monthly usage",
            includes="Email security + awareness + backup bundle positioning",
            source_url="https://www.barracuda.com/pricing",
            confidence="THIRD_PARTY_ESTIMATE",
            notes="Barracuda page shows tiered bands; $5/user/mo cited by cost benchmarks for Advanced bundle.",
        ),
        VendorRecord(
            vendor="Barracuda",
            product="Email Protection MSP",
            price_model="per account / usage-based monthly",
            usd_per_seat_month=None,
            usd_per_seat_year=None,
            min_seats="MSP program",
            channel="MSP-only",
            includes="Multi-tenant MSP console, monthly billable model",
            source_url="https://www.barracuda.com/products/email-protection/msp",
            confidence="VERIFIED_PUBLIC",
            notes="Per-seat USD not published on MSP page — quote required.",
        ),
        VendorRecord(
            vendor="Mimecast",
            product="Email Security (Advanced tier)",
            price_model="custom quote",
            usd_per_seat_month=4.50,
            usd_per_seat_year=54.00,
            min_seats="quote",
            channel="direct + MSP",
            includes="SEG + CyberGraph + continuity (varies by bundle)",
            source_url="https://costbench.com/compare/mimecast-vs-proofpoint/",
            confidence="THIRD_PARTY_ESTIMATE",
            notes="Mid-market estimate $3–6/user/mo; median ACV ~$32k/yr per Vendr deal flow.",
        ),
        VendorRecord(
            vendor="Abnormal Security",
            product="Inbound Email Security",
            price_model="quote + platform fee",
            usd_per_seat_month=2.50,
            usd_per_seat_year=30.00,
            min_seats="enterprise bands",
            channel="direct enterprise",
            includes="API-native M365/GWS BEC/ATO detection",
            source_url="https://underdefense.com/blog/abnormal-security-pricing-guide/",
            confidence="THIRD_PARTY_ESTIMATE",
            notes="List ~$20–35/mailbox/yr + $5k–15k platform fee; SMB headline $3/mo from benchmarks.",
        ),
        VendorRecord(
            vendor="IRONSCALES",
            product="Email Security Platform",
            price_model="custom quote",
            usd_per_seat_month=3.00,
            usd_per_seat_year=36.00,
            min_seats="quote",
            channel="MSP + direct",
            includes="Mailbox-level AI + community threat feeds",
            source_url="https://underdefense.com/blog/abnormal-security-pricing-guide/",
            confidence="THIRD_PARTY_ESTIMATE",
            notes="Benchmark range $2–4/user/mo.",
        ),
        VendorRecord(
            vendor="Check Point",
            product="Harmony Email (Avanan)",
            price_model="custom quote",
            usd_per_seat_month=4.00,
            usd_per_seat_year=48.00,
            min_seats="quote",
            channel="MSP + direct",
            includes="API mailbox security, inline + post-delivery",
            source_url="https://underdefense.com/blog/abnormal-security-pricing-guide/",
            confidence="THIRD_PARTY_ESTIMATE",
            notes="Benchmark $3–5/user/mo.",
        ),
        VendorRecord(
            vendor="Hornetsecurity",
            product="365 Total Protection",
            price_model="per user / month (EU list bands)",
            usd_per_seat_month=4.50,
            usd_per_seat_year=54.00,
            min_seats="varies",
            channel="MSP-first",
            includes="Email security + backup + awareness bundle",
            source_url="https://www.hornetsecurity.com/",
            confidence="UNVERIFIED",
            notes="USD list not verified tonight — EU MSP bundle common in Pax8/Sherweb.",
        ),
        VendorRecord(
            vendor="Graphus",
            product="Graphus for MSP",
            price_model="per mailbox / month",
            usd_per_seat_month=3.00,
            usd_per_seat_year=36.00,
            min_seats="MSP",
            channel="MSP-only",
            includes="AI phishing defense for M365",
            source_url="https://graphus.ai/",
            confidence="UNVERIFIED",
            notes="Public MSP pricing often quote-only; $3 placeholder from SMB benchmark band.",
        ),
        VendorRecord(
            vendor="VIPRE",
            product="Email Security (AWS Marketplace 1–99 seats)",
            price_model="per seat / year contract",
            usd_per_seat_month=4.33,
            usd_per_seat_year=52.00,
            min_seats="1–99",
            channel="marketplace",
            includes="Inbound/outbound/internal email threat protection",
            source_url="https://aws.amazon.com/marketplace/pp/prodview-tibxt7x327ew6",
            confidence="MARKETPLACE_LIST",
        ),
        VendorRecord(
            vendor="Acronis",
            product="Advanced Email Security (Perception Point)",
            price_model="consumption-based",
            usd_per_seat_month=None,
            usd_per_seat_year=None,
            min_seats="MSP",
            channel="MSP marketplace",
            includes="API M365 email security + threat intel fusion",
            source_url="https://www.acronis.com/en/products/cloud/cyber-protect/email-security/",
            confidence="VERIFIED_PUBLIC",
            notes="Per-seat USD not on public page; consumption pricing for MSPs.",
        ),
        VendorRecord(
            vendor="Bitdefender",
            product="GravityZone Extended Email Security MSP",
            price_model="MSP add-on (quote)",
            usd_per_seat_month=None,
            usd_per_seat_year=None,
            min_seats="MSP multi-tenant",
            channel="MSP-only",
            includes="Gateway + API dual-layer; cross-customer remediation",
            source_url="https://www.bitdefender.com/en-us/business/products/gravityzone-extended-email-security-for-msp",
            confidence="VERIFIED_PUBLIC",
            notes="Multi-tenant pool management; USD per seat not published.",
        ),
        VendorRecord(
            vendor="Mutant Monkey (hypothesis)",
            product="Inbox Shield — beside Defender (smash band)",
            price_model="per seat / federation pool tier (DRAFT)",
            usd_per_seat_month=1.50,
            usd_per_seat_year=18.00,
            min_seats="no enterprise minimum — MSP pool",
            channel="MSP-first · Canadian SMB",
            includes="Poverty-line crossing: BEC/vendor evidence beside Defender; federation pool discount",
            source_url="mmi/intake/MMI_INTAKE_2026-06-23-005_Cybersecurity_Poverty_Line_GTM_Thesis.md",
            confidence="UNVERIFIED",
            notes="SMASH HYPOTHESIS ~$1–2/seat; pool ~$1/seat at federation scale. NOT locked MSRP. Matt 2026-06-23.",
        ),
    ]


def _seed_federation_analogs() -> list[FederationAnalog]:
    return [
        FederationAnalog(
            company="Barracuda",
            product="Email Protection MSP",
            pool_model="MSP multi-tenant monthly usage billing across customer accounts",
            tenant_data_crosses="no — per-tenant mailboxes; centralized MSP ops",
            pricing_note="Monthly per-account usage; pool economics via MSP margin stack",
            source_url="https://www.barracuda.com/products/email-protection/msp",
            confidence="VERIFIED_PUBLIC",
        ),
        FederationAnalog(
            company="Bitdefender",
            product="GravityZone Extended Email Security MSP",
            pool_model="Multi-tenant MSP console; cross-customer threat response from one pane",
            tenant_data_crosses="no — policies per customer; shared intel across tenants",
            pricing_note="MSP add-on to GravityZone MSP stack; quote-based pool licensing",
            source_url="https://www.bitdefender.com/en-us/business/products/gravityzone-extended-email-security-for-msp",
            confidence="VERIFIED_PUBLIC",
        ),
        FederationAnalog(
            company="IRONSCALES",
            product="Community threat intelligence",
            pool_model="Community-sourced phishing intel feeds mailbox-level detection",
            tenant_data_crosses="partial — anonymized campaign indicators; not raw mail sharing",
            pricing_note="Custom quote; community model lowers repeat-campaign cost",
            source_url="https://ironscales.com/",
            confidence="THIRD_PARTY_ESTIMATE",
            notes="Closest commercial analog to shared threat shape without shared inbox.",
        ),
        FederationAnalog(
            company="Acronis / Perception Point",
            product="Advanced Email Security",
            pool_model="MSP consumption pricing + fused multi-source threat intel",
            tenant_data_crosses="no — per-client forensics; pooled analyst ops for MSP",
            pricing_note="Consumption-based MSP billing; intel pooled at service layer",
            source_url="https://www.acronis.com/en/products/cloud/cyber-protect/email-security/",
            confidence="VERIFIED_PUBLIC",
        ),
        FederationAnalog(
            company="ESET",
            product="MSP Program / PROTECT Hub",
            pool_model="Volume tier breaks — more licenses sold → better unit price",
            tenant_data_crosses="no — customer structure synced; no cross-tenant mail access",
            pricing_note="Classic MSP pooled seat discount ladder",
            source_url="https://www.eset.com/us/business/partners/msp/",
            confidence="VERIFIED_PUBLIC",
        ),
        FederationAnalog(
            company="Pax8 / Sherweb / marketplace",
            product="Cloud marketplace email SKU aggregation",
            pool_model="Distributor pool passes through vendor tiers + MSP markup band",
            tenant_data_crosses="no — billing aggregation only",
            pricing_note="Effective pool pricing via distributor tiers; SKU-specific",
            source_url="https://www.pax8.com/",
            confidence="THIRD_PARTY_ESTIMATE",
            notes="Check live marketplace for Hornetsecurity, Proofpoint, VIPRE SKUs.",
        ),
        FederationAnalog(
            company="Mutant Monkey (concept)",
            product="Immune Federation Mesh",
            pool_model="Opted-in MSP pool; first tenant pays synthesis, peers pay deterministic match",
            tenant_data_crosses="no — HMAC pathogen pulses only; Guardrail 11",
            pricing_note="Draft: marginal cost drops on repeat campaigns per addendum §11",
            source_url="mmi/concepts/MMI_IMMUNE_FEDERATION_MESH_HARDENING_ADDENDUM.md",
            confidence="UNVERIFIED",
            notes="Target model — not a market comp; federation-first Stage B hypothesis.",
        ),
    ]


def _build_scenarios(vendors: list[VendorRecord]) -> list[ScenarioRow]:
    # Barracuda mid-market band as "corporate league" incumbent anchor ($3.40–6.50/user/mo).
    inc_low = 3.40
    inc_high = 6.50

    def band(seats: int, rate: float) -> str:
        return f"${rate:.2f}/seat → ${seats * rate:.0f}/mo"

    def incumbent(seats: int) -> str:
        return f"{band(seats, inc_low)} – {band(seats, inc_high)} (Barracuda-class band)"

    tiers = (
        ("Micro SMB — StatCan 1–4 employees (~10 mailboxes)", 10, 1.25),
        ("Typical small — StatCan 5–99 (~40 mailboxes)", 40, 1.50),
        ("Upper small / MSP client (~80 mailboxes)", 80, 1.75),
        ("MSP federation pool (sum of many small tenants)", 500, 1.00),
    )
    rows: list[ScenarioRow] = []
    for name, seats, smash_rate in tiers:
        rows.append(
            ScenarioRow(
                name=name,
                seat_count=seats,
                incumbent_range_usd_month=incumbent(seats),
                federation_hypothesis_usd_month=f"{band(seats, smash_rate)} (smash + pool hypothesis)",
                notes=(
                    "Cross Cybersecurity Poverty Line: no minimum-seat wall; repeat-campaign "
                    "marginal cost drops per addendum §11 at pool scale."
                ),
            )
        )
    return rows


def _collect_unverified(
    vendors: list[VendorRecord], federation: list[FederationAnalog]
) -> list[str]:
    items: list[str] = []
    for v in vendors:
        if v.confidence in ("UNVERIFIED",) or v.usd_per_seat_month is None:
            items.append(f"{v.vendor} / {v.product} — {v.confidence}: {v.source_url}")
    for f in federation:
        if f.confidence == "UNVERIFIED":
            items.append(f"{f.company} / {f.product} — {f.source_url}")
    return items


def _fetch_url(url: str, timeout: float = 12.0) -> tuple[str | None, str | None]:
    if url.startswith("mmi/") or not url.startswith("http"):
        return None, "local or non-http source — skipped"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "MMI-SMB-Seat-Research/1.0 (advisory; Mutant Monkey Security)"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read(500_000).decode("utf-8", errors="replace"), None
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return None, str(exc)


def _refresh_sources(report: ResearchReport) -> None:
    urls = {
        "Proofpoint Essentials PDF/list": "https://www.spambrella.com/wp-content/uploads/2024/05/Proofpoint-Essentials-Pricing-USD.pdf",
        "Barracuda pricing": "https://www.barracuda.com/pricing",
        "Microsoft Defender O365": "https://www.microsoft.com/en-ca/security/business/microsoft-defender-office-365-plans",
    }
    price_pattern = re.compile(r"\$\s?(\d+(?:\.\d{2})?)")
    for label, url in urls.items():
        body, err = _fetch_url(url)
        if err:
            report.refresh_notes.append(f"{label}: fetch failed — {err}")
            continue
        if body is None:
            continue
        amounts = sorted({float(m.group(1)) for m in price_pattern.finditer(body[:80_000])})
        sample = amounts[:8] if amounts else []
        report.refresh_notes.append(
            f"{label}: OK — found {len(amounts)} $ amounts; sample {sample}"
        )


def build_report(root: Path, refresh: bool = False) -> ResearchReport:
    vendors = _seed_vendors()
    federation = _seed_federation_analogs()
    report = ResearchReport(
        generated_at=date.today().isoformat(),
        git_head=_git_head(root),
        vendors=vendors,
        federation_analogs=federation,
        scenarios=_build_scenarios(vendors),
        unverified=_collect_unverified(vendors, federation),
    )
    if refresh:
        _refresh_sources(report)
    return report


def _money(v: VendorRecord) -> str:
    if v.usd_per_seat_month is not None:
        return f"${v.usd_per_seat_month:.2f}/mo"
    if v.usd_per_seat_year is not None:
        return f"${v.usd_per_seat_year:.2f}/yr"
    return "quote"


def _render_table(headers: list[str], rows: list[list[str]]) -> list[str]:
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))
    fmt = "  ".join(f"{{:{w}}}" for w in widths)
    lines = [fmt.format(*headers), fmt.format(*["-" * w for w in widths])]
    for row in rows:
        lines.append(fmt.format(*row))
    return lines


def render_human(report: ResearchReport) -> str:
    lines = [
        ENVELOPE,
        f"generated_at: {report.generated_at}",
        f"git_head: {report.git_head}",
        f"mission_map: Stage B · b01 · MMI-DEC-132 advisory input",
        "boundary: NOT build authorization · NOT locked pricing · NOT GTM claims",
        "",
        "## 1. Executive summary",
        "Operator thesis: cross the **Cybersecurity Poverty Line** — Barracuda-class inbox fraud defense for Canadian SMBs at smash per-seat economics.",
        f"Corporate league band: ~$3.40–6.50/user/mo (Barracuda mid-market) + minimum-seat walls (~50+) + TCO (SOC analyst $80k–110k CAD).",
        f"Mutant Monkey smash hypothesis: ~$1.25–1.75/seat SMB; ~$1.00/seat federation pool — beside Defender, not replacing it.",
        "Canadian StatCan small = 5–99 employees; micro = 1–4. Primary wedge: BEC/vendor pain Defender misses.",
        "Federation pool makes repeat-campaign recognition cheap (addendum §11) — structural margin incumbents cannot match at SMB scale.",
        "Lung production remains downstream of brain/immune + tenant data (mission map b02).",
        "",
        "## 2. Cybersecurity Poverty Line thesis (operator capture · MMI-INTAKE-2026-06-23-005)",
        "Industry term (Sophos + sector literature): SMBs below a price/feature floor get retail AV or nothing — prime ransomware targets.",
        "Two walls create the gap:",
        "  · Minimum Seat Wall — enterprise quotes require 50–500 seats; 25-employee shop cannot pay $50k entry.",
        "  · TCO Wall — license + alert firehose + analyst salary; true cost 200–400% above sticker.",
        "Enterprise blind spots Mutant Monkey addresses (beside Defender):",
        "  · Keys to the castle — BEC uses valid-looking mail, not malware attachments.",
        "  · Alert fatigue — decision-support + evidence, not SOC noise.",
        "  · No business context — Dial 1 documented override when evidence says legit deal.",
        "  · Defender BEC gap — look-alike domain, forged thread, vendor wire fraud without malicious code.",
        "GTM frame: pull Canadian SMB above poverty line through MSP federation — quality in evidence chain, not corporate logo.",
        "Price framing (conditional): if smash price hurts credibility — base seat = Inbox Shield decision layer only;",
        "  full 70-agent swarm + Lung scale + federation mesh = separate tiers (INTAKE-2026-06-23-005 §9).",
        "Operator intent: mission over margin extraction — smash bands honest for poverty-line crossing; not locked MSRP.",
        "",
        "## 3. Per-vendor pricing table",
    ]
    vendor_rows = [
        [
            v.vendor[:18],
            v.product[:28],
            _money(v),
            v.channel[:14],
            v.confidence[:12],
        ]
        for v in sorted(
            report.vendors,
            key=lambda x: (x.usd_per_seat_month is None, x.usd_per_seat_month or 999),
        )
    ]
    lines.extend(
        _render_table(["Vendor", "Product", "Price", "Channel", "Confidence"], vendor_rows)
    )
    lines.extend(["", "## 4. Federation / pool analog table"])
    fed_rows = [
        [
            f.company[:16],
            f.product[:26],
            f.pool_model[:36],
            f.tenant_data_crosses[:10],
            f.confidence[:12],
        ]
        for f in report.federation_analogs
    ]
    lines.extend(
        _render_table(
            ["Company", "Product", "Pool model", "Data cross", "Confidence"],
            fed_rows,
        )
    )
    lines.extend(["", "## 5. MSP marketplace observations"])
    lines.extend(
        [
            "- Barracuda MSP: monthly usage-based per account — pool billing at MSP layer.",
            "- Bitdefender / Acronis: multi-tenant + cross-customer remediation; quote per seat.",
            "- ESET MSP: explicit volume tier breaks (more seats → lower unit).",
            "- Pax8/Sherweb: distributor pool for Hornetsecurity, Proofpoint, VIPRE SKUs — verify live.",
            "",
            "## 6. Canadian tier scenario bands — smash hypothesis (not locked)",
        ]
    )
    for s in report.scenarios:
        lines.append(f"- {s.name} ({s.seat_count} seats)")
        lines.append(f"  Incumbent band: {s.incumbent_range_usd_month}")
        lines.append(f"  Federation hypothesis: {s.federation_hypothesis_usd_month}")
        lines.append(f"  Notes: {s.notes}")
    lines.extend(["", "## 7. UNVERIFIED / manual follow-up"])
    for item in report.unverified:
        lines.append(f"- {item}")
    if report.refresh_notes:
        lines.extend(["", "## 8. Live refresh notes"])
        for note in report.refresh_notes:
            lines.append(f"- {note}")
    lines.extend(
        [
            "",
            "## 9. Boundary",
            "Advisory research only. Matt §11 required before any locked pricing or GTM claim.",
            "Does not advance MMI-DEC-132 in decision log — operator review after --write.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_json(report: ResearchReport) -> str:
    payload = {
        "envelope": ENVELOPE,
        "generated_at": report.generated_at,
        "git_head": report.git_head,
        "vendors": [asdict(v) for v in report.vendors],
        "federation_analogs": [asdict(f) for f in report.federation_analogs],
        "scenarios": [asdict(s) for s in report.scenarios],
        "unverified": report.unverified,
        "refresh_notes": report.refresh_notes,
    }
    return json.dumps(payload, indent=2) + "\n"


def write_artifacts(root: Path, report: ResearchReport) -> list[Path]:
    out_dir = root / INTEL_DIR / report.generated_at
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    report_txt = out_dir / "report.txt"
    report_txt.write_text(render_human(report), encoding="utf-8")
    written.append(report_txt)

    json_path = out_dir / "report.json"
    json_path.write_text(render_json(report), encoding="utf-8")
    written.append(json_path)

    memo_path = root / MEMO_REL
    memo_body = [
        "# MMI Research — Federation SMB Seat Economics (Stage B · b01 · MMI-DEC-132)",
        "",
        "**Classification:** `RESEARCH_INPUT` · `ADVISORY_MEMO` · `ZERO_ROUTING_INFLUENCE` · `NOT_BUILD_AUTHORIZATION`",
        "",
        f"**Generated:** {report.generated_at} · git `{report.git_head}`",
        "",
        "**Source:** `scripts/mmi_smb_seat_pricing_research.py --write`",
        "",
        "**Boundary:** Hypothesis bands only. Not locked MSRP. Not GTM claims. Matt §11 before commercial lock.",
        "",
        "---",
        "",
    ]
    memo_body.extend(render_human(report).splitlines()[6:])  # skip envelope header dup
    memo_path.write_text("\n".join(memo_body) + "\n", encoding="utf-8")
    written.append(memo_path)
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="MMI SMB seat pricing + federation pool competitive research"
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help="Run research and print human report to stdout (default)",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write memo + competitive_intel/ artifacts",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Also print JSON summary to stdout",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Attempt live fetch of key public pricing URLs",
    )
    args = parser.parse_args(argv)
    if not args.run and not args.write:
        args.run = True

    root = _repo_root()
    report = build_report(root, refresh=args.refresh)

    if args.run:
        sys.stdout.write(render_human(report))
    if args.json:
        sys.stdout.write(render_json(report))
    if args.write:
        paths = write_artifacts(root, report)
        sys.stderr.write(
            "WROTE:\n" + "\n".join(f"  {p.relative_to(root)}" for p in paths) + "\n"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
