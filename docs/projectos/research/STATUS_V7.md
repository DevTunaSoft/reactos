# ProjectOS V7 — Wave 1 status and handoff

Status timestamp: 2026-11-27T05:45Z. Research only. No OS code changed, no patch adopted, no test executed, no PR merged.

## Directive revision used (exact)

- Version 7, 2026-11-26, from commit `5c02f5c57e25a6f85b93623f56d39e58f27c116d` in `DevTunaSoft/reactos`.
- File blob SHA-256: `c0cc15328ecb7208701d0d2cae5b52d91b66b04ccca98ecd8cb29dbc58d979ae`.
- Git blob hash (`git hash-object`): `9beaf0db7b720388b63afd8270160c47ff2c5830`.
- Full text preserved locally; prior PR #1 records preserved unmodified.

## Pinned baselines

- Upstream `reactos/reactos` master and `DevTunaSoft/reactos` master: `3e6033a613fbf7c5bd58aaeaa05af42514af59d5` (re-resolved live 2026-11-27T05:14Z).
- Research parent: `5c02f5c57e25a6f85b93623f56d39e58f27c116d` (PR #1 head).
- Stacked draft branch: `research/v7-wave1`, base `research/fork-archaeology-2026-11-26`.

## Queue and supervisor

- Durable queue: append-only `queue_events.jsonl` + atomically replaced `queue_state.json` under the private research state directory. Sanitized snapshot published as `QUEUE_SNAPSHOT_V7.jsonl`.
- Original helper scripts: `tools/supervisor.py`, `tools/collect_network.py`, `tools/revalidate_findings.py`, `tools/build_records.py`. Read-only GitHub API via the existing authorized `gh` CLI; no token read, printed or stored by the scripts.
- Crash recovery test: PASS. Worker A claimed synthetic task, heartbeat backdated to simulate a crash, and worker B's claim produced a `lease_reclaimed` event and reassigned the same task. Exact evidence: `queue_events.jsonl` entries at 2026-11-27T05:19:36Z.
- Lease: 900 s; max attempts: 3; stale lock timeout: 600 s; single-writer lock enforced.
- Emergency stop: presence of `<state>/EMERGENCY_STOP` blocks all claims. Stop is local only and must be removed explicitly to resume.

## Wave 1 results (denominators explicit)

| Metric | Value | Denominator |
|---|---:|---|
| Fork network members retrieved | 2426 | unique repository IDs from paginated REST fork list |
| Parent lineage verified | 2336 | 2426 fork members (90 unresolved) |
| Archived fork members | 12 | 2426 |
| Disabled fork members | 0 | 2426 |
| Prior candidates revalidated | 999 | 999 prior name-search records |
| Prior candidates still public | 999 | 999 |
| Prior candidates in verified fork network | 910 | 999 (89 outside) |
| Prior findings with cited commit verified | 12 | 12 (F-01..F-12) |
| Exact patch-id matches to merged upstream work | 2 | 3 equivalence checks performed |
| New strong candidate | 1 | 9 findings total |
| Runtime tests executed | 0 | all records marked NOT RUN |

## Highest-value results

- FV7-003: F-02 patch is byte-identical (`git patch-id --stable`) to merged upstream PR #1965 → ALREADY_FIXED.
- FV7-006: modern USB3/xHCI stack merged upstream (PRs #9623, #9646) → historical GSoC branches are archaeology, not patch sources; CORE-13344 still Open.
- FV7-007: WoW64 prerequisites merged (#8713, #9766) while CORE-17655 is Reopened → revalidate older branch diffs against current baseline.
- FV7-009: FreeLoader FAT `FatCountClustersInChain` is unbounded at pinned baseline (lines 1108-1133) and upstream PR #9510 proposing bounds was closed unmerged → one research-only strong candidate; no code imported.

## Blockers / gaps

- 90 fork members have unresolved GraphQL lineage; names may be deleted/private/renamed. Do not infer cause.
- Branch/tag enumeration for the 2426 forks is not complete (queued as W2-01); the 14 branch rows in the inherited round-2 record remain unrevalidated.
- No runtime reproduction, build, VM or test was performed under this wave. All such fields are NOT RUN.
- No multilingual/community, Testman, failure-archive, or independent-forges sweep has run yet (W2-02, W3-01, W3-02 queued).
- Independent evidence reviewer not yet assigned; all findings marked `pending_independent`.

## Next actions

1. Enumerate branches/tags for verified fork members with pinned tip SHAs (W2-01).
2. Independent review of FV7-009 and the bounded-traversal hypothesis; produce engineering packet only if it survives review.
3. Failure archaeology and multilingual community sweep (W2-02, W3-01).
4. Revalidate F-04 TheNNX five commits against the newly landed WoW64 prerequisites.

## Wave 2 checkpoint — W2-01 bounded ref enumeration (2026-11-27T05:52Z)

- Worker `cron-20261127T055054Z`; single task W2-01 claimed at 2026-11-27T05:51:06Z (900 s lease). No `EMERGENCY_STOP`; 0 running leases at claim. Remote identity and branch verified before writing: origin `https://github.com/DevTunaSoft/reactos.git`, HEAD and remote `research/v7-wave1` = `bc35d6a35001b6a58296ebbe1ede0b3d1ba65efd`.
- Cohort: 12 most-recently-pushed verified non-archived forks + 3 archived forks, selected deterministically from the W1-01 verified network (2426 members). 15 repositories, all public REST 200.
- Retrieval 2026-11-27T05:52:26Z via `gh api`: `GET /repos/{full_name}/branches?per_page=100&page=N`, `GET /repos/{full_name}/tags?per_page=100&page=N`, `GET /repos/{full_name}` for license/provenance. Results: 1,221 branches, 1,177 tags, 1,210 distinct tip SHAs; 382 tip SHAs shared by 2+ forks (dedup by exact SHA).
- Bounded limit reached honestly for `nitroos-org/reactos` only (500 branches recorded, 5-page cap hit, true count not established). Other 14 repos ended below the cap; endpoints complete for the tested sample.
- SPDX licenses observed: GPL-2.0 and GPL-3.0. All sampled repos are verified fork-network members; retrieved content treated as untrusted evidence.
- Three tips pinned with full SHAs at 2026-11-27T05:54:08Z: `ebef9d5d6b43b5094cd5d343127952a08220cdf4` (`fix/fastfat-fat-write-race`), `ff79e163074e2f8368c8fbb2e254d4db9b8ee70c` (`GSoC_2017/usbxhci`), `ef34d4e269764168ebe386c603b44b4350ccf328` (`feat/wow64-3c-win32k-thunks`). Each resolves in `reactos/reactos` with an identical commit-message first line (clarification appended at 2026-11-27T05:55Z). Tip identity is not proof of master ancestry or whole-branch equivalence.
- New leads observed, not adopted: `nitroos-org/reactos` `feat/wow64-3b*`/`3c*` and `fix/btrfs-*`/`fix/fastfat-*` branches; `Kreijstal/reactos` `GSoC_2017/usbxhci`, `wow64-ntfs` branches. Queued as W4-01 and W4-02.
- Runtime/build/test fields: NOT RUN. Patch-equivalence dedup: NOT RUN (no patch import authorized).
- Canonical evidence: `REF_ENUMERATION_V7.jsonl` (append-only, 20 records, 4 record types).

This document is a checkpoint, not a claim that research is complete.

## Correction/addendum — community discovery and path sanitization (2026-11-27T05:58Z)

- Eight public community/press/mirror leads were retrieved at 2026-11-27T05:55Z using web search (one Russian-language lane, seven English-language sources). Records: `COMMUNITY_LEADS_V7.jsonl`, with faithful summaries, exact URLs, uncertainty and explicit corroboration/contradiction links. Only search snippets were inspected for these leads; full-page extraction remains queued (W3-03..W3-07).
- Notable contradiction: `reactos.org/wiki/Supported_USB_Devices` still describes `usbxhci.sys` as non-existent, while PR #9646 is verified merged. Recorded as documentation lag; not resolved by inference.
- Third-party 0.4.16 source mirror shows the same unbounded `FatCountClustersInChain` loop as the pinned upstream baseline; mirror is corroboration only, not authoritative (W3-05).
- Provenance correction: two W2-01 helper scripts initially contained host-specific absolute paths. They were rewritten to derive paths from environment variables or their own location; no credential values were ever present. This correction is appended rather than rewriting history.
- Queue was replenished with W3-03..W3-07 and W4-01/W4-02; no duplicate lease was created during the concurrent unattended run.

## Wave 3 checkpoint — parallel lanes, infrastructure fixes and corrections (2026-11-27T06:25Z)

Four research lanes and one dedicated infrastructure agent ran in parallel; none changed OS implementation code, performed a test, merged or pushed a PR.

- Supervisor v2 (`tools/supervisor.py`) replaces v1: UTC-only lease arithmetic (`calendar.timegm`, no `time.mktime`), worker+lease-id enforced on beat/complete/review, retry increments on lease reclaim, bounded exponential backoff with `available_at`, meaningful-progress stall detection, idempotent `replenish`, and ledger `replay`. Independently re-run here: `SUMMARY 32/32 checks passed; exit=0`. Replay rebuilt 22 events into 11 tasks with identical counts.
- Restoration proof: clean `git clone --depth 1 --branch research/v7-wave1` at HEAD `8591a33`, 18 canonical paths present, JSONL parsed, zero secret/personal-path hits, zero private artifacts. Cron job `08b68a4bc9b8` confirmed enabled/hourly (`hermes cron list`), unchanged. Records: `INFRA_*_V7.jsonl`, `INFRA_SUPERVISOR_V2_FIXES_V7.md`, `INFRA_SUPERVISOR_V2_TEST.*`, `INFRA_BACKLOG_TEMPLATE.json`.
- Independent review (`REVIEW_FV7_009_V7.jsonl`): verdict **needs-work**. Primary source confirms the unbounded loop and unvalidated `BytesPerSector`; engineering packet not warranted without reproducer, tests and per-file licensing review. Tests NOT RUN. Reviewer: `hermes-w3w4-audit-7f3c9a`; assignment in `REVIEWER_ASSIGNMENT_V7.jsonl`.
- WoW64 (`WOW64_PREREQ_V7.jsonl`, 10 records): merged #8713 is an ancestor of all eight sampled 3b/3c tips; merged #9766 is absent from all; all tips diverged from master. No branch is ready for adoption.
- USB3 (`USB3_GAP_V7.jsonl`, `WIKI_CONTRADICTION_V7.jsonl`, `PRESS_RECONCILIATION_V7.jsonl`): drivers exist at pin, but `boot/bootdata/txtsetup.sif` lacks `USB\\ROOT_HUB30`/`PCI\\CC_0C0330` and load entries (open PR #9865); open PR #9750 addresses a WdfVersionBindClass NULL dereference during setup; pinned source still has stub/UNIMPLEMENTED markers. Wiki claim dates to rev 30811 (2012) and still appears at rev 56222 (2025-12-15), i.e. stale documentation. VideoCardz claims not verifiable from PR #9646 beyond merge/driver paths/author statements. Runtime NOT RUN.
- Multilingual/community/history (`MULTILINGUAL_V7.jsonl` 15, `REDDIT_FORUM_V7.jsonl` 15, `HISTORICAL_FAILURES_V7.jsonl` 26): 10 language lanes queried, 6 with usable sources, 4 zero-result; 7 full-page extractions, 21 snippet-only, 25 API extractions; 56 records all NOT RUN. Reddit/forum/wiki direct HTTP blocked (403/Anubis) and recorded as snippets only. Habr article dated 2023-12-30; treated as time-bound, not current 2026 state.
- Branch enumeration (`REF_ENUMERATION_W4_V7.jsonl` 14, `SHARED_TIP_CLASS_V7.jsonl` 439): second cohort of 12 forks, 403 branches and 2988 tags, 252 distinct tips, no capped endpoints; all 382 prior shared tips resolve as exact SHAs in upstream; 54 high-value pins (39 unique). Patch-equivalence dedup NOT RUN.
- Count reconciliation (`COUNT_RECONCILIATION_V7.jsonl`, 8 records) documents exact discrepancies between earlier prose counts and the ledger. Final live queue: 15 verified, 1 reviewed, 2 queued, 0 running (`QUEUE_SNAPSHOT_V7.jsonl`, 18 tasks). Two evidence-backed tasks completed in isolated ledgers were adopted with explicit `integrator_adopt` ledger events; no live lease was fabricated.
- Terminology correction (`TERMINOLOGY_CORRECTION_V7.jsonl`, 11 records): `git patch-id --stable` equality means **normalized patch equivalence**, not byte identity. Earlier wording in FV7-003/FV7-004 and related prose is corrected here without rewriting history. All prior F-02/F-07 conclusions (already fixed upstream) stand.
- Cron prompt updated for the v2 contract (unique worker, lease-id, heartbeats, replenish, independent reviewer flag). No cron schedule or authorization change.

## Wave 4 checkpoint — WoW64 deep diff, USB3 setup verification, test intelligence (2026-11-27T06:42Z)

- `WOW64_DEEP_DIFF_V7.jsonl` (10 records, 8 tips): 98 unique changed paths compared across 8 immutable fork tip patches and merged PRs #8713/#9766. Exact file overlap: one path (`sdk/include/ndk/pstypes.h`) with #8713, zero with #9766; zero patch-id equivalences; 51 paths absent at pinned master. No functional change verified as already upstream; licensing GPL-2.0-or-later, route A if ever reused; tests NOT RUN. No branch is adoption-ready for CORE-17655.
- `USB3_SETUP_VERIFY_V7.jsonl` (10 records): PR #9865 proposes exactly five text-setup lines (`USB\ROOT_HUB30`, `PCI\CC_0C0330`, and three `[InputDevicesSupport.Load]` driver entries); these are absent at pin and master, no superseding PR found — OPEN. GUI path already landed via #9646 ([SourceDisksFiles] and hivesys.inf). PR #9750's 11-line `WdfVersionBindClass` NULL guard is absent from pin/master — OPEN, with unresolved reviewer findings (class-module reference leak in rollback, CHANGES_REQUESTED metadata). CORE-13344 remains Open; all runtime fields NOT RUN.
- `RELEASE_TAG_FAT_V7.jsonl` (7 records): authoritative 0.4.16 tag resolved and raw `fat.c` fetched; `FatCountClustersInChain` compared to pinned baseline.
- `TEST_INTELLIGENCE_V7.jsonl`: 6 test IDs, 8259 suite runs, 1906 skipped/TODO mappings, 33 CI jobs (29 with skipped steps, 84 skipped steps), 13 endpoints checked. Testman `detail.php` unavailable (0 bytes/timeouts), `export.php` returns "Necessary information not specified"; guessed endpoints 404; Testman revision c7f35f8 unresolved to an immutable commit. GitHub Actions run 42141127747 is compile-and-upload only. Runtime execution NOT RUN.
- Evidence-size correction: the raw 1.9 MB per-test mapping is preserved in private research state; the public `TEST_INTELLIGENCE_V7.jsonl` contains 58 records (27 KB) retaining 100% of the aggregated denominator (1906) with exact source URLs. This is a publication-size correction, not a data deletion.
- Queue reconciliation: W6-01 and W6-03/W3-05 completed via their real v2 leases; W6-02 was adopted with an explicit ledger event because its agent used an isolated ledger. Final live queue: 19 verified, 1 reviewed, 3 queued, 0 running across 23 tasks (`QUEUE_SNAPSHOT_V7.jsonl`). Attempts on interposed-but-unworked tasks were incremented by the v2 backoff rules and remain visible in the ledger.

## Wave 5 checkpoint — retrieval tooling and previously blocked sources (2026-11-27T06:55Z)

- Installed an isolated uv venv with pinned `requests`, `beautifulsoup4`, `lxml`, `trafilatura`, `playwright`, `selenium`, `pypdf`, `psutil`, Pillow and `pytesseract`; Playwright Chromium/Firefox/WebKit and Tesseract 5.4.0 installed and smoke-tested. Node `puppeteer-core` and `@lightpanda/browser` installed in the private state directory. Manifest: `TOOLING_MANIFEST_V7.md`; pins: `requirements-v7.txt`.
- Original helpers: `tools/research_fetch.py` (cheapest-first strategy chain, one reused browser per engine, image/font/media blocked, 20 s request cap, 5 MB response cap, challenge detection with no circumvention), `tools/tool_smoke_v7.py`, `tools/build_tooling_records.py`.
- Engine smoke 6/6 passed from a local data URL: Chromium 111 ms launch, Firefox 1877 ms, WebKit 217 ms; Puppeteer/Chrome, Lightpanda module and Selenium/Chrome all functional. Tesseract probe read synthetic text in 303 ms. Memory samples include pre-existing resident browsers and are not per-engine costs. No engines ran concurrently.
- Revisited 8 previously inaccessible/snippet-only URLs: 4 full pages via direct HTTP (Habr 11821 chars, VideoCardz 15156, mailing archive 16069), 3 via Wayback snapshots (forums 13282/15487, wiki 5690, Reddit 1000), 1 still restricted (Fossies 401, no snapshot; authoritative upstream tag used instead). Reddit JSON and old.reddit returned 403; MediaWiki API was challenged. Challenge markers never bypassed.
- Snapshot dates recorded explicitly: forum 2020-09-25 and 2019-01-23, wiki 2019-07-18, Reddit 2021-08-03. Snapshots are historical evidence, not current-state claims.
- Per-attempt evidence: `TOOL_EFFECTIVENESS_V7.jsonl` (24 records). Selection rule: direct HTTP first; browsers only when HTML is unavailable or JS-dependent; Wayback for Anubis-blocked public pages; public APIs before browser automation.
- No OS implementation source changed; no authentication, CAPTCHA, paywall or access restriction bypassed.

This document is a checkpoint, not a claim that research is complete.

## Wave 6 checkpoint — W6-04 high-value tip / issue correlation (2026-11-27T06:56Z)

- Worker `cron-20261127T065016Z`; W6-04 claimed at 2026-11-27T06:50:23Z (900 s lease `24debf6bf35540669cf5f00fae4dcc66`). No `EMERGENCY_STOP`, 0 active leases at claim; replenish was a no-op (3 queued >= min-queued 2). Remote identity/branch verified before writing: origin `https://github.com/DevTunaSoft/reactos.git`, HEAD and remote `research/v7-wave1` = `514aade2a59fff4e5f444ed86780d88a4787de59`.
- Cohort: 54 `high_value_tip_pin` records in `SHARED_TIP_CLASS_V7.jsonl` deduped by exact SHA to 39 unique pins (30 wow64, 3 xhci, 3 btrfs, 3 fat); source lines and ref names preserved in the new records.
- Retrieval 2026-11-27T06:52:15Z–06:54:14Z, read-only: `GET https://api.github.com/search/issues?q=repo%3Areactos%2Freactos+<sha>` for all 39 SHAs (39/39 exit 0; exact endpoints stored) plus 4 theme searches; JIRA REST `/rest/api/2/search` for 8 JQL queries (exact URLs, JQL and totals stored). All retrieved content treated as untrusted evidence.
- Result: 38/39 per-SHA searches returned `total_count=0`. The one hit, SHA `15c9005acb6878f5397c8fdbf9a5af59a970b8d5` (`USB-3.x-xHCI`), resolved to merged PR #8940 `[MLANG][MLANG_WINETEST] Sync to Wine-10.0` (merged 2026-05-08T07:30:20Z); the exact SHA is absent from the 469-character PR body/metadata. An appended verification record classifies it as false-positive search tokenization; earlier records were not rewritten.
- Domain context only (not tip equivalence): GitHub theme totals WoW64 13, xHCI 7, btrfs 34, fastfat 37 (samples include open #9865/#9750 and merged #9646/#8713/#9766). JIRA: CORE-17655 Reopened, CORE-13344 Open, CORE-18200 Open; domain totals wow64 2, xhci 1 (CORE-20821 Untriaged, updated 2026-10-31), btrfs 78, fastfat 45, FAT32 98.
- Canonical evidence: `TIP_ISSUE_CORRELATION_V7.jsonl` (53 append-only records: 39 per-SHA, 4 theme, 8 JIRA, 1 summary, 1 verification). All lines parse; secret/local-path scan clean. Conclusion: no direct issue/PR citation of any of the 39 exact tip SHAs; absence of a literal reference does not prove unrelatedness. No patch import, build, test or VM; all runtime fields and patch-equivalence dedup NOT RUN.

