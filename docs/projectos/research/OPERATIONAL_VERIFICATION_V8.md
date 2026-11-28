# ProjectOS V8 — operational correction verification (observed 2026-11-28T02:12Z)

This reports observed configuration and tests after the binding 2026-11-28 operational supplement. It is not a new master directive and does not replace V7/V8. No research was interrupted.

## Control persistence and inheritance

| Artifact | SHA-256 (observed) | Storage | Inheritance evidence |
|---|---|---|---|
| V8 master | `ba45cc1830f5380…4693d` | private control state; scheduler-visible `CONTROLLING_DIRECTIVE_V8.md` | Cron prompt requires `sha256sum` check; supervisor `verify-control` gate |
| Operational correction | `f2e43b42e665853b…212` | private control state; scheduler-visible copy; public control bundle | Cron prompt names checksum; supervisor gate rejects stale control |
| CONTROL index | `d3785fdb9e115b81b…231` | private control state; scheduler-visible copy; public control bundle | Names V8 + supplement precedence and worker verification rule |
| V7 master | `c0cc15328ecb720…d979ae` | private control state; GitHub commit `5c02f5c5` | Scheduler prompt reads V7 from branch |

`python tools/supervisor.py verify-control` returned `ok: true` with all three mandatory hashes. A deliberate expectations tamper (V8 hash → zeros) produced `REJECTED: stale_control checksum_mismatch:V8_MASTER` with exit code 2; the expectations file was restored immediately. The live `tools/supervisor.py` is now the gated v3 implementation, and claims carry a `control_verified` field.

The public derived V8 file has SHA-256 `a0877189…ebf50b` because it is a sanitized rendering; the controlling source remains `ba45cc18…`. The manifest explains this difference. No secret or private host path is present in the published bundle.

## Supervisor, singleton and watchdog

- One enabled scheduled job: `08b68a4bc9b8`, now **every 10 minutes** (was hourly), `enabled=true`, 15 completed fires, `last_status=ok`, last run `2026-11-27T19:24:37-06:00`, next `2026-11-27T20:15:36-06:00`, deliver `origin`, workdir `research_v7`.
- Thirteen other jobs remain paused, including the four ProjectOS implementation agents and the Mission 365 orchestrator. `EMERGENCY_STOP` remains the operator brake.
- Bounded watchdog `tools/watchdog_v8.py` uses a stale threshold of 25 minutes, a 30-minute recovery cooldown, and refuses recovery while any lease is active. Live check: `stale=true, active_leases=1, would_recover=false`. With an idle test state and a stale jobs fixture: `stale=true, active_leases=0, would_recover=true`. No automatic recovery was fired, so no restart loop was created.
- Single-dispatch protection is the queue's unique lease IDs, `ledger_active_leases` skip logic and the prompt's "one supervisor, no nested delegation" rule. Actual subagent cap remains 3 for this project; crons are excluded from that number.

## Queue and lease recovery

- At 2026-11-28T02:12Z: 79 verified, 6 reviewed, 10 queued, 0 running, 0 blocked, 0 stalled. The ready reserve exceeds the required 6 specific assignments.
- Expired-lease recovery was tested earlier: v2 rejected late finishes with `lease_expired`; artifacts were adopted through append-only `integrator_expired_lease_recovery` events, the unfinished task was requeued, and a later supervisor fire completed it. Nothing was silently rewritten.
- W9-10 was reopened as `W9-10R` because its earlier evidence recorded zero fetched diffs and `unique changes NOT RUN`; it must not be marked verified without a performed analysis. `W10-13` (249/246 tip reconciliation) and `W10-14` (validator remeasurement) were added.

## Technical output and corrections

- Independent cron review upheld FV7-003: both immutable patches gave stable patch-id `ecb96617…`; PR #1965 merged 2019-10-30; precision correction retained that patch-id proves normalized, not byte, equivalence.
- FV7-007 `CONFIRMED_WITH_CORRECTIONS`; five prior tally/path errors corrected; F-04 head SHA `41b38f00` is diverged from the pin, with integration via merge `29f6b92f`.
- Four fork cohorts cover 57 forks; all sampled exact tip SHAs resolve upstream, and W9-10R now targets actual unique-change analysis. ARM64 PR #9809 was reclassified as an open upstream PR tip, not an independent implementation.

## Observed limitations

- At the time the supplement was propagated, one subagent was running. A course-correction message was attempted but that worker completed before delivery; no in-flight worker adopted the new control. No subagents are running now, and all future claims are gated by the supervisor. This is an honest adoption gap, not a claim of universal inheritance.
- Sustained dispatch across multiple turnovers after changing to 10-minute scheduling has not yet been observed; the next fire is scheduled. The scheduler mechanism is real and previously completed 15 fires, including one interrupted run that was manually recovered.
- No OS runtime test, build, VM boot, patch import, merge or upstream submission was performed. All research records remain NOT RUN for runtime.

Machine-readable evidence: `OPERATIONAL_VERIFICATION_V8.jsonl`. Authoritative bundle: `CONTROL_BUNDLE_V8/` with `MANIFEST_V8.json`.
