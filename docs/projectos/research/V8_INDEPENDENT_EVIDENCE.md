# ProjectOS V8 — independent corrective evidence

This checkpoint adds independent evidence for V8 priorities A, C and D. It supplements, rather than replaces, the supervisor's earlier `FORK_ANCESTRY_METHOD_V8.jsonl`, `ISOLATED_RECOVERY_V8.jsonl` and `PRODUCTION_RETRIEVAL_V8.jsonl` records.

## Priority A — fork ancestry supplement

- `FORK_ANCESTRY_SUPPLEMENT_V8.json`
- 24 tip SHAs examined from a 246-unique-SHA denominator; 12 exact-present, 11 inconclusive, 1 patch-equivalent.
- Methodology correction: HTTP 200 from a commit API proves object presence only. Reachability requires `git merge-base --is-ancestor` / `git branch --contains`; normalized patch identity requires `git patch-id --stable` on immutable `.patch` files; semantic equivalence requires source inspection.
- Verified example: `2fda8374a2e1c655272fcfd49465675377618bbc` is patch-equivalent to upstream cherry-pick `34c563fa2a2…`. At pinned baseline `3e6033a6`, `dll/win32/comctl32/button.c:1527` still calls `GetSysColorBrush(COLOR_BTNFACE)`, so the fork change is not an independent unfixed contribution.
- Coverage limitation: only 24/246 tips examined in this pass; 206 tip objects were unavailable locally. No claim of complete reassessment is made.

## Priority C — independent recovery exercise

- `INDEPENDENT_RECOVERY_V8.json`
- Remote and local head verified at `cc96564f9f9a1f8de84953938f10dc5ed68970e5` with `git ls-remote` and `git rev-parse`.
- 71 JSONL files / 7,812 records parsed with zero errors; 731 requirement rows validated; 64 queue snapshot records validated.
- Recovery resumed a bounded read-only assignment: upstream PR #9510 and PR #9341 were checked and both are closed unmerged, consistent with published records.
- Limitations: the live private queue mutated concurrently during the exercise; the worker used one hashed snapshot and made no active-queue claim. Published sanitized snapshot lagged private state by six V8 assignments at exercise time. These are recorded, not hidden.

## Priority D — research data integrity

- `DATA_INTEGRITY_CORRECTIONS_V8.jsonl` — 74 append-only proposed corrections (66 malformed hardware source URLs, 5 record-count discrepancies, 3 WoW64 summary inconsistencies; 73 high confidence, 1 medium).
- `tools/validate_research_artifacts.py` — read-only regression validator that detects JSON/JSONL errors, duplicate ids, malformed URLs, count mismatches, WoW64 summary inconsistencies and banned private/credential strings.
- Validator result on the published corpus: `files=106 json=3 jsonl=74 ids=3773 urls=6455 failures=74`. The 74 failures correspond to the 74 correction records; none were silently accepted.
- Important: corrections are append-only proposals. Historical research records are not rewritten, and no finding is marked accepted solely because a correction was proposed.

## Authorization status

Research only. No OS implementation change, OS test execution, patch import, merge, upstream submission, history rewrite, credential exposure or security-control bypass occurred.
