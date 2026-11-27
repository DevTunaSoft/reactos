# ProjectOS V7 — coverage matrix (Wave 1)

Coverage claims are scoped to what was actually queried. Zero means zero; no percentage is inferred where the denominator is unknown.

| Source family | Language | Subsystem | Query / endpoint | Date (UTC) | Inspected | Unavailable | Follow-ups |
|---|---|---|---|---:|---:|---:|---|
| GitHub REST fork list | en | repository inventory | `GET /repos/reactos/reactos/forks?per_page=100&sort=oldest`, `gh api --paginate` (Link headers followed by client), 25 pages | 2026-11-27 | 2426 unique IDs | 0 request errors | branch/tag pagination (W2-01) |
| GitHub GraphQL | en | parent lineage | 100 aliases/query, `parent{nameWithOwner databaseId}` | 2026-11-27 | 2336 verified parents | 90 unresolved | classify renamed/deleted/private |
| GitHub GraphQL + REST ID fallback | en | prior candidate validation | 999 name lookups in 10 batches; `GET /repositories/{id}` fallback | 2026-11-27 | 999 public | 0 | 89 candidates outside fork network |
| JIRA REST | en | wow64/usb/arm64 | `GET /rest/api/2/issue/{CORE-ID}` for 3 IDs | 2026-11-27 | 3 | 0 | status reconciliation with GitHub |
| JIRA REST text search | en | FAT boot | `jql=text ~ "cluster chain"`, maxResults=10 | 2026-11-27 | 6 returned | 0 | no FreeLoader boot issue found |
| GitHub REST issue/PR search | en | CORE IDs | `search/issues?q=repo:reactos/reactos CORE-…` | 2026-11-27 | 3+2+18 items | 0 | state/merged verification |
| GitHub REST commit/patch | en | storage/memory | 12 immutable commit URLs + 3 `.patch` comparisons | 2026-11-27 | 12 verified, 3 patch-ids | 0 | semantic comparison for F-03 |
| ReactOS raw source at pinned SHA | en | FreeLoader FAT | `boot/freeldr/freeldr/lib/fs/fat.c` lines 320, 335, 1108-1133 | 2026-11-27 | 1 file | 0 | design synthetic malformed images |

## Not covered in Wave 1 (explicitly zero)

- Languages other than English: 0 queries. Initial lanes (ru, de, uk, pl, fr, es, pt, it, zh, ja, ko, cs, nl, tr) are queued as W3-01.
- Community surfaces: 0 queries on forums, Reddit, Hacker News, OSDev, Stack Exchange, WineHQ, Vogons, MSFN, blogs, chat archives or lawfares.
- Historical artifacts: 0 queries on SVN history, ros-diffs/ros-dev archives, Testman, CI logs, GSoC attachments, academic sources, standards or non-GitHub forges.
- Runtime testing: 0 builds, 0 VM boots, 0 tests executed. All test fields are `NOT RUN`.
- Branch/tag enumeration inside verified forks: 0 new branches enumerated in this wave.
- Independent evidence review: 0 findings reviewed; all are `pending_independent`.

No claim of universal coverage is made. Prior records are treated as leads until revalidated; corrections are appended, not erased.

## Addendum — community and language lanes (2026-11-27T05:55Z)

| Source family | Language | Surface | Items inspected | Unavailable | Follow-ups |
|---|---|---|---:|---:|---|
| Habr | ru | company article | 1 (snippet only) | 0 | W3-03 full extraction |
| ReactOS forum | en | 3 threads + forum index | 4 (snippets only) | 0 | read latest posts with dates |
| Reddit | en | r/reactos thread | 1 (snippet only) | 0 | check current wiki text |
| Independent press | en | VideoCardz | 1 (snippet only) | 0 | W3-07 primary-source reconciliation |
| ReactOS wiki | en | Supported USB Devices | 1 (snippet only) | 0 | W3-04 revision date |
| Third-party source mirror | en | Fossies Dox 0.4.16 | 1 (snippet only) | 0 | W3-05 authoritative tag check |

Total community items inspected: 8; full-page extractions performed: 0. Language lanes covered: 2 of 15 initial lanes (ru, en). These are leads, not verified technical evidence.

## Addendum — Wave 3 coverage (2026-11-27T06:25Z)

| Source family | Language lanes | Records | Full extractions | API extractions | Snippet-only | Notes |
|---|---:|---:|---:|---:|---:|---|
| Community forums / Habr / press / mirror | 10 queried (6 usable, 4 zero-result) | 15 | 5 | 0 | 10 | `MULTILINGUAL_V7.jsonl` |
| Reddit / ReactOS forum | en, de, ru + adjacent | 15 | 2 | 0 | 13 | `REDDIT_FORUM_V7.jsonl`; direct HTTP 403/Anubis blocking recorded |
| JIRA / upstream PR / mailing list | en | 26 | 0 | 25 | 1 | `HISTORICAL_FAILURES_V7.jsonl`; 8 JIRA issues opened, 10 PR states verified |
| Fork refs (second cohort) | N/A | 453 published records | N/A | 12 repos, 403 branches, 2988 tags | N/A | `REF_ENUMERATION_W4_V7.jsonl`, `SHARED_TIP_CLASS_V7.jsonl`; 382/382 shared tips resolved, patch-equivalence NOT RUN |

Cumulative language lanes with at least one usable source: 6 of 15. Runtime tests executed in Wave 3: 0. Habr source dated 2023-12-30 and treated as time-bound.

## Addendum — Wave 4 coverage (2026-11-27T06:42Z)

| Source family | Records (published) | Scope | Notes |
|---|---:|---|---|
| Immutable fork tip patches/diffs | 10 | 8 WoW64 tips + 2 upstream PR patches | 98 unique paths; 51 absent at pin; `WOW64_DEEP_DIFF_V7.jsonl` |
| Upstream PR diffs + pinned source | 10 | PRs #9865/#9750, `txtsetup.sif`, `wdfldr.c`, CORE-13344 | API/raw extraction; runtime NOT RUN |
| Authoritative release tag | 7 | ReactOS 0.4.16 `fat.c` | `RELEASE_TAG_FAT_V7.jsonl` |
| Testman + GitHub Actions | 58 (aggregated from 1958 raw) | 8259 suite runs, 1906 skipped mappings, 33 CI jobs | raw mapping retained privately; `TEST_INTELLIGENCE_V7.jsonl` |

Testman per-test detail unavailable; no runtime test executed. Public evidence compacted without changing any denominator.

## Addendum — Wave 10 coverage extension: four previously unqueried language lanes (2026-11-27T11:13Z)

Task `RPL-COVERAGE-0002` (lane B), worker `cron-20261127T111304Z`. Query tool: public `web_search` snippets, `limit=10` per query. Canonical records: `COVERAGE_EXTENSION_V7.jsonl` (7 append-only records). All retrieved text treated as untrusted evidence; snippet-only, no full-page extraction, no primary-source verification, no inference.

| Language | Query | Result rows (denominator) | Language-matched technical items | Full extractions | Notes |
|---|---|---:|---:|---:|---|
| ko | ReactOS WoW64 USB 3.0 xHCI ARM64 한국어 포럼 드라이버 | 10 | 0 | 0 | All rows English-language, already-covered families |
| cs | ReactOS WoW64 USB 3.0 xHCI ARM64 čeština fórum ovladače | 10 | 0 | 0 | Czech subforum surface found; no matched article |
| nl | ReactOS WoW64 USB 3.0 xHCI ARM64 Nederlands forum drivers | 10 | 1 | 0 | linuxmag.nl USB 3.0 item; cites Phoronix, secondary |
| tr | ReactOS WoW64 USB 3.0 xHCI ARM64 Türkçe forum sürücüleri | 10 | 1 | 0 | technopat.net ARM64 forum post; secondary |

Totals: 4 lanes, 40 result rows, 2 language-matched items, 0 full extractions, 0 publication dates verified, 0 primary-source correlations. ko/cs are explicit zero-result lanes at this query, not claims of universal absence. New source-surface lead: ReactOS forum Czech subforum (`https://reactos.org/forum/viewforum.php?f=39`), snippet-derived 58 topics / 489 posts, unverified beyond the snippet; no thread opened. The two matched items corroborate already-recorded primary findings (PR #9646 USB3; FV7-008 / PR #9795 ARM64) only as secondary reporting. All runtime fields remain NOT RUN; no OS code, patch import, build, test, VM, merge or upstream submission.

## Addendum — Wave 8 coverage (2026-11-27T14:47Z)

| Source family | Records | Scope | Notes |
|---|---:|---|---|
| Kernel memory / filesystem reliability | 3 | JIRA/GitHub PR metadata at pin 3e6033a6 | `KERNEL_MEMORY_CANDIDATES_V7.jsonl`, `FS_RELIABILITY_V7.jsonl`; NOT RUN |
| SMP / network / historical regressions | 67 + 22 | 379 JIRA keys, 65 PR GETs, 27 searches | `SMP_NETWORK_ARCHAEOLOGY_V7.jsonl`, `NETWORKING_GAP_V8.jsonl`; 2 JIRA 400 + 5 Wayback lanes failed |
| Fork refs third cohort | 515 | 15 forks, 499 branches, 3765 tags, 249 tips | `FORK_REFS_W8_V7.jsonl`, `FORK_UNIQUE_CHANGES_V7.jsonl`; 249/249 exact SHAs upstream |
| Community / adjacent FOSS | 67 | 10 language lanes, 10 HyperKitty searches, 3 snapshots | `COMMUNITY_EXPANSION_V7.jsonl`, `ADJACENT_FOSS_V7.jsonl`; 9 zero-result lanes, 2 Anubis lanes |
| Retrieval engines | 28 | 5 engines, 1 JS fixture, 2 public pages each | `TOOL_INTEGRATION_V7.jsonl`; Lightpanda unavailable_platform |

Cumulative language lanes queried: at least 30; lanes with a usable source: 7. Runtime tests executed: 0. Unsupported or challenged lanes are recorded as failures/unavailable, never as negative findings.



