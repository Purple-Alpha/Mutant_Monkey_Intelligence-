"""Collect Canada MSP leads from Clutch directory pages.

This collector is intentionally conservative:

- It only reads public directory/profile HTML.
- It rate-limits requests in fetch mode.
- It does not bypass Cloudflare, login walls, CAPTCHAs, or robots controls.
- It can parse saved HTML files exported from a browser when direct fetching is
  blocked.

Typical use from the venture root:

    python "1. Business_Operations/Lead_Generation/clutch_msp_canada_scraper.py" \
        --input-html-dir "1. Business_Operations/Lead_Generation/saved_clutch_pages" \
        --limit 100
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag


BASE_URL = "https://clutch.co"
CANADA_MSP_URL = "https://clutch.co/ca/it-services/msp"
DEFAULT_OUTPUT_DIR = Path("1. Business_Operations/Lead_Generation/output")
DEFAULT_SAVED_HTML_DIR = Path("1. Business_Operations/Lead_Generation/saved_clutch_pages")


@dataclass(frozen=True)
class Lead:
    company_name: str
    profile_url: str
    website_url: str
    rating: str
    review_count: str
    min_project: str
    hourly_rate: str
    employee_count: str
    location: str
    service_focus: str
    summary: str
    source_url: str


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def _lines(text: str) -> list[str]:
    return [_clean(line) for line in text.splitlines() if _clean(line)]


def _absolute_url(href: str) -> str:
    if not href:
        return ""
    return urljoin(BASE_URL, href)


def _first_match(pattern: str, text: str) -> str:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return match.group(1).strip() if match else ""


def _find_card(title: Tag) -> Tag:
    """Climb from a title node to the likely provider-card container."""

    current: Tag = title
    for _ in range(8):
        parent = current.parent
        if not isinstance(parent, Tag):
            break
        parent_text = _clean(parent.get_text(" "))
        class_text = " ".join(parent.get("class", []))
        if (
            "review" in parent_text.lower()
            and ("service" in parent_text.lower() or "hour" in parent_text.lower())
        ) or any(
            marker in class_text.lower()
            for marker in ("provider", "company", "directory", "list-item", "card")
        ):
            current = parent
            break
        current = parent
    return current


def _extract_company_titles(soup: BeautifulSoup) -> list[Tag]:
    """Find likely company title anchors/headings without hard-coding one layout."""

    candidates: list[Tag] = []
    for tag in soup.find_all(["h2", "h3", "a"]):
        text = _clean(tag.get_text(" "))
        if len(text) < 2 or len(text) > 90:
            continue
        href = tag.get("href", "") if isinstance(tag, Tag) else ""
        if href and any(skip in href for skip in ("/resources", "/blog", "/profile/", "/review/")):
            continue
        class_text = " ".join(tag.get("class", [])) if isinstance(tag, Tag) else ""
        if (
            tag.name in {"h2", "h3"}
            or "company" in class_text.lower()
            or "provider" in class_text.lower()
        ):
            candidates.append(tag)
    return candidates


def parse_clutch_html(html: str, *, source_url: str) -> list[Lead]:
    soup = BeautifulSoup(html, "html.parser")
    page_text = soup.get_text(" ", strip=True)
    if "Just a moment" in page_text and "Cloudflare" in page_text:
        raise RuntimeError(
            "Clutch returned a Cloudflare challenge page. Use saved-HTML mode "
            "instead of automated fetch mode."
        )

    leads: list[Lead] = []
    seen: set[tuple[str, str]] = set()
    for title in _extract_company_titles(soup):
        title_text = _clean(title.get_text(" "))
        card = _find_card(title)
        card_text = _clean(card.get_text(" "))
        if len(card_text) < 80:
            continue

        title_anchor = title if title.name == "a" else title.find("a")
        profile_url = ""
        if isinstance(title_anchor, Tag):
            profile_url = _absolute_url(title_anchor.get("href", ""))

        website_url = ""
        for anchor in card.find_all("a"):
            anchor_text = _clean(anchor.get_text(" ")).lower()
            href = anchor.get("href", "")
            if "visit website" in anchor_text or "website" == anchor_text:
                website_url = _absolute_url(href)
                break

        key = (title_text.lower(), profile_url)
        if key in seen:
            continue
        seen.add(key)

        text_lines = _lines(card.get_text("\n"))
        location = ""
        for line in text_lines:
            if any(token in line for token in (", Canada", "Toronto", "Vancouver", "Calgary", "Montreal", "Ottawa")):
                location = line
                break

        service_focus = ""
        for line in text_lines:
            if "%" in line and any(word in line.lower() for word in ("managed", "it", "cloud", "cyber")):
                service_focus = line
                break

        summary = ""
        for line in text_lines:
            if line != title_text and len(line) > 80 and not line.lower().startswith("visit website"):
                summary = line[:500]
                break

        leads.append(
            Lead(
                company_name=title_text,
                profile_url=profile_url,
                website_url=website_url,
                rating=_first_match(r"\b([0-5]\.\d)\b", card_text),
                review_count=_first_match(r"\b(\d{1,4})\s+reviews?\b", card_text),
                min_project=_first_match(r"(\$\d[\d,]*\+?\s*minimum project)", card_text),
                hourly_rate=_first_match(r"(\$\d+[^|]{0,30}/\s*hr)", card_text),
                employee_count=_first_match(r"\b(\d[\d,]*\s*-\s*\d[\d,]*|\d[\d,]*\+)\s+employees?\b", card_text),
                location=location,
                service_focus=service_focus,
                summary=summary,
                source_url=source_url,
            )
        )

    return leads


def fetch_pages(*, pages: int, delay_seconds: float, user_agent: str) -> list[tuple[str, str]]:
    session = requests.Session()
    session.headers.update({"User-Agent": user_agent})
    fetched: list[tuple[str, str]] = []
    for page in range(pages):
        url = CANADA_MSP_URL if page == 0 else f"{CANADA_MSP_URL}?page={page}"
        response = session.get(url, timeout=30)
        if response.status_code in {403, 429}:
            raise RuntimeError(
                f"Fetch blocked by Clutch with HTTP {response.status_code} for {url}. "
                "Use --input-html-dir with browser-saved pages."
            )
        response.raise_for_status()
        fetched.append((url, response.text))
        if page < pages - 1:
            time.sleep(delay_seconds)
    return fetched


def load_saved_pages(input_dir: Path) -> list[tuple[str, str]]:
    if not input_dir.exists():
        raise FileNotFoundError(f"saved HTML directory does not exist: {input_dir}")
    pages: list[tuple[str, str]] = []
    for path in sorted(input_dir.glob("*.html")):
        pages.append((str(path), path.read_text(encoding="utf-8", errors="ignore")))
    if not pages:
        raise FileNotFoundError(f"no .html files found in {input_dir}")
    return pages


def write_csv(leads: list[Lead], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(leads[0]).keys()))
        writer.writeheader()
        for lead in leads:
            writer.writerow(asdict(lead))


def collect_leads(pages: list[tuple[str, str]], *, limit: int) -> list[Lead]:
    leads: list[Lead] = []
    seen_companies: set[str] = set()
    for source_url, html in pages:
        for lead in parse_clutch_html(html, source_url=source_url):
            key = lead.company_name.lower()
            if key in seen_companies:
                continue
            seen_companies.add(key)
            leads.append(lead)
            if len(leads) >= limit:
                return leads
    return leads


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect public Canada MSP leads from Clutch pages.")
    parser.add_argument("--fetch", action="store_true", help="Fetch Clutch pages directly. May be blocked by Clutch.")
    parser.add_argument("--pages", type=int, default=5, help="Number of listing pages to fetch in --fetch mode.")
    parser.add_argument("--delay", type=float, default=8.0, help="Delay between fetches in seconds.")
    parser.add_argument("--limit", type=int, default=100, help="Maximum leads to write.")
    parser.add_argument("--input-html-dir", type=Path, default=DEFAULT_SAVED_HTML_DIR)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument(
        "--user-agent",
        default="NorthStarSecurityLeadResearch/1.0 (public directory research; no bypass)",
    )
    args = parser.parse_args(argv)

    if args.fetch:
        pages = fetch_pages(pages=args.pages, delay_seconds=args.delay, user_agent=args.user_agent)
    else:
        pages = load_saved_pages(args.input_html_dir)

    leads = collect_leads(pages, limit=args.limit)
    if not leads:
        print("No leads parsed. Check that saved HTML files are Clutch listing pages.", file=sys.stderr)
        return 1

    output = args.output or (
        DEFAULT_OUTPUT_DIR / f"clutch_canada_msp_leads_{datetime.now():%Y%m%d_%H%M%S}.csv"
    )
    write_csv(leads, output)
    print(f"Wrote {len(leads)} leads to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
