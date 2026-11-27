# ProjectOS V7 — infrastructure correction evidence (INFRA)

Research-only addendum. No OS implementation source, no tests/builds, no merges,
no pushes, no merge-conflict resolution and no upstream submissions. The live
`tools/supervisor.py`, live queue state and the canonical Wave 1 records were not
edited. All work was done on a copy and an isolated state directory.

## Supervisor v2 changes (`<private>/research_v7/tools/supervisor_v2.py`)

1. **UTC lease arithmetic** — `epoch_utc()` uses `calendar.timegm` on
   `%Y-%m-%dT%H:%M:%SZ`; timestamps are parsed as timezone-aware UTC
   (`datetime.strptime(...).replace(tzinfo=timezone.utc)`). No `time.mktime()` call
   remains. Under `TZ=EST5EDT`, local `mktime` differed from UTC by 18,000 s while
   supervisor status and lease checks were unchanged.
2. **Ownership and lease identity** — `beat`, `finish`, `complete` and `review`
   require the current `lease_owner` plus the exact `lease_id`, a live `lease_until`
   and a fresh heartbeat. Rejections emit `update_rejected` and exit 3 without
   mutating task state. Completion also requires non-empty evidence; review
   requires a reviewer different from the lease owner.
3. **Reclaim accounting** — expired leases increment `attempts`, clear lease
   fields and set `available_at` using bounded exponential backoff
   (`base * 2^(attempts-1)`, capped) before the task becomes claimable again.
4. **Stall detection** — a reclaim with no evidence and no progress heartbeat
   inside the stall window is marked `stalled: true` in the ledger and
   `stall_detected: true` on the task. `beat --progress-note` records meaningful
   progress and clears the flag; retry exhaustion blocks the task.
5. **`replenish`** — idempotent backlog seeding from a built-in research-only
   template when `queued < min_queued`, with unique `RPL-<KEY>-<seq>` ids and a
   persisted sequence cursor. An hourly supervisor can therefore continue without
   user interaction. `replay` rebuilds state from the append-only ledger and
   refuses partial reconstruction from legacy seed events that lack item bodies.
6. **Defensive scheduling** — claim re-checks active leases in the ledger
   immediately before selecting a task, so a concurrent writer cannot produce a
   duplicate claim.

## Test evidence

`python <repo>/docs/projectos/research/INFRA_SUPERVISOR_V2_TEST.py` against
`<private>/research_v7/state/infra_test/` with an injected UTC clock: **32/32
checks passed, exit 0**. Full command/output log:
`INFRA_SUPERVISOR_V2_TEST_LOG.txt`; machine results:
`INFRA_SUPERVISOR_V2_TEST_RESULTS.json`. Highlights:

- three workers claimed three distinct tasks with distinct lease ids;
- non-owner, wrong-lease, missing-evidence and self-review updates rejected;
- two expired leases reclaimed together, attempts incremented to 1,
  `available_at` advanced by bounded backoff, stall detected only on the task with
  no evidence/progress;
- reclaimed tasks reassigned to new owners and completed after a crash;
- replenish added 4 tasks, skipped when above threshold, then added 4 unique ids;
- replay of 22 ledger events rebuilt 11 tasks with identical status counts.

## Restoration and governance

- Clean shallow clone of `research/v7-wave1` matched remote head
  `8591a33b8bb808afcb1f47139ac4251871495d8f`; 18 canonical paths from
  `HANDOFF_V7.md` exist and parse; 0 secret/personal-path hits in published
  research records and 0 private operational artifacts in the clone:
  `INFRA_RESTORATION_V7.jsonl`.
- Cron job `08b68a4bc9b8` is `[active]`, every 60m, verified read-only:
  `INFRA_CRON_VERIFICATION_V7.jsonl`. The `cronjob_manage` tool was not exposed to
  this execution context; `hermes cron list` was used instead and nothing was changed.
- Reviewer role for FV7-009 and exact review scope:
  `REVIEWER_ASSIGNMENT_V7.jsonl`.
- Count reconciliation against the live ledger/state with exact discrepancies:
  `COUNT_RECONCILIATION_V7.jsonl`.
- Patch-id terminology correction and all affected records/lines:
  `TERMINOLOGY_CORRECTION_V7.jsonl`. `git patch-id --stable` equality means
  normalized patch equivalence, not byte identity.
