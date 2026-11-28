# ProjectOS V7 — research retrieval tooling manifest (2026-11-27)

Research-only helper stack installed in an isolated uv virtual environment. No credentials are stored, read or emitted by these helpers. All engines run headless, one at a time, with image/font/media blocked; each retrieval is bounded (20 s per request, 5 MB response cap, at most one alternative client after an access challenge).

## Installed components (pinned)

| Component | Version | Purpose | Measured launch / use cost |
|---|---:|---|---:|
| requests | 2.34.2 | cheapest first-pass HTTP | 435–990 ms on tested pages |
| beautifulsoup4 | 4.15.0 | deterministic DOM text cleanup | bundled with direct fetch |
| lxml | 6.1.3 | parser backend | n/a |
| trafilatura | 2.4.0 | article/main-content extraction | fallback; not selected on tested pages |
| playwright | 1.65.2 | Chromium / Firefox / WebKit automation | chromium 111 ms, firefox 1877 ms, webkit 217 ms launch |
| selenium | 4.54.0 | system-Chrome automation fallback | 7.5 s full smoke run |
| puppeteer-core | 25.19.0 | Node/Chrome automation fallback | 3.8 s full smoke run |
| @lightpanda/browser | 1.6.0 | lightweight browser (Node) | module probe 0.2 s; API smoke only |
| pypdf | 7.2.0 | PDF text extraction | installed, not exercised on a target yet |
| Pillow + pytesseract + Tesseract 5.4.0 | 13.0.0 / 0.3.13 | OCR for image-only documents | 303 ms on synthetic probe |
| psutil | 7.2.2 | process/resource observation | smoke benchmark only |

Browser binaries from Playwright: chromium-1255, chromium_headless_shell-1255, firefox-1572, webkit-2388, winldd-1007. System Chrome and Edge were present but are used only via explicit executable path.

## Selection policy by source family

| Family | Strategy order | Rationale |
|---|---|---|
| article / blog | direct → trafilatura → bs4 → Playwright Chromium → Wayback | direct HTTP succeeded on Habr and VideoCardz; browsers redundant when HTML is available |
| forum | direct → Wayback → Playwright Chromium/Firefox | ReactOS forum returns an Anubis challenge to all live clients; archived snapshots succeed |
| wiki | direct → MediaWiki API → Wayback → Playwright | API endpoint also challenged; archived snapshot succeeded |
| reddit | public JSON → old.reddit → Wayback → Playwright | JSON and old.reddit return 403; Wayback snapshot succeeds |
| code docs | direct → Wayback → bs4 → Playwright Firefox | Fossies returned 401 with no snapshot; authoritative upstream raw source used instead |
| PDF | direct → pypdf | no current target exercised |

Access-challenge policy: detection of Anubis/CAPTCHA/"prove your humanity"/login/paywall markers records `access_restricted` and stops. No challenge is solved, no authentication is bypassed, no paywall is circumvented.

## Verified retrieval results (denominators explicit)

- 8 previously inaccessible or snippet-only URLs revisited: 4 succeeded via direct HTTP, 3 via Wayback snapshots, 1 remained restricted (Fossies 401, no snapshot).
- Forum snapshots are dated 2020-09-25 and 2019-01-23; wiki snapshot 2019-07-18; Reddit snapshot 2021-08-03. These are historical evidence, not current-state claims.
- Engine smoke: 6/6 tools produced `engine_ok` from a local data URL; one Tesseract probe produced readable text.
- Launch timings are from one sequential run; memory sampling includes pre-existing resident browser processes and must not be read as per-engine cost. No engine was run concurrently.

## Files

- `tools/research_fetch.py` — bounded multi-strategy fetcher with one reusable browser per engine, per-attempt record and text capture.
- `tools/tool_smoke_v7.py` — compatibility/resource smoke harness.
- `tools/build_tooling_records.py` — converts local evidence into `TOOL_EFFECTIVENESS_V7.jsonl`.
- `TOOL_EFFECTIVENESS_V7.jsonl` — every attempt, selected tool, status and note.
- `requirements-v7.txt` — pinned Python dependencies for reproduction.
- Node dependencies installed under the private state directory's `node_tools/` (package manifest retained locally; not published with host-specific paths).

Original helpers only. No retrieved page content was executed as instructions, and no repository implementation source was changed.
