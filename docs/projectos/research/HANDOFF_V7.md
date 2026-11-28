# ProjectOS V7 — recovery handoff index

Purpose: reconstruct the research program from this branch after a clean workspace reset. No secrets are stored here.

## Authorized scope

- Repository: `DevTunaSoft/reactos`, public. Destination: `docs/projectos/research/` only, on research branches.
- Never write OS implementation sources, root agent instructions, workflows, hooks, CI config or repository settings. No merges, no upstream submissions, no code import.
- Credentials: existing authorized `gh` CLI only. Required scope: `repo`. Token values are never stored in this branch; provide them through the host credential store.

## Recovery order

1. Verify remote identity: `git remote -v` must show `https://github.com/DevTunaSoft/reactos.git`.
2. Verify branch: `research/v7-wave1` stacked on `research/fork-archaeology-2026-11-26` (PR #1). Do not reset or force-push.
3. Read `STATUS_V7.md`, `WAVE1_REPORT.md`, `QUEUE_SNAPSHOT_V7.jsonl`, `COVERAGE_V7.md`, `FAILURE_MODE_INDEX_V7.jsonl`, `SOURCE_REGISTER_V7.jsonl`.
4. Restore the private operational state on the host: `queue_events.jsonl`, `queue_state.json`, and collector outputs. The queue tool reconstructs state from the ledger if `queue_state.json` is absent only after the ledger is replayed by the operator; never invent queue history.
5. Run `python tools/supervisor.py status` from the state directory. If `<state>/EMERGENCY_STOP` exists, stop and ask the owner before resuming.
6. Claim one task with a unique worker ID, do bounded research, append evidence, commit, push to the stacked branch, and verify the remote SHA with `git ls-remote`.

## Canonical records

- `FORK_NETWORK_V7.jsonl` — 2426 verified fork-network members with parent lineage status.
- `CANDIDATE_VALIDATION_V7.jsonl` — 999 prior name-search candidates, live status and network membership.
- `FINDINGS_V7.jsonl` — canonical findings with exact source, SHA, observed facts, classification and decision.
- `ISSUE_CORRELATION_V7.jsonl` — issue-to-fix records including one lead with no canonical issue ID.
- `REVALIDATION_V7.jsonl` — verification of inherited F-01..F-12 citations.
- `PATCH_EQUIVALENCE_V7.jsonl` — `git patch-id --stable` comparisons.
- `FAILURE_MODE_INDEX_V7.jsonl` — rejected/closed-unmerged attempts.
- `SOURCE_REGISTER_V7.jsonl` — source IDs, URLs, revisions, classification.
- `QUEUE_SNAPSHOT_V7.jsonl` — sanitized queue state.
- `tools/` — original research helpers.

## Operational limits from the directive

- Start with at most four research workers; six only with separate owner approval. Reduce under host pressure.
- Bounded browser pool: one shared isolated instance, at most two active pages where practical.
- Push meaningful sanitized progress at the end of each wave or at least hourly while material changes exist.
- Verify every push by reading the remote head; never claim cloud custody before verification.
- If the remote head changes, reconcile before pushing. No force push, no history rewrite, no deletion of remote records.
- All tests remain NOT RUN unless exact evidence exists; no test execution is authorized by this wave.

## Stop / pause

`EMERGENCY_STOP` in the private state directory prevents new claims until explicitly removed. It does not alter repository data. A paused scheduler must not be silently re-enabled.
