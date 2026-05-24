"""Shared constant tables for Phase 1.3 Red profile generators.

All identifiers in this module live in the reserved ``.example`` /
``.test`` / ``.invalid`` namespace per the deep dive §2.5 sandbox-safety
boundary. The ``SyntheticEmailAttackCasePayload`` model validator
rejects any case carrying a non-reserved-namespace sender or recipient,
so misuse here fails fast.

Each table is deliberately frozen as a ``tuple`` so Red profile
generators can index into them without re-shuffling, which keeps
output byte-deterministic per Matt's §11 decision 3 floor of ≥ 100
unique cases per profile per battery.
"""

from __future__ import annotations

from typing import Final

# --- Internal recipient addresses (Blue's tenant) ---------------------------
RECIPIENT_AP: Final[str] = "ap@northstar-customer.example"
RECIPIENT_FINANCE: Final[str] = "finance@northstar-customer.example"
RECIPIENT_OPS: Final[str] = "ops@northstar-customer.example"


# --- Vendor names used across profiles --------------------------------------
VENDOR_NAMES: Final[tuple[str, ...]] = (
    "Acme Manufacturing",
    "Tech Corp",
    "Pro Services",
    "Global Parts",
    "Pacific Logistics",
    "Northern Supply",
    "Coastal Office Goods",
    "Midwest Equipment",
    "Atlantic Imports",
    "Mountain Materials",
)


def vendor_slug(name: str) -> str:
    """Lowercase, hyphenated slug for synthesizing a vendor domain."""

    return name.lower().replace(" ", "-")


# --- Urgency phrases (paired with finance language) ------------------------
URGENCY_PHRASES: Final[tuple[str, ...]] = (
    "today",
    "by end of day",
    "before EOB",
    "this afternoon",
    "as soon as possible",
)


# --- Dollar amount bands. Chosen so they bracket the "unusual_dollar_amount"
# detector's typical threshold ($25k+) without being clones of any real
# invoice number. ---
DOLLAR_AMOUNTS: Final[tuple[int, ...]] = (
    8_500,
    12_400,
    18_240,
    27_900,
    44_600,
    61_300,
    78_150,
    96_400,
    134_750,
    188_220,
)


# --- Sender-domain variant kinds used by FAKE_INVOICE_RED ------------------
# Each variant takes a vendor slug and a base TLD and returns a host.
SENDER_DOMAIN_VARIANT_KINDS: Final[tuple[str, ...]] = (
    "matching_legit",
    "hyphen_insertion",
    "prefix_bolted",
    "suffix_bolted",
    "tld_swap",
)


def build_sender_domain(slug: str, kind: str) -> str:
    """Build a sandbox-safe sender domain for a vendor + variant kind."""

    if kind == "matching_legit":
        return f"{slug}.example"
    if kind == "hyphen_insertion":
        # Re-hyphenate an already-hyphenated slug or insert one when bare.
        parts = slug.split("-")
        if len(parts) >= 2:
            return f"{parts[0]}-{parts[-1]}-llc.example"
        return f"{slug}-llc.example"
    if kind == "prefix_bolted":
        return f"invoices-{slug}.example"
    if kind == "suffix_bolted":
        return f"{slug}-payments.example"
    if kind == "tld_swap":
        return f"{slug}.test"
    raise ValueError(f"unknown sender-domain variant kind: {kind!r}")


# --- Vendor-update pivot patterns -------------------------------------------
VENDOR_UPDATE_PATTERN_KINDS: Final[tuple[str, ...]] = (
    "ach_routing_change",
    "remit_to_address_change",
    "thread_hijack_reply",
    "future_dated_invoice",
)


# --- Malicious attachment kinds the Red profile cycles through --------------
# Each kind maps to one filename + one content_type + one AttachmentClass.
MALICIOUS_ATTACHMENT_KINDS: Final[tuple[tuple[str, str, str, str], ...]] = (
    # (kind, filename, content_type, attachment_class)
    ("executable", "shipping_manifest.exe", "application/x-msdownload", "payload_carrier"),
    ("iso_image", "invoice_packet.iso", "application/x-iso9660-image", "payload_carrier"),
    ("macro_office", "purchase_order.docm", "application/vnd.ms-word.document.macroEnabled.12", "executable_doc"),
    ("double_extension", "remittance.pdf.exe", "application/x-msdownload", "payload_carrier"),
    ("encrypted_archive", "secure_documents.zip", "application/zip", "payload_carrier"),
    ("html_smuggling", "invoice_preview.html", "text/html", "credential_lure"),
    ("vhd_image", "backup_set.vhd", "application/octet-stream", "payload_carrier"),
)


# --- Body sentence fragments used by malicious-attachment Red profile ------
MALICIOUS_ATTACHMENT_BODIES: Final[tuple[str, ...]] = (
    "Please open the attached file and confirm receipt as soon as possible.",
    "Documents are attached for your records. Open to view delivery details.",
)


# --- URL obfuscation kinds + sample hosts the Red profile cycles through ---
# Each kind maps to a single base URL the generator may pad with paths.
URL_OBFUSCATION_KINDS: Final[tuple[tuple[str, str], ...]] = (
    # (kind, base_url) - all hosts in the reserved namespace
    ("punycode", "https://xn--80akhbyknj4f.example"),
    ("homoglyph", "https://раypal-secure.example"),  # Cyrillic 'a' homoglyph
    ("shortener", "https://bit.ly.example/3xQp9Z"),
    ("credential_bearing", "https://login@portal-update.example"),
    ("suspicious_tld", "https://secure-update.zip.example"),
    ("ip_address", "https://192.0.2.45.example"),
)


# --- Login / password reset path fragments used by URL Red profile ---------
URL_PATH_FRAGMENTS: Final[tuple[str, ...]] = (
    "/login",
    "/signin",
    "/account/verify",
    "/portal/reset",
    "/secure/update",
    "/auth/confirm",
    "/sso/login",
    "/account/login",
    "/portal/login",
)


# --- Body sentence fragments used by URL Red profile -----------------------
URL_BODIES: Final[tuple[str, ...]] = (
    "Please verify your account using the secure link below.",
    "Action required: reset your password using the portal link.",
)


__all__ = [
    "DOLLAR_AMOUNTS",
    "MALICIOUS_ATTACHMENT_BODIES",
    "MALICIOUS_ATTACHMENT_KINDS",
    "RECIPIENT_AP",
    "RECIPIENT_FINANCE",
    "RECIPIENT_OPS",
    "SENDER_DOMAIN_VARIANT_KINDS",
    "URGENCY_PHRASES",
    "URL_BODIES",
    "URL_OBFUSCATION_KINDS",
    "URL_PATH_FRAGMENTS",
    "VENDOR_NAMES",
    "VENDOR_UPDATE_PATTERN_KINDS",
    "build_sender_domain",
    "vendor_slug",
]
