# ProjectOS V8 — directive inventory verification report

Audit time: 2026-11-28T00:25Z. Read-only inspection; no directive, scheduler, queue or worker was modified. No productive research was interrupted.

## Controlling state actually observed

- `private/state/directives/CONTROL.md` (SHA-256 `aa8902e6…a451`, 1177 bytes, mtime 2026-11-27T18:00:59Z) names **V8** as the controlling directive and **V7** as the preserved predecessor. Rule 5: every worker must read it and inherit the V8 checksum before claiming work.
- `private/state/directives/V8-master.md` (SHA-256 `ba45cc1830f5380…4693d`, 44797 bytes, mtime 2026-11-27T17:55:41Z) is the authoritative owner-supplied V8 source. An identical working copy is at `research_v7/state/CONTROLLING_DIRECTIVE_V8.md`; the public `docs/projectos/CONSOLIDATED_RESEARCH_DIRECTIVE_V8.md` is a derived rendering with SHA-256 `a0877189…ebf50b`.
- `private/state/directives/V7-master.md` (SHA-256 `c0cc1532…9ae`, mtime 2026-11-27T17:56:21Z) preserves V7, also published at GitHub commit `5c02f5c5`.
- The 731-row `private/state/requirements_matrix.jsonl` (SHA-256 `31e7d3bc…fe2`) binds `V8 sha256:ba45cc18…` to each obligation and contains 26 lines mentioning continuation obligations.

No additional directive file exists in `private/state/directives/` (only CONTROL.md, V7-master.md, V8-master.md, V8-master.sha256).

## "Immediate Operational Intervention and Research Redirection" directive

**NOT INCORPORATED AND NOT INHERITED.** The literal title was searched in `private/state`, `research_v7/state`, `Downloads`, Desktop, Documents, `cron/jobs.json`, the 731-row matrix, and 1968 persisted worker transcripts: zero matches. `session_search` returned zero indexed sessions, so chat-history search alone cannot confirm absence; the current conversation also contains no such directive. There is no receipt timestamp, checksum, storage location, precedence or worker prompt for it. It is recorded in the inventory as `NOT INCORPORATED INTO PERSISTENT CONTROL STATE`, not as a controlling instruction.

## Scheduler (actual configuration)

| Field | Observed |
|---|---|
| Job ID / name | `08b68a4bc9b8` / "ProjectOS V7 research continuity" |
| Enabled / state | `true` / scheduled; 14 completed repeats |
| Schedule | `every 60m`; last run 2026-11-27T18:14:34-06:00 `ok`, next 2026-11-27T18:50:38-06:00 |
| Deliver / workdir / skills | `origin` / `research_v7` / `projectos-private-audit` |
| Prompt length | 1779 characters |
| Prompt directive handling | Reads `state/CONTROL.md` and `state/CONTROLLING_DIRECTIVE_V8.md`, verifies SHA-256 `ba45cc18…` with `sha256sum`, reads V7 from the research branch and the private matrix; respects V8 section 24; keeps the four implementation agents and the Mission 365 orchestrator paused; checks `EMERGENCY_STOP`; verifies repo identity, branch and clean status; one shared browser with no sandbox-disabling flags; queue claim/commit/push/remote verification; replenishment and stalled-lease detection. |
| Continuity | Not enabled in job config; each fire gets a fresh session with the self-contained prompt above. |

The scheduler prompt does **not** mention the "Immediate Operational Intervention" directive, and does not state the owner's 3-subagent cap.

## Worker inheritance (actual, not intended)

- CONTROL.md rule 5 requires control-file read + checksum inheritance. The scheduler prompt enforces it for cron fires.
- Of 1968 persisted worker transcripts, the literal V8 checksum appears in 5 and `CONTROL.md` in 6. This is evidence of partial propagation, not universal enforcement.
- Last dispatched batch: the `V8F01-C04` prompt named V8 SHA `ba45cc18…` and that worker read CONTROL.md; the `W9-12` worker loaded `projectos-private-audit`, read CONTROL.md and hashed it; the `W9-11` worker loaded `grounded-citations` and did **not** read CONTROL.md during the observed transcript. All three were bounded research tasks under V8/V7 limits, but checksum inheritance was not identical.
- No live subagents were running at audit time (`delegate_task list`: count 0).

## Current supervisor and assignments

- Queue at 2026-11-28T00:13:44Z: 69 verified, 5 reviewed, **6 queued**, 0 running, 0 blocked, 0 stalled; 6 available now. Active assignments: `RPL-REVIEW-0011` (p3), `RPL-CORRELATION-0014`, `RPL-COVERAGE-0010`, `RPL-EVIDENCE-0009`, `RPL-FAILURE-0013` (p4), `RPL-PROVENANCE-0012` (p5).
- Only one scheduled job is enabled (the V7/V8 supervisor above); 13 others remain paused, including the four ProjectOS implementation agents and the private orchestrator.
- `EMERGENCY_STOP` was absent at the earlier check; no job was paused, cancelled or edited for this audit.
- Concurrency limits actually in force: V7 says up to 4 research workers and 6 only with approval; V8 says maximum sustainable within previously authorized limits; the owner's 3-subagent cap for this project exists only in conversation and Hermes memory, not in CONTROL.md, V8, the scheduler prompt, the matrix or worker prompts.
- Repository: local HEAD and remote `research/v7-wave1` were equal at `ae96ebb0165d0d0a65e84aca003cf0b7b2e4fc4e` at audit time (research continued during the audit; no push was made by this report).

## Instructions received in conversation but not persisted/propagated

1. The 3-subagent cap for this project (crons excluded) — memory only; not in persistent project control state or worker prompts.
2. The alleged "Immediate Operational Intervention and Research Redirection" directive — not received in any inspected channel, therefore nothing to persist or propagate.
3. This audit/report request is a task, not a directive; it does not change control state.
4. "Do not interrupt active research" is already represented in V8 (sections 1 and 28) and was honored: no job, worker, lease or queue entry was modified by this audit.

## Publication integrity

`DIRECTIVE_INVENTORY_V8.jsonl` is the sanitized machine-readable inventory. Private absolute paths, credential patterns and directive bodies are not published; only relative locations, titles, versions, receipt evidence, hashes, precedence and observed inheritance. This report is appended to the existing research branch; no master directive was created, rewritten or superseded.
