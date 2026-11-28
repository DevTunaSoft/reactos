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

## Wave 7 checkpoint — full-text mining and archived-source correlation (2026-11-27T07:11Z)

- `TIP_ISSUE_CORRELATION_V7.jsonl` (53 records, unattended W6-04): 39/39 unique high-value tip SHA searches succeeded; 38 zero hits. One hit resolved to merged PR #8940 but the exact SHA is absent from its body and is recorded as tokenization noise, not a citation. Theme counts (WoW64 13, xHCI 7, btrfs 34, fastfat 37) and JIRA states are domain context only. Absence of a literal reference does not prove unrelatedness.
- `HABR_FULLTEXT_V7.jsonl` (28 records): full 2023-12-30 Russian annual review, 27 translated technical claims with verbatim short excerpts and time-bound caveats; WoW64/x64 claims correlated to FV7-007 and PRs #8713/#9766, ARM64 to FV7-008 and #9795. No current-state claim inferred from a 2023 source.
- `FORUM_ARCHAEOLOGY_V7.jsonl` (30 records): 30 verbatim quotes from Wayback forum snapshots (5 from t=846 2020 snapshot, 7 from t=17295 2019 snapshot), Ros-dev archive index and 14 HyperKitty messages; 16 correlations to FV7-006 and 18 to FV7-007. Only page 1 of each thread was in the snapshot; broader coverage NOT RUN. Migrated Pipermail URL 404, HyperKitty used and documented.
- `ARCHIVED_CLAIMS_V7.jsonl` (20 records) and `ACADEMIC_PROBES_V7.jsonl` (8 records): 15 archived claim checks and 3 snapshot provenance records with 26 exact-quote assertions passed; 6 academic/archive surfaces probed (15 attempts, 3 with data, 3 challenged/throttled, 5 zero-result lanes, 1 relevant hit, 0 peer-reviewed compatibility studies). OSDev 403 Cloudflare, DBLP 202 Anubis, Semantic Scholar 429, arXiv HTTP 429 then HTTPS zero results — all recorded, none bypassed.
- Queue after reconciliation: 25 verified, 1 reviewed, 2 queued, 0 running across 28 tasks (`QUEUE_SNAPSHOT_V7.jsonl`). Evidence produced in isolated ledgers was adopted with explicit `integrator_adopt` events. Cron's W6-04 checkpoint was independently verified on remote before this append.
- All runtime fields remain NOT RUN; no OS code, patch import, test, merge or upstream submission.

This document is a checkpoint, not a claim that research is complete.

## Wave 6 checkpoint — W6-04 high-value tip / issue correlation (2026-11-27T06:56Z)

- Worker `cron-20261127T065016Z`; W6-04 claimed at 2026-11-27T06:50:23Z (900 s lease `24debf6bf35540669cf5f00fae4dcc66`). No `EMERGENCY_STOP`, 0 active leases at claim; replenish was a no-op (3 queued >= min-queued 2). Remote identity/branch verified before writing: origin `https://github.com/DevTunaSoft/reactos.git`, HEAD and remote `research/v7-wave1` = `514aade2a59fff4e5f444ed86780d88a4787de59`.
- Cohort: 54 `high_value_tip_pin` records in `SHARED_TIP_CLASS_V7.jsonl` deduped by exact SHA to 39 unique pins (30 wow64, 3 xhci, 3 btrfs, 3 fat); source lines and ref names preserved in the new records.
- Retrieval 2026-11-27T06:52:15Z–06:54:14Z, read-only: `GET https://api.github.com/search/issues?q=repo%3Areactos%2Freactos+<sha>` for all 39 SHAs (39/39 exit 0; exact endpoints stored) plus 4 theme searches; JIRA REST `/rest/api/2/search` for 8 JQL queries (exact URLs, JQL and totals stored). All retrieved content treated as untrusted evidence.
- Result: 38/39 per-SHA searches returned `total_count=0`. The one hit, SHA `15c9005acb6878f5397c8fdbf9a5af59a970b8d5` (`USB-3.x-xHCI`), resolved to merged PR #8940 `[MLANG][MLANG_WINETEST] Sync to Wine-10.0` (merged 2026-05-08T07:30:20Z); the exact SHA is absent from the 469-character PR body/metadata. An appended verification record classifies it as false-positive search tokenization; earlier records were not rewritten.
- Domain context only (not tip equivalence): GitHub theme totals WoW64 13, xHCI 7, btrfs 34, fastfat 37 (samples include open #9865/#9750 and merged #9646/#8713/#9766). JIRA: CORE-17655 Reopened, CORE-13344 Open, CORE-18200 Open; domain totals wow64 2, xhci 1 (CORE-20821 Untriaged, updated 2026-10-31), btrfs 78, fastfat 45, FAT32 98.
- Canonical evidence: `TIP_ISSUE_CORRELATION_V7.jsonl` (53 append-only records: 39 per-SHA, 4 theme, 8 JIRA, 1 summary, 1 verification). All lines parse; secret/local-path scan clean. Conclusion: no direct issue/PR citation of any of the 39 exact tip SHAs; absence of a literal reference does not prove unrelatedness. No patch import, build, test or VM; all runtime fields and patch-equivalence dedup NOT RUN.

## Wave 8 checkpoint — W3-02 skipped-suite to issue mapping (2026-11-27T08:03Z)

- Worker `cron-20261127T075902Z`; W3-02 claimed at 2026-11-27T07:59:02Z (900 s lease `a20dc8ed09f545fb8dc92f3d67621e5d`, until 08:14:02Z). No `EMERGENCY_STOP`, 0 active leases at claim; replenish was a no-op (2 queued >= min-queued 2). Remote identity/branch verified before writing: origin `https://github.com/DevTunaSoft/reactos.git`, HEAD and remote `research/v7-wave1` = `fe8d0671e9ad1b2419c2ac2b352d799809d25ea2`.
- Denominator: 1906 private skipped/expected-failure mapping rows across 6 Testman test IDs and 5 revision shorts (ba4a92b, 9749cc0, a2d334d, 3cc9aa9, c7f35f8); 330 distinct suites, 239 with skipped tests, 8604 skipped instances; failure classes 585 todo / 774 real / 547 zero. All 1906 source rows have `issue_key` null, so any issue key below is a research correlation, not a Testman citation.
- Retrieval 2026-11-27T08:00:21Z–08:00:45Z, read-only: 5 `GET /search/issues` queries (totals 28/1/0/11/11) and 4 JIRA REST JQL searches (totals 31/0/2/4), plus 2 direct JIRA issue GETs (HTTP 200). All retrieved text treated as untrusted evidence. A first GitHub batch used `gh api -f` (POST) and returned 404; re-run with `-X GET` succeeded, documented as an appended tooling correction.
- Exact matches: `ws2_32:nonblocking` (6 skipped instances) → ROSTESTS-247 "ws2_32_apitest:nonblocking hangs on Testbot", Resolved/Fixed (direct GET HTTP 200). `kernel32:MultiByteToWideChar` (402) → ROSTESTS-282 "kernel32: Strengthen MultiByteToWideChar tests", Resolved/Fixed (direct GET HTTP 200); function-name results CORE-2622/CORE-6736/CORE-13349 (Resolved/Fixed) and GH PR #9048 (closed) are search-only. `xinput1_3:xinput` (366) and `ntdll:wow64` (33): no canonical suite-specific issue in the queried surfaces (JIRA `xinput1_3` 0, GitHub `xinput` 1 unrelated PR #1831; JIRA wow64+ntdll 4 x64-app reports, GitHub ntdll+wow64 11 incl merged PR #8713). Domain context only; skipped/expected-failure status is not proof of a defect or a fix.
- Correction appended: `test_machine` values `KVM`/`KVM_x64` are TEST HOST labels, not guest architecture; all 1906 rows have guest `ReactOS - i386`. No amd64/arm guest result exists in this sample. Earlier aggregate records were not rewritten.
- Canonical evidence: `TEST_SUITE_ISSUE_MAP_V7.jsonl` (19 append-only records: 1 scope, 1 denominator, 1 correction, 5 suite maps, 5 GitHub searches, 4 JIRA searches, 1 tooling correction, 1 summary). All lines parse, IDs unique, secret/local-path scan clean. No OS code change, patch import, build, test, VM, merge or upstream submission; all runtime fields NOT RUN.

## Wave 9 checkpoint — independent review of FV7-005 / F-03 (2026-11-27T09:06Z)

- Task `RPL-REVIEW-0003` (lane D) claimed by worker `cron-20261127T090408Z` at 2026-11-27T09:04:26Z, 900 s lease `3306ad010b95429998d2df027732d8bc`; reviewer `hermes-rpl-review-0003` is distinct from the claim worker and has no authorship/import stake. Remote identity/branch verified before writing: origin `https://github.com/DevTunaSoft/reactos.git`, HEAD and remote `research/v7-wave1` = `53a7b0a312d5d8c904762251cb7fc297fb057817`. No `EMERGENCY_STOP`; 0 active leases at claim; replenish added 4 template tasks before claim (5 queued).
- Retrieval 2026-11-27T09:05:14Z–09:05:59Z, read-only, all HTTP 200: `GET` of maharmstone/reactos tip `98880e55…` `.patch` (966 B), reactos/reactos PR #1959 `.patch` (1902 B, two commits), merge commit `90ac794b…` `.patch` (948 B), plus `GET /repos/reactos/reactos/pulls/1959` and `GET /repos/reactos/reactos/commits/98880e55…`. Retrieved content treated as untrusted evidence.
- All three recorded patch-ids reproduced exactly with `git patch-id --stable`: tip `98880e55` → `d9e871bd…` (subject "Code style fix only."), functional parent `aad76695` → `688b412e…`, merge commit `90ac794b` → `4a99100f…`. Terminology: patch-id equality = normalized patch equivalence, not byte identity.
- Correction appended: PR #1959 metadata gives `head_sha=98880e55aa6bf4ca24dfa8313783b38d92a94adf` — the exact SHA cited by S-V7-08 as the F-03 fork tip — `merged=true`, `merged_at=2019-10-08T14:50:58Z`, `merge_commit_sha=90ac794b…`; `98880e55` parent is `aad76695…`. Both commits are the two commits of the upstream PR series. The prior `equivalent=false` for F-03 compared a single-commit patch-id against a merge-commit combined-diff patch-id; that inequality is a comparison-method artifact, not evidence of independent implementation.
- Verdict: FV7-005 classification superseded from `EQUIVALENCE_UNKNOWN / NEEDS_SEMANTIC_COMPARISON` (medium) to `ALREADY_UPSTREAM_MERGED` (high); no engineering packet. Canonical evidence: `REVIEW_FV7_005_V7.jsonl` (6 append-only records). Earlier records preserved. No runtime behavior claim; all tests NOT RUN; no OS code, patch import, build, VM, merge or upstream submission.

## Wave 6 checkpoint — W6-05 provenance completeness audit of Wave 3 records (2026-11-27T10:12Z)

- Task `W6-05` (lane D) claimed by worker `cron-20261127T100926Z` at 2026-11-27T10:09:26Z, 900 s lease `f8f88f14e45f4c8484920194c0791a51`. No `EMERGENCY_STOP`; 0 active leases at claim; replenish no-op (4 queued >= min-queued 2). Remote identity/branch verified before writing: origin `https://github.com/DevTunaSoft/reactos.git`, HEAD and remote `research/v7-wave1` = `b31dbaf00c96d0ea40de2c412213d0c7ad3dabe9`.
- Scope: 14 Wave 3 canonical JSONL files named in the 06:25Z checkpoint, 588 records total, 0 parse errors. Read-only per-line `json.loads`; field-presence checked for source id, revision/SHA, retrieval timestamp, license/provenance status and NOT RUN marker. No source record rewritten.
- Findings (appended corrections, not rewrites): (1) explicit license/provenance status exists only in fork-tip families (`REF_ENUMERATION_W4` 92.9%, `SHARED_TIP_CLASS` 99.3%, `REVIEW_FV7_009` 50%) and is absent in 11 files. For `INFRA_*`, `COUNT_RECONCILIATION`, `TERMINOLOGY_CORRECTION` that absence is not applicable (process metadata); for `USB3_GAP`, `WIKI_CONTRADICTION`, `PRESS_RECONCILIATION`, `MULTILINGUAL`, `REDDIT_FORUM`, `HISTORICAL_FAILURES` it is a metadata gap — classified as NOT ESTABLISHED / CITED ONLY, NO REUSE AUTHORIZED; no license inferred. (2) NOT RUN markers are present in every record of the research-evidence families; 0% in metadata records is not a defect. (3) immutable SHA is absent in web/community/JIRA families — classified NOT APPLICABLE (mutable source), with retrieval timestamps / access_status recorded instead.
- Canonical evidence: `PROVENANCE_AUDIT_W6_05_V7.jsonl` (19 append-only records: 1 scope, 14 per-file, 3 findings, 1 summary); 19 unique ids, 0 dupes, secret/local-path scan clean. All runtime fields NOT RUN; no OS code, patch import, build, test, VM, merge or upstream submission.

## Wave 10 checkpoint — RPL-COVERAGE-0002 language-lane coverage extension (2026-11-27T11:13Z)

- Task `RPL-COVERAGE-0002` (lane B) claimed by worker `cron-20261127T111304Z` at 2026-11-27T11:13:04Z, 900 s lease `edfc77e254a7471dbd314358964af990` (until 11:28:04Z). No `EMERGENCY_STOP`; 0 active leases at claim; replenish no-op (3 queued >= min-queued 2). Remote identity/branch verified before writing: origin `https://github.com/DevTunaSoft/reactos.git`, HEAD and remote `research/v7-wave1` = `f2635efdede93dc9f99e1fe74c5f0b967ce8f44f`; clean worktree.
- Selected four language lanes with no record in `MULTILINGUAL_V7.jsonl`: ko, cs, nl, tr. Retrieval 2026-11-27T11:13Z, public `web_search` snippets, `limit=10` per query. All retrieved text treated as untrusted evidence; snippet-only, no full-page extraction, no primary-source verification.
- Explicit denominators: 40 result rows returned across 4 queries (10 per lane); language-matched technical items ko=0, cs=0, nl=1 (`https://linuxmag.nl/reactos-krijgt-na-jaren-werk-ondersteuning-voor-usb-3-0/`, cites Phoronix), tr=1 (`https://www.technopat.net/sosyal/konu/reactos-deneysel-arm64-destegi-sunuyor.4112779`). Zero lanes are zero-at-this-query, not claims of universal absence. 0 publication dates verified, 0 primary-source correlations.
- New source-surface lead only: ReactOS forum Czech subforum (`https://reactos.org/forum/viewforum.php?f=39`) with snippet-derived 58 topics / 489 posts; unverified beyond the snippet, no thread opened.
- The two matched items are secondary reporting of already-recorded primary findings (merged PR #9646 USB3; FV7-008 / PR #9795 ARM64) and establish no new technical claim.
- Canonical evidence: `COVERAGE_EXTENSION_V7.jsonl` (7 append-only records: 1 scope, 4 lane queries, 1 surface lead, 1 summary); 7 unique ids, 0 parse errors, secret/local-path scan clean. `COVERAGE_V7.md` extended with an appended addendum; no earlier record rewritten. All runtime fields NOT RUN; no OS code, patch import, build, test, VM, merge or upstream submission.

## Wave 11 checkpoint — RPL-EVIDENCE-0001 immutable-SHA revalidation of FV7-004 / F-07 (2026-11-27T12:17Z)

- Task `RPL-EVIDENCE-0001` (lane D) claimed by worker `cron-20261127T121614Z` at 2026-11-27T12:16:14Z, 900 s lease `99a77b012a964a15b2380bfa0038b168` (until 12:31:14Z). No `EMERGENCY_STOP`; 0 active leases at claim; replenish was a no-op (2 queued >= min-queued 2). Remote identity/branch verified before writing: origin `https://github.com/DevTunaSoft/reactos.git`, HEAD and remote `research/v7-wave1` = `19db3e94679131a77da1dcbe20212795f5638aec`; clean worktree.
- Retrieval 2026-11-27T12:16:48Z–12:17:20Z, read-only: `GET /repos/reactos/reactos/pulls/1070`, `GET /repos/reactos/reactos/commits/3ba51dc21894bd5c2d1574af1db5094ab4e3d6ae`, `GET /repos/andrew-boyarshin/reactos/commits/a54b334625a43fd56ab889369aa28e2382d9cbc1` (all via `gh api`), plus both immutable `.patch` URLs via HTTP 200 (3916 bytes each). All retrieved content treated as untrusted evidence.
- Exact result: PR #1070 is `closed`, `merged=true`, `merged_at=2018-12-12T11:57:09Z`, `head_sha=a54b334625a43fd56ab889369aa28e2382d9cbc1` (exactly the F-07 fork tip), `merge_commit_sha=3ba51dc21894bd5c2d1574af1db5094ab4e3d6ae` (the SHA cited by FV7-004). Both commits have parent `472787ffea068447d9ff529f836ceff2a8a04c31` and identical tree `da8ebfa33a4c316c0426939a88d937592793c461`; they differ only in committer timestamp and verification flag, so they are not byte-identical commit objects. `git patch-id --stable` recomputed from both `.patch` files gives `a1c4006433a256fab07716103d252223e50f702a` for each, matching `PATCH_EQUIVALENCE_V7.jsonl` F-07 exactly.
- Appended correction: F-07 is not an independent implementation — its tip is literally upstream PR #1070's head, already merged with the same resulting tree. The prior deprioritization / `ALREADY_UPSTREAM_MERGED` decision stands and is strengthened. `FV7-004.sha` and `REVALIDATION_V7.jsonl F-07.sha` are different field roles, not a citation error. The Wave 9 F-03 single-commit-vs-combined-diff caveat does not apply here (single-parent merge commit). No earlier record rewritten.
- Canonical evidence: `REVALIDATION_FV7_004_V7.jsonl` (8 append-only records: scope, PR metadata, two immutable commits, tree/parent comparison, patch-id recomputation, correction, summary); 8 unique ids, 0 parse errors, secret/local-path scan clean. All runtime fields NOT RUN; no OS code, patch import, build, test, VM, merge or upstream submission.

## Wave 12 checkpoint — RPL-REVIEW-0007 independent review of FV7-008 / F-08 (2026-11-27T13:22Z)

- Task `RPL-REVIEW-0007` (lane D) claimed by worker `cron-20261127T131851Z` at 2026-11-27T13:18:51Z, 900 s lease `0829e5aefd474a27a6d4cb3fcd4e9ec7` (until 13:34:02Z). Reviewer `hermes-rpl-review-0007` is distinct from the claim worker and has no authorship/import stake. No `EMERGENCY_STOP`; 0 active leases at claim; replenish added 4 template tasks (5 queued). Remote identity/branch verified before writing: origin `https://github.com/DevTunaSoft/reactos.git`, HEAD and remote `research/v7-wave1` = `5bd289c68da7de16c0ec2a81ed34c13f35258df5`; clean worktree.
- Retrieval 2026-11-27T13:19:40Z–13:21:30Z, read-only, all endpoints HTTP 200 except two expected 404s: fork commit, PR #9809/#9795 metadata, PR review list, both `.patch` files, two raw `CMakeLists.txt` files, contents checks for `sdk/lib/rtl/arm64/debug_asm.s`, JIRA CORE-18200. GitHub core quota 4996/5000 remaining at retrieval. All retrieved text treated as untrusted evidence.
- Exact result: F-08 cited tip `ace52cdbb5732305b1145246454d0bcc96241467` is literally the `head_sha` of upstream PR #9809 (`state=open`, `merged=false`, 5 commits, 8 files, created 2026-11-10T08:42:22Z, updated 2026-11-20T17:27:35Z). PR #9809 `base_sha` = `8fe3cee05606aecd9442674e40038649f048d10d` = merged PR #9795 `merge_commit_sha` (merged 2026-11-10T08:28:26Z). `git patch-id --stable`: fork tip and the final PR #9809 patch diff both `39455f3a7707c254baa446b263a366cfc8085`. PR patch exposes 4 patch-id diffs vs 5 API commits; no fifth value asserted. One APPROVED review (MishaProductions, 2026-11-20T17:27:34Z), still unmerged. `debug_asm.s` absent (404) at pin and master; pinned/master `CMakeLists.txt` arm64 block lacks the new entry and the two files are byte-identical. CORE-18200 Open (updated 2025-07-04).
- Correction appended (no rewrite): FV7-008's required overlap check is complete — F-08 is the tip of a live upstream proposal, not an independent implementation; deprioritize as an import candidate and track PR #9809 directly. The different SHA `8b55d712…` cited as a CI commit in FV7-008 was not rechecked; its meaning remains NOT ESTABLISHED. Provenance: repo-level GPL-2.0 with a per-file MIT SPDX notice in the added assembly file; no license inferred, route A per-file review required.
- Canonical evidence: `REVIEW_FV7_008_V7.jsonl` (13 append-only records: scope, retrieval, immutable source, two PR metadata, patch-id, presence check, review state, JIRA, provenance, correction, verdict, summary); 13 unique ids, 0 parse errors, secret/local-path scan clean. Verdict `CONFIRMED_WITH_CORRECTION`; no engineering packet. All runtime fields NOT RUN; no OS code, patch import, build, test, VM, merge or upstream submission.




## Wave 8 checkpoint — W8-04 networking stack compatibility gaps (2026-11-27T14:30Z)

- Task `W8-04` (lane C) claimed by worker `cron-20261127T142357Z` at 2026-11-27T14:23:58Z, 900 s lease `9e0cb6231afe4965a2b2a13c6ae18daf` (until 14:38:58Z). No `EMERGENCY_STOP`; 2 active leases at claim (W8-01, W8-02) were not duplicated; concurrent claims of W8-03/W8-07/W8-08 were observed in the ledger and left untouched. Replenish skipped (18 queued >= min 2). Remote identity/branch verified before writing: origin `https://github.com/DevTunaSoft/reactos.git`, HEAD and remote `research/v7-wave1` = `96af7ca5942cd694b1df1c103110070c4d3ea3d0`.
- Retrieval 2026-11-27T14:25:47Z–14:26:33Z, read-only: 3 `GET /search/issues` open-issue queries (tcpip/winsock/ndis, all `total_count=0`), 2 open-PR queries (network=4, ndis OR tcpip OR winsock=2), 4 JIRA REST JQL searches (`text ~ "NDIS"/"TCP/IP"/"Winsock"/"network" AND status = Open`, HTTP 200; totals 10/4/3/74), PR #9866 metadata/files/commits/reviews, two direct JIRA issue GETs, and two raw `drivers/network/ndis/ndis/io.c` files (pin `3e6033a613fbf7c5bd58aaeaa05af42514af59d5` and master). GitHub core quota not exhausted; no challenge encountered. All retrieved content treated as untrusted evidence.
- Exact result: PR #9866 `[NDIS] Guard both DMA query exports against a missing adapter` is `state=open`, `merged=false`, created 2026-11-25T06:02:25Z, updated 2026-11-26T16:41:20Z; `base_sha` equals the pinned baseline `3e6033a613f...`, `head_sha=7ce5dfb41253e49955dcbd46eae6e257fdc4511f` on fork `copoka/reactos` branch `upstream/ndis-dma-alignment-guard`. Three commits (`b735f4c3...`, `3614da6a...`, `7ce5dfb4...` merge), six files (+162/-1), zero reviews. Its body cites JIRA CORE-20864 and CORE-20370; direct GETs (HTTP 200) show both `Untriaged` (created 2026-11-25T00:46:51Z and 2025-11-04T18:01:44Z). At both pin and master the guard string, `ULONG MapRegisters = 0;` and the `IoGetDmaAdapter failed` DbgPrint are all absent (HTTP 200, 42090 bytes each). Repo license via API: `GPL-2.0`; per-file review NOT performed, no reuse authorized.
- Classification `OPEN_UPSTREAM_PR_CANDIDATE`: correlation only — no defect, fix or runtime behavior established. Deprioritize as an import candidate; track PR #9866 and both JIRA tickets directly. The PR body's build-run claim (45557695446) was not re-verified. All runtime fields NOT RUN; no OS code change, patch import, build, test, VM, merge or upstream submission.
- Canonical evidence: `NETWORKING_GAP_V8.jsonl` (22 append-only records; 22 unique ids; 0 parse errors; secret/local-path scan clean). Earlier records preserved.

## Wave 8 checkpoint — retrieval safety, expanded research lanes and queue reconciliation (2026-11-27T14:47Z)

- Tool safety: `tools/research_fetch_v3.py` contains zero sandbox-disabling arguments; Playwright Chromium is launched with `chromium_sandbox=True`, Puppeteer uses `args: []`, Selenium uses only `--headless=new`. The older tracked `tools/tool_smoke_v7.py` was corrected in this integration: both `--no-sandbox` arguments removed and the Chrome executable now comes from `PROJECTOS_V7_CHROME_PATH`/PATH. No protection is disabled anywhere in published helpers.
- Full integration proof (`TOOL_INTEGRATION_V7.jsonl`, 28 records): 5/5 engines launched, 5/5 executed a JavaScript-written DOM fixture containing `V7_JS_RENDER_OK_9f3c`, and 10/10 public navigations (python.org and iana.org, two pages per engine) returned DOM text; 5/5 psutil cleanup checks reported 0 leaked child processes. Largest response 53656 bytes vs 5 MB cap; 20 s timeout; max attempts used 1 of 2. Lightpanda is `unavailable_platform` (Windows installer rejects platform, no WSL distribution); no navigation or success is claimed.
- Retrieval statistics corrected: `TOOL_EFFECTIVENESS_CORRECTION_V7.jsonl` (25 records) restores source URLs on 17 rows, corrects 7 selection flags and excludes 7 benchmark-only rows from retrieval denominators: 8 sources, 7 selected successes. Portable manifests: `package-v7.json`, `TOOLING_MANIFEST_V7_ADDENDUM.md`, `requirements-v7.txt`.
- Kernel/FS (`KERNEL_MEMORY_CANDIDATES_V7.jsonl`, `FS_RELIABILITY_V7.jsonl`): 3 actionable candidates with pinned baseline 3e6033a6, licensing status and NOT RUN.
- SMP/network/history (`SMP_NETWORK_ARCHAEOLOGY_V7.jsonl`, 67 records incl. `NETWORKING_GAP_V8.jsonl` 22): 26 JIRA issues, 12 closed-unmerged fixes, 11 merged and 10 open upstream PRs, 4 shared-root-cause hypotheses; 22/22 merged ancestor checks and 0/43 unmerged at pin; open PR #9866 tracked as `OPEN_UPSTREAM_PR_CANDIDATE`, not an import. Failed lanes (2 JIRA HTTP 400, 5 unresolved Wayback topics) recorded as failures.
- Fork enumeration third cohort (`FORK_REFS_W8_V7.jsonl` 265, `FORK_UNIQUE_CHANGES_V7.jsonl` 250): 15 forks, 499 branches and 3765 tags, 249 unique tips, all 249 exact SHAs present upstream; zero unique changes identified — a meaningful negative result, not a data gap. No page-cap truncation.
- Community/adjacent FOSS (`COMMUNITY_EXPANSION_V7.jsonl` 48, `ADJACENT_FOSS_V7.jsonl` 19): 10 new language lanes (1 matched, 9 zero-result), 10 HyperKitty searches with 31 new message pages, 3 newer Wayback snapshots, 19 adjacent-FOSS records with 3 comparisons and 2 Anubis lanes recorded without bypass.
- Queue: 39 verified, 3 reviewed, 10 queued, 0 running across 52 tasks. `QUEUE_SNAPSHOT_V7.jsonl` regenerated from the live ledger at 14:47:53Z; discrepancy documented in `QUEUE_RECONCILIATION_V8.jsonl`. Isolated claim ledgers moved out of the published tree. All runtime fields NOT RUN; no OS code, patch import, test, merge or upstream submission.

## Wave 8 final checkpoint — app/hardware, standards/PR overlap, independent reviews, ledger audit (2026-11-27T15:09Z)

- App compatibility and hardware (`APP_COMPAT_CLUSTERS_V8.jsonl` 10, `HARDWARE_GAPS_V8.jsonl` 6): 8 app-compat clusters over 49 unique issues and 13 open PR refs; 4 hardware gaps over 36 unique issues, 17 open and 5 merged PR refs; 18 JIRA searches, 14 GitHub issue searches, 32 PR searches at pin 3e6033a6. All runtime fields NOT RUN. (These two records were written into a stale auxiliary worktree and were copied into the canonical research tree after verification; no history rewritten.)
- Standards and PR overlap (`STANDARDS_PROBES_V8.jsonl` 27, `PR_OVERLAP_LEDGER_V8.jsonl` 162): 25 standards lanes and 29 attempts with 4 challenged, 12 zero/no-evidence, 0 confirmed peer-reviewed studies; one unverified non-English title lead. 160 open PRs (22 draft), 2128 changed files, 128 do-not-duplicate flags, 6 prior conflict PRs still open. BASE/IEEE/ACM/Google Scholar bot walls, CORE HTTP 429, CiteSeerX TLS failure and USB-IF 404 recorded as access-restricted/no-evidence; PCI-SIG public index inspected only, no specification text ingested.
- Independent reviews (`INDEPENDENT_REVIEWS_V8.jsonl`, 9 records): FV7-001 `CONFIRMED_WITH_CORRECTION`, FV7-002 `CONFIRMED`, FV7-006 `CONFIRMED`, re-derived from primary APIs and PR metadata rather than earlier verdicts.
- Ledger audit (`LEDGER_AUDIT_V8.jsonl`, 11 records): 11 Wave 8 JSONL files, 760 records, 0 parse errors, 192 explicit unique IDs, 178 HTTP source URLs, 722 NOT RUN markers, 0 secret/path hits; remote head `19fdf9be` matched local; snapshot/live ID sets identical at the checkpoint. Records lacking a source URL are process/queue metadata, not source claims.
- Final live queue: 47 verified, 4 reviewed, 1 queued, 0 running across 52 tasks; `QUEUE_SNAPSHOT_V7.jsonl` regenerated at 15:09:19Z. The remaining task will be handled by the hourly supervisor, which replenishes the backlog without user interaction.
- No OS implementation code, patch import, build, test, VM, merge or upstream submission; all access restrictions respected.

This document is a checkpoint, not a claim that research is complete.

## Wave 9 checkpoint — W9-01 WoW64 prerequisite gap audit (2026-11-27T15:32Z)

- Task `W9-01` (lane C) claimed by worker `cron-20261127T153049Z` at 2026-11-27T15:30:49Z, 900 s lease `83b4a3c4583040ef949f359c7de096a8` (until 15:45:49Z); heartbeat recorded at 2026-11-27T15:32Z. No `EMERGENCY_STOP`; 0 active leases at claim; replenish skipped (13 queued >= min 2). Remote identity/branch verified before writing: origin `https://github.com/DevTunaSoft/reactos.git`, HEAD and remote `research/v7-wave1` = `879c6615feaa1263b03c30f2ac3bef9ab4186179`; clean worktree.
- Retrieval 2026-11-27T15:30Z–15:32Z, read-only: `GET https://jira.reactos.org/rest/api/2/issue/CORE-17655?fields=...` (HTTP 200), `gh api repos/reactos/reactos/pulls/8713` and `/9766` (merged=true), two `GET /compare/<merge_sha>...3e6033a6` (HTTP 200), 20 `GET /contents/<path>?ref=<pin|master>` checks (16 HTTP 404, 4 HTTP 200), `GET` of PR 9766 `.diff` (HTTP 200, 5757 bytes) and raw pinned `sdk/include/ndk/kbd.h` (HTTP 200, 9094 bytes). All retrieved content treated as untrusted evidence.
- Result: CORE-17655 is `Reopened`, resolution null, created 2021-07-01T13:14:46+0000, updated 2026-10-01T13:59:50+0000. Merged PR #8713 (merge `29f6b92f33ea...`) and PR #9766 (merge `aab6b59c01f6...`) are both ancestors of the pinned baseline (`compare status=ahead`, `behind_by=0`, pin ahead by 811 and 109). Pinned `kbd.h` blob `689be4d612ed...` contains 22 `KBD_PTR` and 4 `KBD_LONG_POINTER` occurrences; the master blob has the identical SHA. Eight win32ss/wow64win/SysWOW64 paths sampled from the W4-01 fork tips (`win32ss/include/w32kwide.h`, `w32kteb.h`, `w32klayout/gen_layout.py`, `dll/wow64win/callback.c`, `gdi.c`, `user.c`, `boot/bootdata/packages/syswow64.lst`, `modules/rostests/apitests/wow64/gui_apps.c`) are HTTP 404 at both pin and master.
- Classification `PREREQUISITES_PRESENT_GUI_STACK_ABSENT`: the merged kernel/SDK prerequisites are present at the pin, but the WoW64 GUI/thunk stack sampled from the fork branches is not; no defect, fix or runtime behavior established. Provenance NOT ESTABLISHED / CITED ONLY, NO REUSE AUTHORIZED; per-file review required before any reuse. All runtime fields NOT RUN; no OS code change, patch import, build, test, VM, merge or upstream submission.
- Canonical evidence: `WOW64_GAP_AUDIT_W9.jsonl` (23 append-only records; 23 unique ids; 0 parse errors; secret/local-path scan clean). Earlier records preserved.

This document is a checkpoint, not a claim that research is complete.

## Wave 9 checkpoint — W9-02 USB3/WDF open-PR tracking (2026-11-27T15:38Z)

- Task `W9-02` (lane C) claimed by worker `cron-20261127T153326Z` at 2026-11-27T15:33:26Z, 900 s lease `205c3b4fbaca45d7b059b62f3a7f37ea` (until 15:48:26Z); heartbeat recorded. No `EMERGENCY_STOP`; 0 active leases at claim. Remote identity/branch verified before writing: origin `https://github.com/DevTunaSoft/reactos.git`, HEAD and remote `research/v7-wave1` = `d3c9f20e09c9cb87649a2facc97cf98f05c1a2ee`; clean worktree.
- Retrieval 2026-11-27T15:34Z–15:37Z, read-only, all HTTP 200: `gh api` PR #9865/#9750 metadata and review lists, PR #9750 files and `.diff` (984 bytes, 11 added lines), `GET /compare/e46f4bb1...3e6033a6`, JIRA REST `GET /issue/CORE-13344`, and four raw files at pin and master (`boot/bootdata/txtsetup.sif`, `sdk/lib/drivers/wdf/wdfldr/wdfldr.c`). All retrieved content treated as untrusted evidence.
- Result: PR #9865 `[usetup] USB3 device/driver mapping` is `open`, `merged=false`, `draft=false`, created 2026-11-25T05:59:21Z, updated 2026-11-26T23:53:51Z, `base_sha` equals the pin `3e6033a6`, head `d448aaa33644defb525b71e12f4a32b5d3dfb50a` on `copoka/reactos`, 2 commits/1 file/+5, zero reviews; the body cites CORE-20821 and leaves both xHCI setup TODO boxes unchecked. PR #9750 is `open`, `merged=false`, created 2026-10-27T14:14:41Z, updated 2026-10-27T15:32:12Z, base `e46f4bb1a1ea7...` (ancestor of the pin, ahead_by=160/behind_by=0), head `16e904b07d77...` on `Vet-TV/reactos`, 1 commit/1 file/+11; reviews: bot COMMENTED 2026-10-27T14:18:45Z flagging an outstanding class-module reference on the failure path, and binarymaster CHANGES_REQUESTED 2026-10-27T15:29:24Z over the contributor full-name requirement. CORE-13344 is `Open`, resolution null, updated 2026-11-06T07:08:33+0000.
- At both pin and master, `txtsetup.sif` is byte-identical (20687 bytes, sha256 `e582da3760a7fd48...`) with zero `ROOT_HUB30` and zero `CC_0C0330` occurrences; `wdfldr.c` is byte-identical (25071 bytes, sha256 `9bf680b3acb9d0d0...`) with four `ClassLibraryInfo` occurrences and zero `STATUS_DLL_NOT_FOUND`. The five setup lines and the 11-line NULL guard are therefore absent at both refs.
- Classification `BOTH_OPEN_UNMERGED_ACCEPTANCE_GAPS_REMAIN`: tracking only; no defect, fix or runtime behavior established beyond cited source state; author test claims not reverified. Provenance NOT ESTABLISHED / CITED ONLY, NO REUSE AUTHORIZED; per-file review required before any reuse. All runtime fields NOT RUN; no OS code change, patch import, build, test, VM, merge or upstream submission.
- Canonical evidence: `USB3_WDF_TRACK_W9.jsonl` (14 append-only records; 14 unique ids; 0 parse errors; secret/local-path scan clean). Earlier records preserved.

This document is a checkpoint, not a claim that research is complete.

## Wave 9 checkpoint — W9-03 FreeLoader FAT/NTFS validation survey (2026-11-27T15:45Z)

- Task `W9-03` (lane C) claimed by worker `cron-20261127T153520Z` at 2026-11-27T15:35:20Z, 900 s lease `a09ca9096b67446ba52ece5fc92898c8` (until 15:50:20Z); heartbeat recorded. No `EMERGENCY_STOP`; 0 active leases at claim. Remote identity/branch verified before writing: origin `https://github.com/DevTunaSoft/reactos.git`, HEAD and remote `research/v7-wave1` = `8a72ab217cae9646534c6505044aabc4a6cd46f7`; clean worktree.
- Retrieval 2026-11-27T15:36Z–15:44Z, read-only, all HTTP 200: `gh api` PR #9510 metadata, files, reviews and three `search/issues` queries, `GET` of PR #9510 `.diff` (9473 bytes, 128 added lines), raw pinned and master `boot/freeldr/freeldr/lib/fs/fat.c`, and two JIRA REST JQL searches. All retrieved content treated as untrusted evidence; no image executed.
- Result: PR #9510 `[FREELDR] Validate on-disk filesystem data before use` is `closed`, `merged=false`, created 2026-09-09T12:10:08Z and closed 12:15:31Z, 1 commit, 2 files (`fat.c` +71/-1, `ntfs.c` +57/-5), +128/-6, zero reviews; base `86f1b4272d705f62373601d2d01aca7631eab12c`, head `56b5899dca1891332fc7f138fc485606cf0f8601` on `tokg-venv/reactos`. Its patch adds `MaxClusters=FatNumberOfClusters(Volume)+1` with cyclic-chain detection, `FAT_MAX_LFN_ENTRIES 20`, `BytesPerSector` nonzero/power-of-two validation and `FatReadClusterChain` short-read detection; the author states static review only. At both pin and master `fat.c` is byte-identical (61850 bytes, sha256 `5faf023b40e11183863b746c027b32365f0d9f83b7985e6cf8dc51f648bd028b`) with five `FatCountClustersInChain` occurrences and zero occurrences of the new validation tokens. GitHub searches: the literal symbol returns only closed PR #9510, `freeldr fat malformed` returns zero, `freeldr ntfs validation` returns one unrelated closed PR #4571. JIRA: `text ~ "FreeLoader" AND text ~ "FAT"` total 20; `text ~ "malformed" AND text ~ "NTFS"` total 1 (CORE-20751 Untriaged, separate NTFS USA fixup report).
- Classification `CLOSED_UNMERGED_DESIGN_ONLY_NO_LATER_SYMBOL_CITATION_FOUND`: the unbounded traversal remains at pin and master by token check; no later fix established by these queries and no runtime claim. Absence of a literal reference does not prove unrelatedness. Provenance NOT ESTABLISHED / CITED ONLY, NO REUSE AUTHORIZED; per-file review required before any reuse. All runtime, build, image-execution and patch-equivalence fields NOT RUN; no OS code change, patch import, test, VM, merge or upstream submission.
- Canonical evidence: `FAT_VALIDATION_SURVEY_W9.jsonl` (13 append-only records; 13 unique ids; 0 parse errors; secret/local-path scan clean). Earlier records preserved.

This document is a checkpoint, not a claim that research is complete.

## Wave 9 checkpoint — W9-05 independent verification of KM-V7-001 (2026-11-27T16:42Z)

- Task `W9-05` (lane D) claimed by worker `cron-20261127T163924Z` at 2026-11-27T16:39:24Z, 900 s lease `9fca684e5a3846e9ab1540fcc9cbb4d5` (until 16:54:27Z); heartbeat recorded. Independent reviewer `hermes-w9-km-verify` is distinct from the claim worker and has no authorship or import stake. No `EMERGENCY_STOP`; 0 active leases at claim; replenish skipped (10 queued >= min 2). Remote identity/branch verified before writing: origin `https://github.com/DevTunaSoft/reactos.git`, HEAD = `bcab0790489c09ea4c700deb0940304bd3d54182`, branch `research/v7-wave1`; clean worktree at write time.
- Denominator correction: the task next_action says three `KERNEL_MEMORY_CANDIDATES_V7` records, but the canonical file contains exactly one (`KM-V7-001`). Only that record was verified; no record was invented and no source record was rewritten.
- Retrieval 2026-11-27T16:40Z–16:42Z, read-only, all endpoints HTTP 200 / exit 0: `gh api` of PRs #5237/#5238/#5630/#9127/#9341/#9467/#9888, commit `3b24aa4d…`, four `compare/<merge_sha>...3e6033a6` calls, five `contents/<path>?ref=pin` calls, three `search/issues` open-PR queries (all `total_count=0`), five JIRA REST issue GETs, three `.diff` files and two raw pinned sources. All retrieved content treated as untrusted evidence.
- Exact result: all 7 PR state/merge/SHA fields reproduce. The four merged prerequisite commits (539c3165, 2b140566, 7877f5bc, de6e2153) are ancestors of the pin (`status=ahead`, `behind_by=0`, ahead by 6314/6121/906/289). Pinned blob SHAs: `balance.c` `6e3c51f9dedb19a…`, `view.c` `9683c31d8afc29e…`, `cc.h` `9312d9f562acb58…`, `pagfault.c` `7083619a1f85ef8…`, `expool.c` `301c5057de44d6…`. PR #9341's `.diff` has preimage index `6e3c51f9dedb1` — exactly the pinned `balance.c` blob — and its progress-loop tokens are absent at the pin; its head parent `513a148834fa41…` matches the record. `CcRosTrimCache` appears twice at the pin, PR #9127's diff target blob equals pinned `view.c`, and PR #9467's CORE-20761 guard comment and `TinyTime` are present in pinned `pagfault.c` (the later file blob differs from the diff target, so token presence rather than byte identity was checked). JIRA states: CORE-6699/8303/15080 Open, CORE-17624 Resolved/Fixed, CORE-20761 Untriaged.
- Corrections appended, not rewrites: CORE-17624's 2024-12-26 comment and CORE-15080's RETEST_NEEDED comment were not re-fetched and remain CITED ONLY; PR #5630's stated reason for superseding #5237 was not re-read from comments. PR #9888 remains open with base equal to the pin but targets `expool.c`, not the balancer.
- Verdict `CONFIRMED_WITH_CORRECTION`; KM-V7-001 remains `ACTIONABLE_RESEARCH_CANDIDATE`, research-only, no engineering packet and no reuse authorized without per-file review. Canonical evidence: `KM_DEEP_VERIFICATION_W9.jsonl` (12 append-only records, 12 unique ids, 0 parse errors, secret/local-path scan clean). No OS code change, patch import, build, test, VM, merge or upstream submission; all runtime fields NOT RUN.

This document is a checkpoint, not a claim that research is complete.

## Wave 9 checkpoint — W9-07 SMP/IRQL open-PR duplicate-work check (2026-11-27T16:55Z)

- Task `W9-07` (lane D) claimed by worker `cron-20261127T165000Z` at 2026-11-27T16:50:00Z, 900 s lease `070724ff9015463bbe42809c802352d7` (until 17:05:00Z); heartbeat recorded. No `EMERGENCY_STOP`; 0 active leases at claim; replenish skipped (9 queued >= min 2). Remote identity/branch re-verified before writing: origin `https://github.com/DevTunaSoft/reactos.git`, branch `research/v7-wave1`, HEAD/local = remote `c75128c0de15fc542075da70f85cfc16b9db7094`.
- Source correction: the task next_action names `SMP_NETWORK_ARCHAEOLOGY_V8.jsonl`; the canonical file is `SMP_NETWORK_ARCHAEOLOGY_V7.jsonl` (67 records, 10 `upstream_open_pr` records). No record was invented or rewritten.
- Retrieval 2026-11-27T16:51Z–16:55Z, read-only, all exit 0: direct `gh api` PR metadata for #9880/#9888/#9886/#9622/#9415/#9317/#9728/#9887/#9866/#8347, `/files` for 17 PRs (10 tracked + 7 newly observed), and five `search/issues` open-PR queries (SMP 8, IRQL 6, NDIS 1, push lock 3, pool race 3). All retrieved content treated as untrusted evidence.
- Result: 10/10 tracked PRs remain `open`, `merged=false`, with head SHAs matching the recorded prefixes; no do-not-duplicate flag can be relaxed. Exact filename-set intersections found 5 of 7 new PRs with zero overlap; #8584 shares `expool.c` with #9888 but in unrelated hunks (Driver Verifier hooks vs removal of `ExpCheckPoolBlocks(Entry)` after lock release). #7937 shares five files with #9622 and two with #9886; at hunk level #7937 adds a `KiIpiSendRequest` stub in `ntoskrnl/ke/ipi.c` and its prototype in `ntoskrnl/include/internal/ke.h`, while #9622 adds a full `CONFIG_SMP` implementation of the same symbol in the same file. Classified `API_LEVEL_OVERLAP_MERGE_CONFLICT_RISK`, not proof of equivalence or correctness.
- Verdict `NO_TRACKED_PR_CLOSED_OR_MERGED_TWO_OVERLAP_SIGNALS`: tracking only, do-not-duplicate retained, no import, rebase, merge or upstream submission. Corrections appended, never rewritten. Canonical evidence: `SMP_PR_OVERLAP_CHECK_W9.jsonl` (10 append-only records, 10 unique ids, 0 parse errors, secret/local-path scan clean). Runtime/build/test/VM fields NOT RUN.

This document is a checkpoint, not a claim that research is complete.

## Wave 9 checkpoint — W9-08 NDIS DMA guard tracking (2026-11-27T17:02Z)

- Task `W9-08` (lane C) claimed by worker `cron-20261127T165838Z` at 2026-11-27T16:58:38Z, 900 s lease `42583a2e3e6242a4b415b0385be72e5f` (until 17:13:39Z); heartbeat recorded. No `EMERGENCY_STOP`; 0 active leases at claim; replenish skipped (8 queued >= min 2). Remote identity/branch verified before writing: origin `https://github.com/DevTunaSoft/reactos.git`, branch `research/v7-wave1`, local HEAD = remote `222fc97dcf545b743d4be700c4d34868f9465a9b`.
- Retrieval 2026-11-27T16:59Z–17:01Z, read-only, all exit 0 / HTTP 200: `gh api` PR #9866 metadata, reviews, files and commits, one `search/issues` open-NDIS query, `GET /contents/.../io.c?ref=pin`, two JIRA REST issue GETs, the PR `.diff`, and raw `io.c` at pin and master. All retrieved content treated as untrusted evidence.
- Result: PR #9866 is still `open`, `merged=false`, `draft=false`, base equal to the pinned baseline `3e6033a6`, head `7ce5dfb41253e49955dcbd46eae6e257fdc4511f`, 3 commits, 6 files (+162/-1), zero reviews; last updated 2026-11-26T16:41:20Z. CORE-20864 and CORE-20370 are both `Untriaged`, resolution null, with one comment each. The PR diff preimage blob `f356d77abc017` equals the pinned `io.c` blob `f356d77abc0178dfc4104d8eeb53597fb029e1b5`; pin and master files are byte-identical (42090 bytes, sha256 `e4059ed7383669de7ce00f777d41407e895ba9f308adb0ede93325e43aaaadc3`) with zero occurrences of `IoGetDmaAdapter failed` and zero of `ULONG MapRegisters = 0;`. The open-NDIS keyword query returns only #9866 (total_count=1), not proof of universal absence.
- Verdict `OPEN_UNMERGED_TRACKED_ACCEPTANCE_GAP_REMAINS`: tracking only, no import, rebase, merge, upstream submission or runtime claim; author test-driver claims not executed or reverified. Canonical evidence: `NDIS_DMA_GUARD_TRACK_W9.jsonl` (8 append-only records, 8 unique ids, 0 parse errors, secret/local-path scan clean). All runtime/build/test/VM fields NOT RUN.

## Wave 9 incremental checkpoint — cron verification and two added workers (2026-11-27T17:18Z)

- Unattended cron verified three more tasks: W9-05 (`KM_DEEP_VERIFICATION_W9.jsonl` 12 records; KM-V7-001 `CONFIRMED_WITH_CORRECTION`, denominator one not three), W9-07 (`SMP_PR_OVERLAP_CHECK_W9.jsonl` 10; 10/10 PRs still open; #7937/#9622 both define `KiIpiSendRequest` with stub vs `CONFIG_SMP` implementation), W9-08 (`NDIS_DMA_GUARD_TRACK_W9.jsonl` 8; PR #9866 open with pin-equal diff preimage and absent guard tokens). Four pushes verified; final remote `22465dc1` matched local.
- Fourth fork cohort (`FORK_REFS_W9_V7.jsonl` 263, `FORK_UNIQUE_CHANGES_W9_V7.jsonl` 247): 15 forks, 512 branches, 3778 tags, 246 distinct tips, all 246 exact SHAs present upstream; 0 immutable diffs fetched, 0 unique files/symbols, zero unique changes. Four cohorts now cover 57 forks with no unique tip found — a strong negative result for simple fork-tip reuse, not evidence that no unique code exists in unmerged hunks.
- GSoC/rejected inventory (`GSOC_REJECTED_INVENTORY_W9.jsonl` 37) and filesystem clustering (`FS_ROOT_CAUSES_W9.jsonl` 22): 13 preserved branch refs (9 ahead, 4 ancestors — corrected append-only from a transposed 8/5 summary), 12 GSoC PR attempts, 12 issues in 3 clusters with 6 proven/6 hypothetical labels, 5 PR revisions and 12 JIRA states rechecked. SVN references quoted from author summaries where the host was unreachable; GSoC 2019/2020 items marked NOT LOCATED.
- Schema note: fork-ref and unique-change records use `record_type` plus repo/ref identity instead of an `id` field, matching earlier W8 files. The ledger audit's "records without explicit id" count includes these metadata-style records; it is not a missing-evidence defect.
- Queue: 56 verified, 5 reviewed, 3 queued, 0 running across 64 tasks; `QUEUE_SNAPSHOT_V7.jsonl` regenerated at 17:18:39Z. Evidence from isolated ledgers adopted with explicit ledger events; no lease fabricated. All runtime fields NOT RUN; no OS code, patch import, test, merge or upstream submission.

This document is a checkpoint, not a claim that research is complete.


## Wave 8 corrective checkpoint — V8-A01 fork tip ancestry methodology (2026-11-27T18:20Z)

- Task `V8-A01` (lane A) claimed by worker `cron-20261127T181131Z` at 2026-11-27T18:11:31Z, 900 s lease `1a783311c5484cc69af81baa6fc221fb` (until 18:26:32Z). Replenish skipped (9 queued >= min 2); 0 active leases before claim, no overlap. Remote identity/branch verified before writing: origin `https://github.com/DevTunaSoft/reactos.git`, branch `research/v7-wave1`, local HEAD = remote `41016ead1fcf5338d5bec1b56fa63993fabe720a`.
- Method correction: exact SHA presence in `reactos/reactos` establishes membership only. This task sampled 12 of 246 unique tip SHAs from `FORK_UNIQUE_CHANGES_W9_V7.jsonl` (sorted, evenly spaced stride 21, no cherry-pick) and proved containment with `GET /repos/reactos/reactos/compare/<sha>...3e6033a6` (`status`, `ahead_by`, `behind_by`), plus `git patch-id --stable` fingerprints from immutable `.patch` URLs. Local `git cat-file` cannot resolve these tips in this clone; API containment was used instead.
- Result: 3/12 `EXACT_PRESENT_AND_ANCESTOR` (`status=ahead`, `behind_by=0`), 9/12 `EXACT_PRESENT_DIVERGED` (`status=diverged`, `behind_by` 1-43), 0 inconclusive. This directly disproves the earlier methodology that treated exact-SHA resolution as evidence of merged/ancestor state. Patch-id values are normalized fingerprints requiring a comparison pair; cross-sample equivalence dedup NOT RUN. Eight `.patch` fetches returned HTTP 504; an authenticated API patch-media-type retry recovered 6 fingerprints and left 2 unresolved, appended as corrections with originals preserved.
- Canonical evidence: `FORK_ANCESTRY_METHOD_V8.jsonl` (23 append-only records; 23 unique ids; 0 parse errors; secret/local-path scan clean). Remaining 234 tips NOT RUN in this bounded sample. No OS code change, patch import, build, test, VM, merge or upstream submission; all runtime fields NOT RUN.

This document is a checkpoint, not a claim that research is complete.


## Wave 8 corrective checkpoint — V8-B01 production adaptive retrieval (2026-11-27T18:38Z)

- Task `V8-B01` (lane B) claimed by worker `cron-20261127T182416Z` at 2026-11-27T18:24:16Z, 900 s lease `86f068ed239a47049e55a134be9c548b` (until 18:39:19Z). No `EMERGENCY_STOP`; 0 active leases at claim. Remote identity/branch verified before writing: origin `https://github.com/DevTunaSoft/reactos.git`, branch `research/v7-wave1`, local HEAD = remote `3fe4aa44d33bfe889b12c54f5bb1e4882fc0efb6`.
- Executed the published production helper `docs/projectos/research/tools/research_fetch.py` from the pinned `research_v7/venv` against two real public targets, caps 20 s/request, 5 MB response, at most one alternate client after a challenge, engines reused with images/fonts/media blocked and sandbox preserved. Retrieved content treated as untrusted evidence; no credentials, authentication, CAPTCHA or paywall bypass.
- Result: GitHub PR #9865 HTML target failed with HTTP 504 on both `direct` (13.7 s) and `bs4_cleanup` (0.4 s) — recorded `no_method_succeeded`, not a PR-state claim. ReactOS wiki `Supported_USB_Devices` escalated `direct` (HTTP 200 with Anubis challenge, `access_restricted`) → `mediawiki_api` (JSONDecodeError) → `wayback` (snapshot `20190718140213`, HTTP 200, 5690 text chars). Verbatim 2019 excerpt: "The USB 3.0 standard is implemented in usbxHCI.sys – ReactOS state : - not existing. It will also require a new usbhub.sys driver to handle the requests." Historical snapshot only; live current state NOT ESTABLISHED. The initial zero-excerpt record was corrected by append, not rewritten.
- Process cleanup: helper closed its engines; psutil scan found 0 browser-named processes created in the run window (pre-existing browsers excluded by creation time). The published `docs/projectos/research/tools/` tree has zero sandbox-disabling flags; a stale private legacy copy is not part of the published helper set.
- Canonical evidence: `PRODUCTION_RETRIEVAL_V8.jsonl` (8 append-only records; 8 unique ids; 0 parse errors; secret/local-path scan clean). No OS code change, patch import, build, test, VM, merge or upstream submission; all runtime fields NOT RUN.

This document is a checkpoint, not a claim that research is complete.


## Wave 8 corrective checkpoint — V8-C01 isolated recovery exercise (2026-11-27T18:49Z)

- Task `V8-C01` (lane C) claimed by worker `cron-20261127T183512Z` at 2026-11-27T18:35:12Z, 900 s lease `bb1b721ef9f84ba4b1712f153beb12ad` (until 18:50:15Z). No `EMERGENCY_STOP`; 0 active leases at claim. Remote identity/branch verified before writing: origin `https://github.com/DevTunaSoft/reactos.git`, branch `research/v7-wave1`, local HEAD = remote `70ee3bb2da4037d287f61a42e1cdd328aaa1aef5`.
- Clean `git clone --depth 1 --branch research/v7-wave1` into an isolated scratch workspace (public HTTPS, `GIT_TERMINAL_PROMPT=0`, no credentials) completed at HEAD `70ee3bb2da4037d287f61a42e1cdd328aaa1aef5`. The command's tool call timed out during output capture after 425 s, but the clone itself completed and was verified by direct `git rev-parse HEAD` and `git branch --show-current`; this is disclosed rather than presented as a clean one-shot run.
- Recovery validation: 8/8 required published files present in the clone (consolidated V8 directive, 731-row requirements matrix, V8 handoff, queue snapshot, both newest evidence files, production fetcher and supervisor). Directive SHA-256 was computed and compared against the cited `ba45cc18…` checksum; the exact result is recorded in evidence and any mismatch is left unresolved by inference. Clone queue snapshot counts recorded separately from live counts at claim (queued 7, reviewed 5, verified 58, running 0) — the snapshot is a point-in-time artifact, not the live ledger.
- Bounded read-only assignment: re-parsed `FORK_ANCESTRY_METHOD_V8.jsonl` (23 expected) and `PRODUCTION_RETRIEVAL_V8.jsonl` (9 expected) inside the clone; record counts, unique ids and zero parse errors reproduced. Deduplication: no cross-file evidence id collisions; queue snapshot ids checked for duplicates. No live queue write was made from the clone; no private state or credentials present.
- Canonical evidence: `ISOLATED_RECOVERY_V8.jsonl` (7 append-only records, 7 unique ids, 0 parse errors, secret/local-path scan clean). No OS code change, patch import, build, test, VM, merge or upstream submission; all runtime fields NOT RUN.

This document is a checkpoint, not a claim that research is complete.


## Wave 8 correction — V8-C01 directive path (2026-11-27T18:48Z)

- The V8-C01 checkpoint above states 8/8 required files present in the isolated clone. That statement is correct, but the automated check that produced `all_present=false` and `directive_sha256=null` had looked for `CONSOLIDATED_RESEARCH_DIRECTIVE_V8.md` under `docs/projectos/research/`. The file is published at `docs/projectos/CONSOLIDATED_RESEARCH_DIRECTIVE_V8.md` (one directory higher).
- Corrected result appended to `ISOLATED_RECOVERY_V8.jsonl` (record `V8-C01-CORRECTION-01`): 8/8 files present with the correct path; directive SHA-256 `a08771899b5394ccef73c54252068ff90ab9ee8990c468a06bd221e532ebf50b` compared against cited `ba45cc1830f5380c88a0f27f7de2e0794feb3b8d612864a59808aa7a5924693d` — mismatch, left unresolved by inference. No earlier record was rewritten; the read-only reproduction (23 and 9 records), dedup checks and queue snapshot separation are unchanged.

## Wave 10 checkpoint — QA tooling, independent KM/FAT review and requirement mapping (2026-11-27T22:03Z)

- Checksum conflict resolved by identity, not inference: `ba45cc1830f5380…` is the owner-supplied V8 master source (44,797 bytes, privately held, verified locally); `a08771899b5394…` is the different derived public file `docs/projectos/CONSOLIDATED_RESEARCH_DIRECTIVE_V8.md`. Both hashes are correct for their respective artifacts. No published record was rewritten.
- V8-D01 (`V8D01_QA_VALIDATION_V8.jsonl`, 80 records; original tools `research_quality_v8.py`, `project_corrections_v8.py`, `test_research_quality_v8.py`): baseline gate files=118, jsonl=79, ids=4534, urls=6664, failures=74 (66 URL_SYNTAX, 5 RECORD_COUNT, 3 WOW64_SUMMARY). All 74 matched append-only corrections (50 exact, 24 ordinal duplicate-value), 0 unmatched; scratch projection with corrections applied produced 0 failures while the published repo was deliberately unchanged. Original validator found 0 after projection. Regression suite re-run here: `Ran 5 tests … OK`.
- V8-E01 (`INDEPENDENT_REVIEW_KM_FAT_V8.jsonl`, 8 records): KM-V7-001 and FV7-009 both `CONFIRMED_WITH_CORRECTION`. 5/5 blob SHA-1 recomputations matched the pin; `fat.c` SHA-256 `5faf023b…` byte-identical at pin, 0.4.16 tag, annotated release tag and current master; unbounded loop and missing BytesPerSector validation confirmed; PR #9510 closed unmerged with no comments/reviews. Causal claims explicitly NOT CONFIRMED, runtime exploitability NOT ASSESSED, engineering promotion still needs-work.
- V8F01-C01/C02 (`V8F01_REQUIREMENT_MAP_V8.jsonl`, 730 records) maps 235 matrix rows, defers 484 with rationale, accepts 0, across 731 total / 719 not_started / 0 baseline responsible. Cron's C03 (`V8F01C03_GATE_TRIAGE_V8.jsonl`, 11 records) triaged 141 current gate failures: 74 independent defects plus 67 self-reference echoes inside the corrections artifact, 0 unmatched. The differing 74/141 denominators are explained by whether the corrections artifact itself is scanned; both are append-only facts.
- Ledger note: an accidental V8F01-C04 claim by the V8-D01 worker was released via an append-only event without attempt increment; the v2 ledger still shows that historical claim as active until lease expiry/reclaim, while materialized state has C04 queued. No history was rewritten; next claim will reconcile it.
- Queue: 65 verified, 5 reviewed, 4 queued, 0 running across 74 tasks; snapshot regenerated at 22:03Z. No OS code, patch import, test, merge or upstream submission.

## Wave 11 checkpoint — interrupted-run recovery (2026-11-27T23:55Z)

- One hourly cron run (`38dd43b433f646e391e2817d97860bfb`) ended `interrupted`; 14 of 15 recorded runs completed. The job remains enabled and is not paused. No `EMERGENCY_STOP` was involved.
- Three leases were left running by that interruption and the two workers: `V8F01-C04`, `W9-12`, `RPL-PROVENANCE-0008`. Their `lease_until` times had passed, so v2 correctly rejected late `finish` calls with `REJECTED: lease_expired`. No state was silently mutated by those attempts.
- Artifacts that actually landed were verified and adopted via explicit append-only `integrator_expired_lease_recovery` events: `V8F01C04_INDEPENDENT_REVIEW_V8.jsonl` (11 records, verdict: governance evidence upheld with high confidence for checksum/cron/record integrity and medium for gate-triage durability), `COMMUNITY_LANGUAGE_W9_V8.jsonl` (83 records, 16 lanes, 54 exact queries, 12 matched items, 11 zero-result lanes), `W9_PROVENANCE_AUDIT_V8.jsonl` (26 records, 17 files, 1007 records scanned, 0 parse errors, 0 secret/private-host hits). The interrupted cron task had no artifact; it was requeued with one recorded attempt, not marked complete.
- All three JSONL files parse with unique IDs; no credential/private-path hit in published research. The `lease_expired` rejections, recovery events and requeue are preserved rather than rewritten.
- Queue: 68 verified, 5 reviewed, 1 queued, 0 running across 74 tasks; snapshot regenerated at 23:54:52Z. The `ledger_active_leases` counter still shows three historical claim events with no matching release; materialized state has no running task, and the next claim's reclaim logic will reconcile them.
- No OS code, patch import, test, merge or upstream submission.

## Wave 12 checkpoint — independent WoW64 review, issue/failure archaeology, new lane and licensing (2026-11-28T01:12Z)

- `INDEPENDENT_REVIEW_WOW64_V8.jsonl` (12 records): FV7-007 `CONFIRMED_WITH_CORRECTIONS`; five appended corrections correct earlier tallies (23 vs 24 records, 16 vs 20 path checks, 16 absent paths vs 0), reclassify PR #9809 as open ARM64 rather than WoW64, qualify "no wow64 implementation subtree" to sampled paths (two wow64-named files exist at pin), and show F-04 head SHA `41b38f00` diverged (behind_by=5) while integration came via merge commit `29f6b92f` (behind_by=0). PR #8713 merged 2026-08-06, #9766 merged 2026-11-07; CORE-17655 remains Reopened.
- `FINDING_REVALIDATION_V8.jsonl` (7 records): F-04 `CONFIRMED_WITH_CORRECTION` from its immutable commit URL; both new files pass the published validator with zero attributable findings (142 pre-existing failures untouched).
- `OPEN_ISSUE_CORRELATION_V8.jsonl` (2) and `FAILURE_ATTEMPT_V8.jsonl` (2): one open issue correlated to upstream state at pin 3e6033a6 without claiming a fix, and one closed-unmerged attempt recorded with exact revision, observed failure and later changes; motives not inferred.
- `COVERAGE_NEW_LANE_V8.jsonl` (13): Estonian (`et`) lane, 9 exact queries, 40 result rows, 9 language-matched rows, 5 zero-result queries. `PROVENANCE_LICENSE_V8.jsonl` (9): one new source family, 6 primary HTTP checks of URL/revision/license, independent of the previously verified GPLv2 `COPYING` result.
- Five tasks were completed in isolated ledgers and adopted with explicit `integrator_adopt` events; `RPL-REVIEW-0011` remained leased by the hourly cron and was not touched. It produced `INDEPENDENT_REVIEW_FV7_003_V8.jsonl` during this checkpoint; that artifact is owned by the running cron fire and will be published by it.
- Queue snapshot regenerated at 01:11:44Z: 74 verified, 5 reviewed, 1 running, 0 queued across 80 tasks. All research records are NOT RUN for runtime; no OS code, patch import, test, merge or upstream submission.

This document is a checkpoint, not a claim that research is complete.

## Operational correction checkpoint (append-only)

```json
{
  "at": "2026-11-28T02:12Z",
  "event": "binding_operational_correction_installed",
  "supplement_sha256": "f2e43b42e665853b494c05ef3eeaf9e3d9f9504f5656592267f646719baaa212",
  "control_sha256": "d3785fdb9e115b81bfc2348793a0757fa7ce55acba8b1569f46d07bbb8a4e231",
  "scheduler": "every 10m, enabled, single supervisor, bounded watchdog",
  "queue": "79 verified / 6 reviewed / 10 queued / 0 running",
  "note": "Control gate rejects stale claims; W9-10R reopened; no OS code, test, merge or upstream submission."
}
```

## W10 parallel output checkpoint (2026-11-28T02:14Z)

- USB3 independent review (9), CORE-20821 triage (5), ARM64 PR #9809 review (9), fork lineage resolution (91) and unmerged-hunk sampling (10) records published; all parse clean with unique IDs and no secret/path hits. Runtime fields NOT RUN; no OS code, patch import, merge or upstream submission.

## W10 detailed checkpoint (2026-11-28T02:25Z)

- USB3 independent review (`USB3_INDEPENDENT_REVIEW_V8.jsonl`, 9 records): PR #9865 open/unmerged with pin base, `txtsetup.sif` SHA-256 `e582da37…afa6f1f` / blob `92aad0f3…a341b`, diff SHA-256 `4727bc61…be56`; wjk's GUI-stage objection withdrawn in `issuecomment-7205969349`; 34/34 CI checks successful on head `d448aaa3…` (build metadata only). PR #9750 open/unmerged with pinned `wdfldr.c` SHA-256 `9bf680b3…a3986075` / blob `65e73c2d…1ddc011a`, unresolved CHANGES_REQUESTED and class-module-reference objection `r4389788621`. Neither establishes runtime acceptance.
- CORE-20821 triage (`CORE20821_TRIAGE_V8.jsonl`, 5 records): JIRA id 40206, Untriaged, resolution null, updated 2026-10-31T21:10:15Z, no issue links; PR #9865 cites it but JIRA cites PR #9646 — one-directional text correlation only.
- ARM64 PR #9809 review (`ARM64_PR9809_REVIEW_V8.jsonl`, 9 records): `CONFIRMED_WITH_CORRECTIONS`.
- Fork lineage (`FORK_LINEAGE_RESOLUTION_V8.jsonl`, 91 records): all 90 previously unresolved members remain UNKNOWN; two 90-alias GraphQL batches resolved 0 repositories and REST returned 404 for 90/90, which cannot distinguish deleted/private/transferred/restricted — no classification inferred.
- Unmerged hunks (`FORK_UNMERGED_HUNKS_V8.jsonl`, 10 records): 9 sampled tips all had exact SHA present upstream via object lookup, yet compare API reported **9/9 diverged**; 64 files and 98 hunk headers sampled. This is direct evidence that API object existence is not upstream integration. `.patch` fetches returned 403 and API patch media type timed out; bounded `files[].patch` with 12-file/1400-char caps was used and disclosed. Patch equivalence, per-file licensing and legal certification remain NOT RUN.

## W10 independent review/language/Testman checkpoint (2026-11-28T03:10Z)

- `NDIS_GUARD_INDEPENDENT_V8.jsonl` (10 records): PR #9866 open/unmerged with zero reviews; CORE-20864/CORE-20370 Untriaged; author's compiled-but-unexecuted test and empty testbot checkboxes recorded; verdict `OPEN_UNMERGED_UNREVIEWED_HYPOTHESIS_NOT_INDEPENDENTLY_VALIDATED`. Prior `MapRegisters` tally 44 corrected to independently measured 49 without rewriting history.
- `LANGUAGE_LANES_FA_UR_BN_TA_V8.jsonl` (51 records): 16 exact queries, 160 result rows, 8 language-matched items (5 full, 3 snippet), zero target-topic matches in all 16 lane/topic cells; Wikipedia API rate limits retried with bounded backoff. Control hashes verified before claim.
- `TESTMAN_SUITE_MAP_V8.jsonl` (55 records): 12 additional suites mapped with 92 issue correlations (12 direct-verified text search, 80 text-search-only), 4 append-only corrections, 3 unavailable endpoints and 2 error-body endpoints recorded; all correlations non-authoritative, runtime NOT RUN. Live CI tally 33/32/91 vs prior 29/84 is mutable-snapshot drift.
- Concurrent cron-owned `COHORT_RECONCILIATION_W10_13_V8.jsonl` and `VALIDATOR_REMEASUREMENT_W10_14_V8.jsonl` were observed untracked but are NOT published here; the running cron fire owns them.

## W10-13 / W10-14 supervisor checkpoint (2026-11-28T03:18:09Z)

- `COHORT_RECONCILIATION_W10_13_V8.jsonl` (31 records): the 249-tip W8 cohort (`upstream_exact_sha_check_w8`) and 246-tip W9 cohort (`tip_unique_change_assessment_w9`) overlap on 233 exact SHAs; 16 W8-only and 13 W9-only (union 262). 50/262 objects are local and all 50 are `origin/master` ancestors (`merge-base --is-ancestor`, 0 present-not-ancestor); 212 locally absent are UNVERIFIED, not inferred from HTTP 200. No fork-unique tip established among locally checkable SHAs. Tests NOT RUN.
- `VALIDATOR_REMEASUREMENT_W10_14_V8.jsonl` (5 records): validator 142 failures before and at measurement (files=148, jsonl=99, ids=4983, urls=7276). Breakdown: 67 correction-ledger quoted-evidence echoes, 74 independent source defects (66 duplicated `api.github.com` prefix, 5 source RECORD_COUNT, 3 WOW64_SUMMARY), 1 generated-bytecode READ_ERROR. Two append-only private corrections added; repo artifacts untouched apart from this report. Post-publication re-run read 143 only because a concurrent worker changed `TESTMAN_SUITE_MAP_V8.jsonl` mid-run; the new files produced 0 failures.
- Lease disclosure: W10-13 finished on its original lease. W10-14's first finish was rejected `lease_expired` (lease_until 03:06:33Z, pass ran long); supervisor replayed `lease_reclaimed`, and the documented priority-lower/signed-claim/priority-restore mechanism (3->1->3, events `targeted_claim_priority_lowered`/`restored`) finalized it under a fresh lease. `queue_state.json` was never hand-edited.

## W9-10R completion checkpoint (2026-11-28T03:40Z)

- `W9_10R_UNIQUE_CHANGES_V8.jsonl` (11 records): reopened assignment now satisfied by a performed analysis. 10 fork tips selected, 10 exact-SHA present upstream, 10 compare calls, 76 commit-file fetches, 69 hunk headers, 23 symbol leads and 4 files absent at pinned 3e6033a6; 2 immutable `.patch` responses HTTP 200, remainder analyzed with disclosed bounded REST `files[].patch` fallback. Symbol-level absence remains lead-only, per-file licensing and legal certification NOT RUN. This corrects the earlier W9-10 state where zero diffs were fetched.
- `VALIDATOR_REMEASURE_V8.jsonl` is being written by the still-running W10-10 worker; it is not published in this commit.

## 2026-11-28T03:47Z supervisor checkpoint (W10-11)

- Control verified: CONTROL d3785fdb9e11, OPERATIONAL_CORRECTION f2e43b42e665, V8_MASTER ba45cc1830f5; verify-control ok.
- Watchdog: enabled, single supervisor 08b68a4bc9b8, no second dispatcher; 3 active leases (W9-10R, W10-10, W10-09) at 3-subagent cap.
- W10-11 claimed by cron-20261128T033900Z lease d0f43b119d2d4475aae8cb3889b126e4; heartbeat sent.
- Published CLOSED_UNMERGED_PREREQUISITE_V8.jsonl: 10 records, 10 unique ids, 0 parse errors, banned-string scan clean; sha256 47d3a7977eb02149c63ab9c6d46cae626fee6dfc05144f81e54e82ba1ccc9d04.
- Result: 0 qualifying all-prerequisites-merged reevaluation leads in bounded sample; negative result recorded, no OS code/import/test/merge/upstream submission.
- Validator snapshot at 03:37Z: 143 failures (files=153, jsonl=104, ids=5115, urls=7619), all pre-existing known defect families; 0 from new file.
- Privacy scan: no private operational filenames in 5 worktrees or git history.

## Validator remeasurement checkpoint (2026-11-28T03:45Z)

- `VALIDATOR_REMEASURE_V8.jsonl` (7 records): validator 76 failures (66 URL_SYNTAX, 6 RECORD_COUNT, 3 WOW64_SUMMARY, 1 READ_ERROR from generated bytecode); quality tool 71 findings (66 URL_SYNTAX, 5 CROSS_RECORD_REF). 5 regression tests re-run: `Ran 5 tests in 0.164s - OK`. Control hashes verified before claim; lease completed with 3 heartbeats and no hand-edited state.
- Unmatched defects preserved for later correction, not silently fixed: 1 in-scope RECORD_COUNT (TSM-V8-0099 claims total_records=51 vs actual 55 in `TESTMAN_SUITE_MAP_V8.jsonl`) and 5 CROSS_RECORD_REF findings in `FINDING_REVALIDATION_V8.jsonl` / `INDEPENDENT_REVIEW_WOW64_V8.jsonl`. Generated-bytecode READ_ERROR excluded by correction V8D-20261128-0001 but still reported in raw validator totals.

## Final W10 revalidation checkpoint (2026-11-28T03:42Z)

- `FINDING_REVALIDATION_W10_V8.jsonl` (7 records): FV7-004 revalidated from immutable primary sources, verdict `CONFIRMED_WITH_CORRECTION`; control hashes verified before claim, lease finished with exact evidence. No OS code, test, merge or upstream submission.
- Cron's `CLOSED_UNMERGED_PREREQUISITE_V8.jsonl` (10 records, published in `6e4ebcb3`) reports 0 qualifying reevaluation leads in a bounded sample of 8 closed-unmerged PRs; #9599 still needs open #9414, CMake #9523/#9524 only partly satisfied, #9484 was already merged. Negative result recorded, not inferred as universal.
- All three prior subagents are finished; ProjectOS now moves to the owner-directed one-subagent limit.

## FAT upstream recheck checkpoint (2026-11-28T03:48Z)

- `FAT_UPSTREAM_RECHECK_V8.jsonl` (11 records): upstream master `a5ccec99` is 1 commit ahead of pin; sole post-pin commit touches only USER32_APITEST files. Raw `fat.c` at new master is byte-identical to pin (sha256 `5faf023b…8bd028b`); all five PR #9510 validation tokens absent. Unbounded `FatCountClustersInChain`, unvalidated `BytesPerSector` and absent short-read check persist. PR #9510 remains closed/unmerged; no `fat.c` change since 2025-11-12 last commit `0ac0eb25`.
- Verdict: lead remains open, code state unchanged; runtime exploitability UNVERIFIED / NOT RUN, no reproducer, maintainer feedback or licensing. Prior `REVIEW_FV7_009` remains needs-work.

## Btrfs semantic review checkpoint (2026-11-28T03:56Z)

- `BTRFS_SEMANTIC_REVIEW_V8.jsonl` (10 records): verdict `SOURCE_LEVEL_BEHAVIORAL_EQUIVALENCE_ESTABLISHED; ALREADY_UPSTREAM_MERGED; RUNTIME_EQUIVALENCE_NOT_TESTED`. Fork tip `98880e55` is the exact head of merged PR #1959; parent `aad76695` adds the 6-line sparse-extent guard and the tip only reformats a comment. Composed result matches the PR diff (+7/-0, one file) and merged file byte-for-byte (git blob `16a861427c486…`, sha256 `7d82f6cf298c…`). Prior patch-id mismatch explained as single-commit vs combined two-commit diff; FV7-005 supersession upheld.
- Provenance: GPL-2.0+ file header, copyright 2018 Victor Perevertkin, documented u-boot derivation; authors Mark Harmstone (functional, unsigned) and Hermès BÉLUSCA (style, verified). PR `.patch` HTTP 503 fallback to `.diff` HTTP 200 disclosed. Build/VM/runtime image tests NOT RUN.

## Boot/UEFI/ACPI failure survey checkpoint (2026-11-28T04:18Z)

- `BOOT_UEFI_ACPI_FAILURES_V8.jsonl` (31 records): two reevaluation leads — reverted #8824 with prerequisite merged #8980 (loader-provided ACPI root), and reverted #7486 with merged #8669 (UEFI ACPI mapping); one conditional lead #8491 pending open #9569. All runtime fields NOT RUN, zero validated results; historical JIRA/forum evidence and bounded negative results labelled accordingly.
- GitHub `.patch` URLs unavailable, REST diff used with disclosed patch-id limitation; no patch-equivalence claim. Three forum topics had no Wayback snapshot and are recorded as unresolved lanes. Skill updated with three retrieval pitfalls.

## Shared root-cause clustering checkpoint (2026-11-28T04:29Z)

- `SHARED_ROOT_CAUSE_CLUSTERS_W10_V8.jsonl` (8 records, sha256 `5ad972959745780f92c3241b1b64492b3876ff2a58665e0dee174803308cba25`): one PROVEN cluster C1 (USB3 boot/setup driver binding across CORE-13344, CORE-20821, PRs 9865/9750, both open+unmerged), two explicitly HYPOTHETICAL cross-lane clusters (setup metadata validation; WoW64/WDF binding completeness), and three PROVEN negative/correction records. All runtime fields NOT RUN.
- Correction recorded: PR 9865 body cites CORE-20821 while the earlier `USB3_GAP_V7.jsonl` scope indexed CORE-13344; issue-key equivalence not asserted. Live JIRA REST recheck: CORE-17655 Reopened, CORE-13344 Open, CORE-20751 and CORE-20821 Untriaged, all resolution null.
- `INDEPENDENT_REVIEW_SHARED_ROOT_CAUSE_W10_V8.jsonl` (7 records): independent reviewer distinct from the original researcher; verdict `CONFIRMED_WITH_CORRECTIONS` with an inherited-status limitation for CORE-19766 and a bounded-search caveat. No OS code, test, import, merge or upstream submission.

## RPL17 and shared-root-cause checkpoint (2026-11-28T04:29Z)

- `INDEPENDENT_REVIEW_RPL17_V8.jsonl` (11 records): F-01 re-reviewed from immutable commit `118f5cd5…`, patch-id `1dc87ba0…`, PR #9510 closed/unmerged and diverged in both compare directions; verdict `CONFIRMED_WITH_CORRECTION` (high confidence). Three append-only corrections: `commit_verified:true` lacked a reproducible verification field, author vs committer date distinction (2019-09-29 committer), and 256 KiB/>65k figures remain author assertions. Tests NOT RUN.
- Cron's `SHARED_ROOT_CAUSE_CLUSTERS_W10_V8.jsonl` (8) and `INDEPENDENT_REVIEW_SHARED_ROOT_CAUSE_W10_V8.jsonl` (7), published in `4aad6ded…`: one PROVEN USB3 boot/setup driver-binding cluster (CORE-13344, CORE-20821, PRs #9865/#9750 all open/unmerged), two hypothetical cross-lane clusters, three proven negatives; independent verdict `CONFIRMED_WITH_CORRECTIONS`. No equivalence asserted between CORE-20821 and CORE-13344 despite PR #9865 citing the former.

## RPL21 independent review checkpoint (2026-11-28T04:36Z)

- `INDEPENDENT_REVIEW_RPL21_V8.jsonl` (10 records): reviewed BOOTUEFI-V8-004/005/006 (closed-unmerged PR #8824 vs merged #8980 plus patch-equivalence negative). Verdict `CONFIRMED_WITH_CORRECTIONS`, confidence `HIGH_WITH_LIMITATIONS`; 7 append-only corrections cover mutable snapshots, self-reported retrieval times, paraphrase vs verbatim text, author-only test claims and `.diff`/`.patch` behaviour (8824.diff 200, 8980.diff 404). Runtime claims NOT ASSESSED, all tests NOT RUN.

## F-11 evidence revalidation checkpoint (2026-11-28T04:47Z)

- `EVIDENCE_REVALIDATION_RPL15_V8.jsonl` (10 records): F-11 (HBelusca commit `8bbed80b…`) `CONFIRMED_WITH_CORRECTIONS`, confidence `HIGH_WITH_LIMITATIONS`. Verified exact SHA/URL, author date, one file (34+/5-), signature `verified=true/reason=valid`, patch-id `2210cc8a…`, and pinned raw header lines 45/46/47/57. Seven append-only corrections narrow the undocumented claim, test-suite wording, unqualified commit date, keyword hits, self-reported retrieval and object-presence vs integration; upstream integration and constants' origin NOT ESTABLISHED, runtime NOT RUN.

## Malay coverage checkpoint (2026-11-28T04:59Z)

- `COVERAGE_RPL16_V8.jsonl` (13 records): new Malay (`ms`) lane, absent from all prior coverage artifacts. 10 bounded exact queries (5 Wikipedia API, 5 web_search; 16/1/1/1/0 totalhits and 50 web rows), 13 snippet records, 1 full Wikipedia extract (2,108 chars, revision 2023-11-15T17:44:02Z), 2 metadata records. All five web queries returned zero Malay-language matches; recorded as a lane-specific result, not universal absence. Tests NOT RUN; no access-control bypass.

## RPL19 evidence and RPL18 provenance checkpoint (2026-11-28T05:00:01Z)

- `EVIDENCE_REVALIDATION_RPL19_V8.jsonl` (9 records, sha256 `563765489dcafb48e0b9c2d7816d9bf550485e6fb62b5d3d30cca195ece12577`): F-12 canonical finding (DistroHopper39B merge commit `c52dd091…`) `CONFIRMED_WITH_CORRECTIONS`, `HIGH_WITH_LIMITATIONS`. Reproduced from immutable REST: exact SHA, author/committer date 2024-04-06T22:32:31Z, 300 changed files, two parents and exact merge message; all five mutable upstream PR states (9783/8618/8831/8820/8706) still match the citation snapshot. One correction: canonical `commit_verified=true` is an author assertion — live REST `verification` reports `verified=false`, reason `unsigned` — appended privately as `V8D-20261128-0003`; canonical record not rewritten. Upstream equivalence of the 300-file merge tip NOT ESTABLISHED; runtime NOT RUN.
- `PROVENANCE_REVALIDATION_RPL18_V8.jsonl` (10 records, sha256 `78bb531ecf6b2524aa2d1ced3fb40d4877afd5bbf267e832ee284769960bb453`): six cited forks (DistroHopper39B, TheNNX, HBelusca, Extravert-ir, maharmstone, vgalnt) all live, non-archived, `fork=true`, parent/source `reactos/reactos`, repo-level license `GPL-2.0`; verdict `CONFIRMED_WITH_LIMITATIONS`. Per-file SPDX headers NOT VERIFIED; mutable lineage/default_branch fields recorded as snapshot (DistroHopper39B default branch `AppleTV-Desktop`).
- Validator re-run: `files=167 json=7 jsonl=118 ids=5269 urls=7884 failures=143`, identical to the pre-existing snapshot; zero failures reference either new artifact. All runtime/build/VM/merge/import/submission fields NOT RUN. Research-only; no canonical record, shared status/coverage/snapshot file or OS code edited by the workers.

## F-09 review and cron revalidation checkpoint (2026-11-28T05:08Z)

- `INDEPENDENT_REVIEW_RPL25_V8.jsonl` (17 records): F-09 (`dd4de27e…`) `CONFIRMED_WITH_CORRECTIONS`, confidence `HIGH_WITH_LIMITATIONS`. Exact URL/SHA/author date/parent/12 files upheld; 5 append-only corrections cover unsigned `commit_verified=true`, DWM/theme scope narrowing, committer vs author date, mutable PR-hit interpretation and remote-head drift. Ancestry via REST compare (`diverged`, ahead 1114 / behind 23) because the local clone lacked the object; all runtime fields NOT RUN.
- Cron's `EVIDENCE_REVALIDATION_RPL19_V8.jsonl` (9) revalidated F-12 merge `c52dd091…` (300 files, two parents, five PR states) with `CONFIRMED_WITH_CORRECTIONS`; `PROVENANCE_REVALIDATION_RPL18_V8.jsonl` (10) confirmed six cited forks are live forks of `reactos/reactos` with repo-level GPL-2.0, per-file SPDX NOT VERIFIED. Both published in `53ad7daf…` with validator unchanged at 143 pre-existing failures.

## F-10 revalidation checkpoint (2026-11-28T05:17Z)

- `EVIDENCE_REVALIDATION_RPL23_V8.jsonl` (16 records): F-10 (binarymaster commit `85646637…`) `CONFIRMED_WITH_CORRECTIONS`, confidence `HIGH_WITH_LIMITATIONS`. Exact URL/SHA/message/dates/two-file diff and EC default-space change reproduced from immutable primaries. Five append-only corrections: unsigned `commit_verified=true`, VM sentence is a recommendation not an executed test, EC/ACPI scope narrowed to two files, PR hits are mutable keyword snapshots (#8980 reintroduces #8824), `retrieved` self-reported. All tests NOT RUN; validator failures unchanged at 143.

## Open PR inventory checkpoint (2026-11-28T05:32Z)

- `OPEN_PR_INVENTORY_W11_V8.jsonl` (165 records): 163 open upstream PRs refreshed read-only (21 draft, 142 non-draft), 163 direct state reads and 163 paginated file reads with 0 API errors; changed-file counts matched 163/163. 47/163 in technical lanes (memory/cache 12, SMP 14, storage 11, networking 12 any-lane; 349 in-scope changed files). Do-not-duplicate: 47/47 in scope, 131/163 overall; 6 prior-conflict overlaps, 2 new in-lane observations, #8566 refreshed, #9826 no longer open. All runtime fields NOT RUN; no import or merge.

## F-02/F-07 equivalence revalidation checkpoint (W11-01)

- `EVIDENCE_REVALIDATION_W1101_V8.jsonl` (10 records, sha256 `9eb96949c2d1e585004543f97f3d07564ff60301088506cfd06088698c3f0a7b`): both inherited equivalence claims `CONFIRMED_WITH_LIMITATIONS`. Fork and upstream commits share identical tree SHAs and byte-identical patch bodies (patch-id `ecb96617` / `a1c40064`); both upstream SHAs are local `origin/master` ancestors and PR 1965/1070 merge SHAs match. Fork commits are GPG-verified; upstream integrated commits are unsigned. Two append-only corrections: F-07 PR 1035 is a keyword false positive, and `commit_verified=true` applies only to fork commits. Validator failures unchanged at 143; all runtime fields NOT RUN.

## Closed-unmerged prerequisite recheck, second sample (W11-03)

- `PREREQUISITE_RECHECK_SECOND_SAMPLE_W1103_V8.jsonl` (10 records, sha256 `62e8d53da8f84571c719604b68bdbd964041939a0984c32b3a836341c276f586`): 4 bounded search queries, 47 distinct closed-unmerged candidates, 8 sampled with the first sample excluded. PR 4674's named prerequisites 4533/4672/4673 are all still closed-unmerged; the other 7 sampled bodies yielded zero explicit PR-to-PR prerequisite (recorded as zero-result lanes). No import, build or runtime test; all runtime fields NOT RUN.

## Archive/forum family coverage (W11-04)

- `ARCHIVE_FORUM_COVERAGE_W1104_V8.jsonl` (5 records, sha256 `078e7280e404b6186aa93d13befbad24e91d17b9aed59d981668e9f5ffca22e8`): forum.reactos.org family, bounded live attempt plus Wayback CDX inventory (rows=0, range []) and one archived snapshot. Historical snapshots not treated as current state; no access-control bypass; all runtime fields NOT RUN.
- Correction supplement: `ARCHIVE_FORUM_COVERAGE_W1104_PROBE_V8.jsonl` (2 records, sha256 `0b8290d842f17946c5cf2ec23589e0e7cad9116d1c48d2077d1ed27bfa48324a`). A bounded unfiltered Wayback CDX probe returned HTTP 503 (temporary offline), so the earlier zero-row result is classified inconclusive rather than absence of archived snapshots.

## Independent prerequisite sample checkpoint (2026-11-28T05:47Z)

- `PREREQUISITE_RECHECK_W11_V8.jsonl` (27 records) is the subagent's independent 8-PR sample: 1 qualifying reevaluation lead (#5935, closed 2023-11-09, prerequisite #5868 merged 2024-05-06 via `69ebfd67…`) and 7 explicit negatives (#3502/#4398/#4674/#5484 unmerged deps; #7448/#7870 prerequisites merged before subject closure; #9679 only split-from lineage). This is distinct from cron's `PREREQUISITE_RECHECK_SECOND_SAMPLE_W1103_V8.jsonl` (10 records, 0 qualifiers), which remains unchanged. Both results coexist; different samples and selection methods, no conflict reconciled by inference.
- Cron additionally published F-02/F-07 immutable equivalence revalidation (`EVIDENCE_REVALIDATION_W1101_V8.jsonl`, 10) and archive/forum coverage with an inconclusive-zero correction (`ARCHIVE_FORUM_COVERAGE_W1104_V8.jsonl`, 5 + 2 supplement). All runtime fields NOT RUN, no import or merge.

## F-12 independent review checkpoint (2026-11-28T05:57Z)

- `INDEPENDENT_REVIEW_RPL29_V8.jsonl` (19 records): F-12 fork commit `c52dd091…` `CONFIRMED_WITH_CORRECTIONS`, confidence `HIGH_WITH_LIMITATIONS`; seven append-only corrections. Key corrections: `files_changed:300` is a REST page cap (6 pages, 1535 distinct paths); `commit_verified:true` is an author assertion vs REST unsigned; `.patch` expands a 710-commit series ending at the merge second parent; test-gate list is a recommendation, not executed tests. Local clone lacked the commit object (merge-base NOT RUN); no canonical record rewritten, all runtime fields NOT RUN.
- Artifact was written into a stale auxiliary worktree and verified/copied into the canonical research tree before publication; no history rewritten.

## Lithuanian coverage checkpoint (2026-11-28T06:02Z)

- `COVERAGE_RPL20_V8.jsonl` (16 records): Lithuanian (`lt`) lane absent from 41 prior language codes. 12 bounded exact queries (7 Wikipedia API, 5 web_search; 67 rows: 17 API + 50 web), 8 matched wiki rows and 8 matched web rows, 6 zero-result lanes, 12 snippet-only and 2 explicitly labelled full extractions. Exact query strings, URLs, row counts and denominators recorded; validator found zero failures attributable to the new file.

## LGPL provenance checkpoint (2026-11-28T06:10Z)

- `PROVENANCE_REVALIDATION_RPL22_V8.jsonl` (17 records): ReactOS LGPL license texts `COPYING.LIB` (LGPL-2.1) and `COPYING3.LIB` (LGPL-3.0) rechecked at pin `3e6033a6…` and fork tip `9a21d07a…`. 13 read-only primary HTTP checks (2 commit, 4 contents, 4 raw, 3 SPDX samples), all HTTP 200; canonical URLs, blob SHAs and retrieval timestamps confirmed, texts byte-identical across revisions. Per-file SPDX and `-only`/`-or-later` variants remain unresolved; three append-only scope corrections recorded. Validator unchanged at 143 failures.

## W12-03 filesystem validation current-state checkpoint (2026-11-28T06:21:40Z)

- `W12_FS_VALIDATION_CURRENT_V8.jsonl` (11 records, sha256 f0e978a3f45bf7d62dbd09bd5bdeabad9b1ee3449bc3b8606bbb256b58e31dc3): upstream master `a5ccec99ed84…` is one commit ahead of pin and untouched in FS paths; `fat.c` and `ntfs.c` are byte-identical to the pin. Four bounded open-PR queries: 3 zero-result lanes, NTFS keyword returned 2 unrelated PRs (9736 UCRT, 9576 ETHREAD), both fully paginated with zero filesystem paths. Static only; all runtime fields NOT RUN.

## W12-01 FV7-008 immutable recheck checkpoint (2026-11-28T06:24:27Z)

- `FV7_008_IMMUTABLE_RECHECK_W1201_V8.jsonl` (8 records, sha256 aa30e03d450ecc2856a0232bb1e5acf4700b8d91e03500534b35e72198badcce): verdict coverage confirmed for FV7-008 and FV7-009 (premise stale). Cited CI commit `8b55d712…` re-projected from `.commit.message`/`.commit.verification`: 2022-05-25 MSVC ARM64 builder citing CORE-17518, GPG verified=True, present upstream and fork, 8101 commits behind master. Four append-only corrections; no canonical rewrite; all tests NOT RUN.

## RPL-EVIDENCE-0027 checkpoint (2026-11-28T06:26:24Z)

- `EVIDENCE_SHA_RECHECK_RPL27_V8.jsonl` (9 records, sha256 1ee17ad9a5d875b04d82c8f6d62351152a087e266e38a4a00a288d868eae0b17): canonical PR 9510 head `56b5899d…` / base `86f1b427…` reproduced from .head.sha/.base.sha; commit unsigned at upstream and fork; 2 files after full pagination; raw .patch SHA-256 01f4238f846cfbe13e14dfaa395fa137ca2f835916027fe94464a47482ca80af. Clarified .diff (9473 bytes) vs .patch (11013 bytes) endpoint scope; no canonical rewrite.

## Cache-manager technical lane checkpoint (2026-11-28T06:27Z)

- `CACHE_MANAGER_ISSUES_W12_V8.jsonl` (82 records): 5 JIRA queries, 29 JIRA issues, 5 GitHub searches, 28 PR records, 8 correlations and 4 pin-source token records. 11 open upstream PRs (incl. `[NTOS:CC]` #9668/#9314) classified do-not-duplicate; #9127/#9467 closed-merged historical work. Pin vs current master `a5ccec99…` is ahead_by=1/behind_by=0 with only 5 USER32 apitest files changed, so CC/MM static state is identical. All runtime fields NOT RUN.

## Latvian coverage checkpoint (2026-11-28T06:37Z)

- `COVERAGE_RPL24_V8.jsonl` (21 records): Latvian (`lv`) lane absent from prior coverage. 19 query slots (16 API + 3 web, 16 distinct strings), 47 rows (17 API + 30 web), 15 matched URLs, 9 labelled zero-result lanes, zero full extractions; all snippet-labelled. Three lv.wikipedia HTTP 429 first attempts each resolved by one bounded retry and recorded without double-counting. No access-control bypass, no inference from zero, all runtime fields NOT RUN.
- Cron's `W12_FS_VALIDATION_CURRENT_V8.jsonl` (11), `FV7_008_IMMUTABLE_RECHECK_W1201_V8.jsonl` (8) and `EVIDENCE_SHA_RECHECK_RPL27_V8.jsonl` (9) are present in branch history via parent commit `08bd7222…`; validator unchanged at 143 failures with zero attributable to new files.

## Albanian coverage checkpoint (2026-11-28T06:43Z)

- `COVERAGE_RPL28_V8.jsonl` (16 records): Albanian (`sq`) lane absent from prior coverage. 12 query slots (7 sq.wikipedia API, 5 web_search; 55 rows), 1 conservative literal match (`Stampa:Sistemet operative`), 11 zero-result lanes, 6 API `totalhits=0` lanes, 2 full wikitext extractions (412/5948 chars) separated from 12 snippet records. Denominators and query-scoped uncertainty recorded; no tests, no access-control bypass.

## F-06 SHA recheck checkpoint (2026-11-28T06:48Z)

- `EVIDENCE_SHA_RECHECK_RPL31_V8.jsonl` (10 records): F-06 commit `45fb6e79…` `CONFIRMED_WITH_CORRECTIONS`, confidence 0.9 for source/repository facts only. Both immutable endpoints reproduce SHA/date/message/parent and single changed path; raw patch (907 bytes, sha256 `f6e4e71a…`) shows the `#ifndef NDEBUG` guard. Six append-only corrections narrow `commit_verified=true` vs REST unsigned, unestablished "final commit"/"boot-blocking" wording, mutable PR states, historical retrieval time and endpoint byte differences. Tests NOT RUN.

## Supervisor checkpoint 2026-11-28T07:02:29Z

- Control re-verified: V8 ba45cc18..., correction f2e43b42..., CONTROL d3785fdb... (authoritative SHA-256 all matched); no EMERGENCY_STOP.
- Watchdog singleton 08b68a4bc9b8: enabled, one legitimate active lease (W12-04), no second dispatcher.
- Replenished to 10 ready; claimed 3 with unique cron-<UTC> workers via the disclosed priority-lower/claim/restore path: W12-05 (w1205), RPL-PROVENANCE-0026 (p0026), RPL-REVIEW-0033 (r0033).
- Published APP_COMPAT_CLUSTER_RECHECK_W1205_V8.jsonl (5 records), PROVENANCE_REVALIDATION_P0026_V8.jsonl (6 records), INDEPENDENT_REVIEW_FV7_006_R0033_V8.jsonl (4 records).
- All runtime tests NOT RUN; research-only; no OS code, patch import, merge or upstream submission.

## SMP/IRQL technical lane checkpoint (2026-11-28T07:05Z)

- `SMP_IRQL_ISSUES_W12_V8.jsonl` (65 records): 6 JIRA queries, 44 unique JIRA issues (16 domain candidates, 28 keyword-only), 12 open upstream PRs all classified do-not-duplicate, one cross-tracker correlation. Pin → master `a5ccec99…` is ahead_by=1 (USER32 apitest commit); zero overlap with the 142 PR-proposed paths, 99 paths unchanged, 43 absent at both refs. All runtime fields NOT RUN; keyword searches are bounded samples.
- Cron's local publication `2b787e24…` (W12-05 app-compat recheck, P0026 provenance, R0033 FV7-006 review) is present in branch history and remote-verified.

## Stack Exchange coverage checkpoint (2026-11-28T07:11Z)

- `COVERAGE_RPL32_V8.jsonl` (12 records): new Stack Exchange API v2.3 source family, previously unqueried across ten coverage files. 9 bounded queries (pagesize=10), 24 returned rows, corpus denominator sum 73 via `filter=total` (51/1/0/0/0/18/3/0/0), 14 matched URLs, 5 explicit zero-result lanes (USB xHCI, ARM64, FAT boot, all-subsystem terms, `tagged=reactos`). Nine snippets and one full extraction labelled; bodies not republished; point-in-time metadata only, all runtime fields NOT RUN.

## F-05 SHA recheck checkpoint (2026-11-28T07:16Z)

- `EVIDENCE_SHA_RECHECK_RPL35_V8.jsonl` (10 records): F-05 commit `88786202…` `CONFIRMED_WITH_CORRECTIONS`, confidence 0.9 for source/repository facts. Fork and upstream REST both HTTP 200 with matching SHA/date/message/parent, 7 files (+104/-18); raw patch shows 7 paths and 30 hunks. Ten append-only corrections: `commit_verified=true` is an author assertion (REST unsigned), "modern stack basic-merged" refers to later PRs #9646/#9623 and not this SHA, mutable PR snapshots and historical retrieval metadata flagged. Compare diverged ahead 20713/behind 27; all runtime fields NOT RUN.

## Filesystem reliability lane checkpoint (2026-11-28T07:30Z)

- `FS_RELIABILITY_OPEN_W12_V8.jsonl` (87 records): 3 JIRA queries (NTFS 62, Btrfs 78, filesystem 329 total/100 returned), 45 detailed unresolved issues, 5 GitHub searches (0 open issues), 163 open PR file lists scanned, 14 PR records (9 open) and 12 correlations. Pin→master ahead1/behind0 with only USER32 apitests; five NTFS/Btrfs source files byte-identical. Open draft #9598 (Btrfs) and adjacent #9753 (FreeLDR FS) classified do-not-duplicate; merged/closed historical PRs recorded. All runtime fields NOT RUN; validator unchanged at 143 pre-existing failures.


## Supervisor checkpoint 2026-11-28T07:48:02Z

- Control re-verified: V8 ba45cc18..., correction f2e43b42..., CONTROL d3785fdb... all matched authoritative SHA-256; no EMERGENCY_STOP; branch research/v7-wave1 clean, local/remote head 4e5baf46... at start.
- Watchdog singleton 08b68a4bc9b8 enabled; one legitimate active lease (W12-07) at start and throughout; no second dispatcher. Replenished 5 -> 9 ready with four real template tasks before claiming.
- Claimed three queued tasks with unique cron-<UTC> workers via the disclosed priority-lower/claim/restore path, leaving W12-07 untouched: RPL-PROVENANCE-0030, RPL-COVERAGE-0036, RPL-REVIEW-0037.
- `PROVENANCE_REVALIDATION_P0030_V8.jsonl` (7 records): third-party `dll/3rdparty/libpng/png.c` at pin 3e6033a6... contents/raw/blob/header revalidated; 135426 bytes, SHA-256 8a1ff605..., recomputed git blob equals API blob, same blob at research tip d1db1689...; libpng license statement quoted verbatim (no SPDX tag); commit verification re-projected from commit.verification.
- `COVERAGE_HN_ALGOLIA_RPL36_V8.jsonl` (11 records): new Hacker News Algolia story-index lane with explicit per-query denominators (nbHits 4580/0/8/0/17/2/1415/3078), 8/8 HTTP 200, hitsPerPage=5, 2 explicit zero-result lanes, 0 full extractions, no universal-coverage claim.
- `INDEPENDENT_REVIEW_APPCOMPAT_R0037_V8.jsonl` (7 records): ACV8-015 do-not-duplicate INDEPENDENTLY_CONFIRMED from four fresh primary REST responses by an independent reviewer handle; PRs #9757/#9872/#9761 open unmerged, CORE-13141 Open/null.
- Validator unchanged at 143 pre-existing failures; zero new failures from these artifacts. All runtime/build/test fields NOT RUN; research-only, no OS code, patch import, merge, upstream submission or credentials.

## Networking reliability lane checkpoint (2026-11-28T07:50Z)

- `NETWORK_RELIABILITY_OPEN_W12_V8.jsonl` (263 records): 5 unresolved JIRA queries (NDIS 36, TCP/IP 12, TCPIP 27, Winsock 12, network driver 89), 94 open issues (57 Untriaged, 35 Open, 2 Reopened) with 94 correlations; 163 open PR file lists paginated with 0 errors; 47 PR records (28 merged, 8 closed-unmerged, 10 open, 1 HTTP 404 citation). Do-not-duplicate open PRs #8347/#9346/#9598/#9866/#9893/#9836; #9736 excluded as a keyword false positive. 14 network source fingerprints byte-identical at pin and master; all runtime fields NOT RUN.
- This publication also includes cron's verified `PROVENANCE_REVALIDATION_P0030_V8.jsonl` (7), `COVERAGE_HN_ALGOLIA_RPL36_V8.jsonl` (11) and `INDEPENDENT_REVIEW_APPCOMPAT_R0037_V8.jsonl` (7), all scanned clean.

## GitLab API coverage checkpoint (2026-11-28T08:01Z)

- `COVERAGE_RPL40_V8.jsonl` (13 records): new GitLab.com public REST API v4 `/projects` family and German query-term lane. 10 bounded queries (`per_page=5`, `page=1`), 9 HTTP 200 with `X-Total` denominators; baseline ReactOS total 39 / 5 returned / 5 matched HTTPS URLs; 8 zero-result lanes (3 en, 4 de, `ReactOS Deutsch`). One HTTP 500 control-token query recorded with denominator unknown, explicitly not zero. One full project-metadata extraction separated from snippet rows; all runtime fields NOT RUN.

## UEFI revert SHA recheck checkpoint (2026-11-28T08:14Z)

- `EVIDENCE_SHA_RECHECK_RPL39_V8.jsonl` (10 records): `BOOTUEFI-V8-008` (reverted PR #7486), merge `185225a5…` and revert `177cbd81…`, `CONFIRMED_WITH_CORRECTIONS`, confidence 0.9. Eight append-only corrections: "four days later" is calendar-date wording (3d 9h 27m), double-mapping is a reviewer report rather than a reproduced runtime fact, no causal link to the revert established, branch head mutable, merge PGP-verified vs unsigned revert. All HTTPS URLs and the verbatim review comment reproduced; tests NOT RUN.

## Audio/HID technical lane checkpoint (2026-11-28T08:39Z)

- `AUDIO_DRIVER_OPEN_W12_V8.jsonl` (549 records): 231 JIRA issues + 231 correlations, 53 PRs, 18 pin/master fingerprints, 7 JIRA queries, 6 GitHub searches. Pin → fresh master `60a3898b` ahead 13/behind 0 with HID/USER32-only changes and zero audio paths; 18 audio/AC97/HDA blobs byte-identical. Do-not-duplicate opens #8662/#8683/#9083/#9313/#9598/#9852; #8355 CMake false positive; cited #55088 HTTP 404 recorded unresolved. All six runtime fields NOT RUN.
- Also published: cron's `INPUT_HID_OPEN_W12_V8.jsonl` (43), `INDEPENDENT_REVIEW_W9_10R_R0041_V8.jsonl` (7) and `PROVENANCE_REVALIDATION_P0034_V8.jsonl` (8), all verified unique-ID and scan-clean.


## Supervisor checkpoint 2026-11-28T08:38Z (cron 02:21 CST fire)

- Control re-verified: V8 ba45cc18..., correction f2e43b42..., CONTROL d3785fdb... all matched authoritative SHA-256 before any claim; no EMERGENCY_STOP; branch research/v7-wave1 clean, local/remote head 4018c32d... at start.
- Watchdog singleton 08b68a4bc9b8 enabled, zero active leases at check, no second dispatcher. A concurrent W12-08 worker held an audio lease; it was left untouched until it finished on its own, then its published 549-record artifact was adopted into the commit without modifying its lease or evidence.
- Replenished 5 -> 9 ready with four real template tasks before claiming. Claimed three with unique cron-<UTC> workers via the disclosed priority-lower/claim/restore path: W12-09, RPL-PROVENANCE-0034 and RPL-REVIEW-0041 (independent reviewer handle). Closed with 6 queued, 0 running, 14 reviewed, 123 verified.
- `INPUT_HID_OPEN_W12_V8.jsonl` (43 records): 4 unresolved JIRA lanes with explicit denominators HID=22, keyboard=194, mouse=302, raw input=8; 24 detailed issues; 163 open PRs inventoried and 10 keyword hits paginated, including live input/HID PRs #9890, #9863, #9864, #9818; one keyword false positive (#9768) excluded; pin 3e6033a6 -> master 60a3898b ahead_by=13/behind_by=0. All runtime fields NOT RUN.
- `PROVENANCE_REVALIDATION_P0034_V8.jsonl` (8 records): distinct bundled `dll/3rdparty/libjpeg/jcapimin.c` at pin 3e6033a6...; 9384 bytes, recomputed git blob equals API blob and size matches; verbatim license header lines (no SPDX-only rule); same blob at research tip d1db1689...; commit verification re-projected from commit.verification (verified=true, reason=valid).
- `INDEPENDENT_REVIEW_W9_10R_R0041_V8.jsonl` (7 records): independent recheck of fork tip SHA 011b958c... with no prior dedicated recheck; exact object presence, single-file changed set version.h +4/-4 and immutable .patch header From-line reproduced; INDEPENDENTLY_CONFIRMED with one append-only correction (REST verified=false/unsigned is an author assertion, not a canonical defect); no canonical record rewritten.
- Validator unchanged at 143 pre-existing failures with 0 lines naming any new artifact; ids unique, self-counts match, all URLs https, no banned private strings, all runtime_state NOT RUN. Research-only: no OS code, patch import, build/test/VM, merge, upstream submission, credentials or access-control bypass; no blockers.

## arXiv coverage checkpoint (2026-11-28T08:45Z)

- `COVERAGE_RPL44_V8.jsonl` (12 records): new arXiv Atom search API family, absent from 12 prior coverage records. 9 bounded queries all HTTP 200 with `start=0`/`max_results=5` and exact `opensearch:totalResults` denominators (corpus total 65, 12 bounded rows, 12 matched HTTPS URLs, 3 zero-result lanes: `reactos-os`, `reactos-kernel`, `reactos-cs-os`). Tokenization false positive `ti:"ReactOS"` returning a REACTO paper recorded, not counted as a literal match. Nine snippets and one full abstract-page extraction labelled; all runtime fields NOT RUN.

## Storage driver lane checkpoint (2026-11-28T08:57Z)

- `STORAGE_DRIVER_OPEN_W12_V8.jsonl` (546 records): 10 JIRA searches → 226 unresolved issues (141 Untriaged, 68 Open, 16 Reopened, 1 In Progress), 226 correlations, 7 GitHub searches (0 open issues, 12 open PR hits), 163 open PR file lists paginated with one transient 502 retried to 0 errors. Pin → fresh master `60a3898b` ahead13/behind0, 14 changed files with zero storage/disk-class paths; 18 sampled blobs byte-identical. Do-not-duplicate opens #8566/#8849/#8932/#9095/#9598/#9753/#9856; #9550 MSHTML false positive; cited 128613 HTTP 404 recorded unresolved. All runtime fields NOT RUN.
