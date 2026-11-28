# ProjectOS V7/V8 supervisor checkpoint — 2026-11-28T11:18Z

## Control
- Verified from authoritative copies: CONTROL `d3785fdb9e115b81bfc2348793a0757fa7ce55acba8b1569f46d07bbb8a4e231`, V8_MASTER `ba45cc1830f5380c88a0f27f7de2e0794feb3b8d612864a59808aa7a5924693d`, OPERATIONAL_CORRECTION `f2e43b42e665853b494c05ef3eeaf9e3d9f9504f5656592267f646719baaa212`; supervisor `verify-control` ok=true. No EMERGENCY_STOP.
- Branch `research/v7-wave1`, origin `https://github.com/DevTunaSoft/reactos.git`; implementation agents and Mission 365 orchestrator remain paused.

## Watchdog / dispatch
- `watchdog_v8.py --check`: singleton job `08b68a4bc9b8`, enabled=true, one active lease, would_recover=false. No second dispatcher started.
- Replenished queue 5 -> 9 ready before claiming (`replenish --min-queued 6 --target 12`, cursor 54).

## Completed in this fire
- **W12-15 verified** by worker `cron-20261128T110609Z-w12-15-security-auth-crypto-6e1f8a`, lease `f0d4fdf652904ee4928b21d26aea5ec6`, finished inside lease. Artifact `docs/projectos/research/SECURITY_AUTH_CRYPTO_OPEN_W12_V8.jsonl`: 370 records, 785,789 bytes, SHA-256 `87b8ace48cab2782c2507081b973a1f146febc8d209a480a4bff5a2365f70732`; 10 JIRA query lanes (140 unique issues, 0 errors), 9 GitHub searches, 162 open PR file lists paginated with 0 errors, 5 strict do-not-duplicate opens, 7 broad-keyword false positives, 18 byte-identical pin/master blobs. All six runtime fields NOT RUN.
- Publication commit `3311ffd7dafae53971c013f6959558fbd1f852b0`; `git ls-remote` matched local HEAD at push time. Remote head had advanced to `12c9f09ae77` by a concurrent writer mid-run; no alignment push was made.

## Observations / unfinished
- A first multi-claim script was killed by a 60 s tool timeout after lowering W12-16 priority but before claiming it. W12-16 priority was restored to 4 by append-only event `w12_16_interrupted_claim_priority_restored`; the task was never claimed and remains dependency-ready. RPL-EVIDENCE-0047 also remains queued.
- W12-19 remained running under its pre-existing lease `bc4603bc2ae847e09454aa7338f124a0` and was not touched.
- Validator: `SUMMARY files=219 json=7 jsonl=170 ids=13828 urls=64253 failures=143`; zero FAIL lines name the new artifact. 143 is the unchanged pre-existing failure count.
- Research-only limits observed: no OS code, patch import, test, merge, upstream submission, credential use or access-control bypass.
