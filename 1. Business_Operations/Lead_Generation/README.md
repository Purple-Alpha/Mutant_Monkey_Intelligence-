# Lead Generation

## Clutch Canada MSP Collector

Use `clutch_msp_canada_scraper.py` to collect public company-level MSP leads from Clutch Canada MSP listing pages.

## Important Guardrails

- Do not bypass Cloudflare, CAPTCHA, login walls, or anti-bot controls.
- Collect company-level business data only.
- Do not collect personal emails, personal phone numbers, credentials, or private customer data.
- Rate-limit any direct fetches.
- Prefer saved-HTML mode for Clutch if direct requests are blocked.

## Recommended Saved-HTML Workflow

1. Open `https://clutch.co/ca/it-services/msp` in a browser.
2. Save each listing page as HTML into:

   `1. Business_Operations/Lead_Generation/saved_clutch_pages/`

3. Run:

```powershell
python "1. Business_Operations/Lead_Generation/clutch_msp_canada_scraper.py" `
  --input-html-dir "1. Business_Operations/Lead_Generation/saved_clutch_pages" `
  --limit 100
```

The CSV will land in:

`1. Business_Operations/Lead_Generation/output/`

## Direct Fetch Mode

Direct fetch mode exists, but Clutch may block automated requests:

```powershell
python "1. Business_Operations/Lead_Generation/clutch_msp_canada_scraper.py" `
  --fetch `
  --pages 5 `
  --delay 10 `
  --limit 100
```

If Clutch returns HTTP 403 or 429, stop direct fetch mode and use saved-HTML mode.
