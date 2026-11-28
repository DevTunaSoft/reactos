# ProjectOS V7 — tooling manifest addendum (96af7ca)

Companion to `TOOLING_MANIFEST_V7.md`. This addendum records the corrected
adaptive-retrieval harness, measured JavaScript-rendering evidence, process and
request limits, and the correction to retrieval statistics. It contains no
credentials and no host-specific paths.

## 1. Safety correction

The previously published `tools/tool_smoke_v7.py` passed two
sandbox-disabling arguments (lines 86 and 106). That tracked file belongs to an
earlier wave and is **not edited here** under the untracked-only publication
rule; it is superseded by `tools/research_fetch_v3.py`, which contains no such
argument. The v3 harness detects those argument tokens at runtime and fails a
launch if any is observed.

Important finding: Playwright disables the Chromium sandbox by default. The v3
harness therefore launches Chromium with `chromium_sandbox=True` (an opt-in that
keeps the sandbox enabled) and verifies the real child-process command lines.
Firefox and WebKit are launched with `headless=True` only. Puppeteer-core uses
`args: []`; Selenium uses only `--headless=new`. No authentication, CAPTCHA,
paywall or other challenge bypass was attempted.

## 2. Portable environment

| Variable | Purpose |
|---|---|
| `PROJECTOS_V7_CHROME_PATH` | system Chrome executable for Puppeteer-core and Selenium |
| `PROJECTOS_V7_NODE_TOOLS` | directory containing `node_modules` for `require()` |
| `PROJECTOS_V7_STATE_DIR` | local evidence directory for the statistics correction |
| `PROJECTOS_V7_LIGHTPANDA_BIN` | optional CLI override; unset on this host |

Node dependencies and versions are in `package-v7.json`. Browser binaries come
from the Playwright installation or from the system Chrome named by the
environment variable; no local path is published.

## 3. Commands executed

```sh
export PROJECTOS_V7_CHROME_PATH=<system Chrome executable>
export PROJECTOS_V7_NODE_TOOLS=<dedicated node_tools directory>
export PROJECTOS_V7_STATE_DIR=<local state directory>
python tools/research_fetch_v3.py --mode all \
  --out-dir docs/projectos/research
```

The same harness also accepts `--mode integration` and `--mode correction`.
`python` was the isolated V7 virtual environment (Python 3.14.9).

## 4. JavaScript-rendering proof

Local fixture: a `data:` URL whose empty `<body>` is filled by a `<script>`
that sets `document.body.innerHTML` to `<main id="js-proof">` containing the
known string `V7_JS_RENDER_OK_9f3c`, and sets `window.__v7RenderedByJs = true`.
All five applicable engines asserted the string **and** the JavaScript flag;
static HTML would satisfy neither.

| Engine | Launch ms | JS assertion | Public pages (DOM text chars) | Leaked children |
|---|---:|---|---|---:|
| Playwright Chromium | 933 | true | python.org 3886; iana.org 2469 | 0 |
| Playwright Firefox | 1596 | true | python.org 3886; iana.org 2469 | 0 |
| Playwright WebKit | 405 | true | python.org 3876; iana.org 2455 | 0 |
| Puppeteer-core (system Chrome) | 4676 | true | python.org 3836; iana.org 2299 | 0 |
| Selenium (system Chrome) | 1256 | true | python.org 3816; iana.org 2299 | 0 |

Public URLs: `https://www.python.org/` and
`https://www.iana.org/domains/reserved`. Every public navigation returned HTTP
200 where the engine exposes a status (Playwright and Puppeteer); Selenium does
not expose an HTTP status, so navigation was confirmed with
`document.readyState` plus extracted DOM text. Extracted text samples are
recorded in `TOOL_INTEGRATION_V7.jsonl`.

Forbidden sandbox-disabling flags observed in real child command lines:
Chromium 0/4 inspected, Firefox 0/4, WebKit 0/2, Selenium Chrome 0/9.
Puppeteer-core's actual Chrome `spawnargs` were sampled from Node: 0 forbidden
flags. Total forbidden flags across all engines: **0**.

## 5. Bounds, cleanup and measurements

- Response cap: 5,000,000 bytes; largest observed body/DOM was 53,656 bytes
  (Selenium, python.org), well under the cap.
- Per-request timeout: 20 s everywhere (Playwright navigation, Puppeteer
  navigation/protocol, Selenium page load, HTTP/CLI probes).
- Retries: at most 2 attempts per navigation; maximum actually used in the
  final run was 1. Earlier WebKit failures on `https://example.com/` consumed
  2 attempts and were replaced with the two pages above rather than bypassing
  any protection.
- psutil snapshots were taken before launch, after launch and after cleanup
  for every engine. Browser-process RSS before/after cleanup (MB):
  Chromium 1656.0 → 1668.3; Firefox 1668.2 → 1670.0; WebKit 1670.6 → 1671.0;
  Puppeteer 1563.9 → 1564.1; Selenium 1564.1 → 1562.2. These are host-wide
  browser-process totals, not per-engine cost. New live child processes after
  cleanup: 0 for all five engines.
- No engine was launched concurrently.

## 6. Lightpanda limitation

Status: `unavailable_platform`. Checks performed: `wsl.exe -l -q` returned a
zero distro count; no `lightpanda` CLI was found on PATH; the Node module probe
returned only the `lightpanda` export key, i.e. API helpers rather than a
launchable browser. The previously verified native CLI installation failure
reported a platform incompatibility on Windows. No page navigation or success
is claimed for Lightpanda; it is excluded from the applicable-engine counts.

## 7. Retrieval-statistics correction

`TOOL_EFFECTIVENESS_CORRECTION_V7.jsonl` appends corrected records for all 24
prior rows:

- 17 prior `source_retrieval` attempt rows: `source_url` restored from the
  per-attempt URL (the old builder read a non-existent top-level `url`, so all
  17 were published as `null`); `selected` corrected (17 were previously
  `false`; 7 are now `true`, exactly one per source with a successful
  retrieval); statuses made honest (401/403/challenge rows become
  `access_restricted`, `no_snapshot` becomes `no_snapshot_available`).
- 7 prior engine/OCR smoke rows reclassified as `benchmark_only` with
  `selected: false` and `counted_as_source_retrieval: false`. Benchmark rows
  are never counted as source retrievals.
- Corrected denominators: 8 distinct sources, 7 with a selected successful
  retrieval, 1 restricted without a usable retrieval (Fossies 401, no
  snapshot), 0 benchmark rows counted as sources.

## 8. Files

- `tools/research_fetch_v3.py` — sanitized harness (published copy; identical
  working copy also kept in the private research workspace).
- `TOOL_INTEGRATION_V7.jsonl` — 28 records: environment, 5 launches, 5 JS
  assertions, 10 public-page navigations, 5 cleanup checks, Lightpanda
  availability check, integration summary.
- `TOOL_EFFECTIVENESS_CORRECTION_V7.jsonl` — 25 records: 24 corrected prior
  rows plus a correction summary.
- `package-v7.json` — portable Node dependency manifest.
- `TOOLING_MANIFEST_V7_ADDENDUM.md` — this file.

Research-only: build, boot, install and runtime tests remain **NOT RUN**.
