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

This document is a checkpoint, not a claim that research is complete.
