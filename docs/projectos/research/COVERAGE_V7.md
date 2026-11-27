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
