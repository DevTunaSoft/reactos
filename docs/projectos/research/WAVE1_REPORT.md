# ProjectOS V7 — Wave 1 report

Scope: bootstrap, durable queue, fork-network inventory, candidate validation, issue correlation, prior-finding revalidation. Time window 2026-11-27T05:12Z–05:45Z. All results are research-only; no OS implementation change, patch import, test execution, external submission or merge.

## What was established

1. Exact directive revision `5c02f5c5` (V7) fetched, hashed and recorded; PR #1 records preserved.
2. Live baselines re-resolved: upstream and DevTunaSoft master both `3e6033a6`. Research parent `5c02f5c5`.
3. Single-writer durable queue with append-only events, atomic state, lease/heartbeat, retry/backoff and an emergency-stop flag. Controlled crash/recovery test passed.
4. Authenticated paginated fork network: 2426 unique members; 2336 with GraphQL-verified parent `reactos/reactos`; 90 unresolved; 12 archived; 0 disabled.
5. All 999 prior name-search candidates still public; 910 are in the verified fork network; 89 are outside it. This is an explicit correction to the inherited inventory.
6. All 12 inherited findings F-01..F-12 have their cited commits verified at immutable SHAs.
7. Three patch-equivalence checks with `git patch-id --stable`: F-02 and F-07 exactly match merged upstream changes; F-03 does not match byte-for-byte.
8. Three CORE issues correlated against current upstream: CORE-17655 (Reopened; WoW64 prep merged), CORE-13344 (Open; modern USB3 stack merged), CORE-18200 (Open; multiple ARM64 merges).
9. One new strong candidate: unbounded `FatCountClustersInChain` at pinned baseline, with upstream PR #9510 closed unmerged. No canonical JIRA issue found; runtime test NOT RUN.

## What was disproven or downgraded

- F-02 (Btrfs unaligned reads): already upstream, exact patch identity.
- F-07 (symbol typo): already upstream, exact patch identity; prior deprioritization confirmed.
- F-05/F-06 (2017 xHCI branches): superseded by merged modern USB3 architecture; retain as design/regression archaeology only.
- The 999 prior candidates are not equivalent to fork-network membership.

## Counts with denominators

See `STATUS_V7.md` and `COVERAGE_V7.md`. Runtime tests executed: 0/0. Findings independently reviewed: 0/9. Language lanes searched beyond English: 0/15 initial lanes.

## Contradictory evidence and limitations

- CORE-13344 remains Open while a USB3 driver stack is merged upstream; issue text may be stale or acceptance incomplete. Both facts are recorded; no resolution inferred.
- CORE-17655 remains Reopened while preparation commits landed; current tree has no wow64 implementation subtree at the pinned baseline.
- F-03 may be behaviorally equivalent to upstream despite different patch IDs; marked EQUIVALENCE_UNKNOWN, not rejected.
- 90 fork members unresolved by GraphQL; cause not inferred.
- PR #9510 closure reason was not documented in returned comments; motive not inferred.

## Queue state and next wave

Nine tasks seeded; two verified (W1-01, W1-02), two in progress/awaiting write (W1-03, W1-04), five queued. Next: W2-01 branch/tag enumeration, then independent review of FV7-009 and failure archaeology.
