#!/usr/bin/env python3
"""Deterministic isolated QA harness for supervisor_v2.py.

Runs only against <private>/research_v7/state/infra_test/ with an
injected UTC clock. Never reads or writes the live research queue state.
"""
import calendar
import json
import os
import re
import shutil
import subprocess
import sys
import time

PY = sys.executable
# Paths are derived from this file's location; no host-specific literals.
OUT = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(OUT)))
PRIVATE_ROOT = os.path.join(os.path.dirname(os.path.dirname(REPO_ROOT)), "ProjectOS", "research_v7")
SUP = os.path.join(PRIVATE_ROOT, "tools", "supervisor_v2.py")
TEST_STATE = os.path.join(PRIVATE_ROOT, "state", "infra_test")
REPLAY_STATE = os.path.join(TEST_STATE, "replay_test")
LOG = os.path.join(OUT, "INFRA_SUPERVISOR_V2_TEST_LOG.txt")
RESULTS = os.path.join(OUT, "INFRA_SUPERVISOR_V2_TEST_RESULTS.json")

BASE_ENV = {
    "PROJECTOS_V7_STATE": TEST_STATE,
    "PROJECTOS_V7_LEASE_SECONDS": "5",
    "PROJECTOS_V7_STALL_SECONDS": "6",
    "PROJECTOS_V7_BACKOFF_BASE_SECONDS": "1",
    "PROJECTOS_V7_BACKOFF_MAX_SECONDS": "8",
    "PROJECTOS_V7_MAX_ATTEMPTS": "3",
    "PROJECTOS_V7_MIN_QUEUED": "2",
    "PROJECTOS_V7_TARGET_QUEUED": "4",
}

log_lines = []
checks = []
results = {}


def log(msg):
    log_lines.append(str(msg))
    print(msg)


def check(name, condition, detail=""):
    ok = bool(condition)
    checks.append({"check": name, "pass": ok, "detail": str(detail)})
    log("%s %s :: %s" % ("PASS" if ok else "FAIL", name, detail))
    return ok


def clean():
    for name in ("queue_events.jsonl", "queue_state.json", ".queue.lock", "EMERGENCY_STOP"):
        p = os.path.join(TEST_STATE, name)
        if os.path.isfile(p):
            os.unlink(p)
    if os.path.isdir(REPLAY_STATE):
        shutil.rmtree(REPLAY_STATE)
    os.makedirs(TEST_STATE, exist_ok=True)


def run(args, now, state=None, extra_env=None):
    env = os.environ.copy()
    env.update(BASE_ENV)
    env["PROJECTOS_V7_NOW"] = now
    if state:
        env["PROJECTOS_V7_STATE"] = state
    if extra_env:
        env.update(extra_env)
    cmd = [PY, SUP] + args
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", env=env, timeout=60)
    log("$ PROJECTOS_V7_NOW=%s python supervisor_v2.py %s  [exit=%d]" %
        (now, " ".join(args), proc.returncode))
    for line in (proc.stdout or "").splitlines():
        log("  OUT " + line)
    for line in (proc.stderr or "").splitlines():
        log("  ERR " + line)
    return proc


def state():
    with open(os.path.join(TEST_STATE, "queue_state.json"), encoding="utf-8") as f:
        return json.load(f)


def events():
    with open(os.path.join(TEST_STATE, "queue_events.jsonl"), encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def main():
    clean()
    seed_path = os.path.join(TEST_STATE, "tasks_seed_infra.json")
    with open(seed_path, "w", encoding="utf-8") as f:
        json.dump([
            {"id": "INFRA-01", "title": "UTC lease proof A", "lane": "QA", "priority": 0,
             "next_action": "Verify UTC lease arithmetic."},
            {"id": "INFRA-02", "title": "Ownership proof B", "lane": "QA", "priority": 1,
             "next_action": "Verify owner and lease identity checks."},
            {"id": "INFRA-03", "title": "Crash recovery proof C", "lane": "QA", "priority": 2,
             "next_action": "Verify expired-lease reclaim and retry accounting."},
        ], f, indent=2)

    run(["status"], "2026-11-27T12:00:00Z")
    run(["seed", seed_path], "2026-11-27T12:00:00Z")
    check("seed 3 isolated tasks", len(state()["tasks"]) == 3)

    c1 = run(["claim", "worker-A"], "2026-11-27T12:00:01Z")
    lease_a = json.loads(c1.stdout.strip())["lease_id"]
    c2 = run(["claim", "worker-B"], "2026-11-27T12:00:02Z")
    lease_b = json.loads(c2.stdout.strip())["lease_id"]
    c3 = run(["claim", "worker-C"], "2026-11-27T12:00:03Z")
    lease_c = json.loads(c3.stdout.strip())["lease_id"]
    claims = [json.loads(line) for line in (c1.stdout + c2.stdout + c3.stdout).splitlines() if line.strip()]
    check("unclaimed scheduling: three workers, three distinct tasks and lease ids",
          len({c["id"] for c in claims}) == 3 and len({c["lease_id"] for c in claims}) == 3,
          [c["id"] for c in claims])

    r = run(["beat", "--task", "INFRA-01", "--worker", "worker-Z", "--lease-id", lease_a],
            "2026-11-27T12:00:04Z")
    check("non-owner beat rejected", r.returncode == 3 and "not_owner" in r.stdout, r.stdout.strip())
    r = run(["beat", "--task", "INFRA-01", "--worker", "worker-A", "--lease-id", "bogus"],
            "2026-11-27T12:00:04Z")
    check("wrong lease id beat rejected", r.returncode == 3 and "lease_identity_mismatch" in r.stdout,
          r.stdout.strip())
    r = run(["beat", "--task", "INFRA-01", "--worker", "worker-A", "--lease-id", lease_a],
            "2026-11-27T12:00:04Z")
    check("owner beat accepted", r.returncode == 0)

    r = run(["finish", "--task", "INFRA-01", "--worker", "worker-A", "--lease-id", lease_a],
            "2026-11-27T12:00:05Z")
    check("completion without evidence rejected", r.returncode == 3 and "evidence_required" in r.stdout,
          r.stdout.strip())
    r = run(["complete", "--task", "INFRA-01", "--worker", "worker-A", "--lease-id", lease_a,
             "--evidence", "PASS UTC lease arithmetic with injected clock"], "2026-11-27T12:00:05Z")
    check("complete with evidence accepted", r.returncode == 0)
    r = run(["complete", "--task", "INFRA-01", "--worker", "worker-A", "--lease-id", lease_a,
             "--evidence", "duplicate"], "2026-11-27T12:00:06Z")
    check("replayed completion rejected (not_running)", r.returncode == 3 and "not_running" in r.stdout)

    r = run(["beat", "--task", "INFRA-02", "--worker", "worker-B", "--lease-id", lease_b,
             "--progress-note", "primary source verified"], "2026-11-27T12:00:06Z")
    check("meaningful progress heartbeat accepted", r.returncode == 0)

    r = run(["claim", "worker-D"], "2026-11-27T12:00:11Z")
    st = state()
    reclaim_ev = [e for e in events() if e["event"] == "lease_reclaimed"][0]
    check("expired leases reclaimed on claim", r.returncode == 1 and
          set(reclaim_ev["tasks"]) == {"INFRA-02", "INFRA-03"}, reclaim_ev["tasks"])
    check("retry attempts incremented on reclaim",
          all(st["tasks"][t]["attempts"] == 1 for t in ("INFRA-02", "INFRA-03")),
          {t: st["tasks"][t]["attempts"] for t in ("INFRA-02", "INFRA-03")})
    check("bounded backoff available_at set",
          all(st["tasks"][t]["available_at"] == "2026-11-27T12:00:12Z" for t in ("INFRA-02", "INFRA-03")),
          {t: st["tasks"][t]["available_at"] for t in ("INFRA-02", "INFRA-03")})
    check("stall detected only with no evidence/progress",
          st["tasks"]["INFRA-03"]["stall_detected"] is True and
          st["tasks"]["INFRA-02"]["stall_detected"] is False,
          {t: st["tasks"][t]["stall_detected"] for t in ("INFRA-02", "INFRA-03")})
    check("reclaimed leases cleared", all(st["tasks"][t]["lease_owner"] is None and
          st["tasks"][t]["lease_id"] is None for t in ("INFRA-02", "INFRA-03")))

    r = run(["claim", "worker-D"], "2026-11-27T12:00:12Z")
    d2 = json.loads(r.stdout.strip())
    r = run(["claim", "worker-E"], "2026-11-27T12:00:13Z")
    e3 = json.loads(r.stdout.strip())
    check("automatic crash recovery: reclaimed tasks reassignable",
          d2["id"] == "INFRA-02" and e3["id"] == "INFRA-03" and
          d2["attempts"] == 1 and e3["attempts"] == 1,
          {"worker-D": d2["id"], "worker-E": e3["id"]})

    r = run(["beat", "--task", "INFRA-03", "--worker", "worker-C", "--lease-id", lease_c],
            "2026-11-27T12:00:14Z")
    check("stale owner after reclaim rejected", r.returncode == 3 and "not_owner" in r.stdout)
    r = run(["beat", "--task", "INFRA-03", "--worker", "worker-E", "--lease-id", "wrong"],
            "2026-11-27T12:00:14Z")
    check("new owner wrong lease rejected", r.returncode == 3 and "lease_identity_mismatch" in r.stdout)
    r = run(["complete", "--task", "INFRA-03", "--worker", "worker-E", "--lease-id", e3["lease_id"],
             "--evidence", "PASS crash recovery after expired lease"], "2026-11-27T12:00:15Z")
    check("recovered owner can complete", r.returncode == 0)
    r = run(["review", "--task", "INFRA-02", "--worker", "worker-D", "--lease-id", d2["lease_id"],
             "--evidence", "x", "--reviewer", "worker-D"], "2026-11-27T12:00:16Z")
    check("self-review rejected", r.returncode == 3 and "reviewer_must_be_independent" in r.stdout)
    r = run(["review", "--task", "INFRA-02", "--worker", "worker-D", "--lease-id", d2["lease_id"],
             "--evidence", "PASS independent evidence review", "--reviewer", "reviewer-INFR"],
            "2026-11-27T12:00:16Z")
    check("independent review accepted", r.returncode == 0)
    check("reviewed status recorded", state()["tasks"]["INFRA-02"]["status"] == "reviewed")

    r = run(["replenish"], "2026-11-27T12:00:17Z")
    first_ids = [tid for tid in state()["tasks"] if tid.startswith("RPL-")]
    check("replenish seeds backlog when queue is empty", len(first_ids) == 4, first_ids)
    r = run(["replenish"], "2026-11-27T12:00:18Z")
    check("replenish idempotent above threshold", "REPLENISH_SKIPPED" in r.stdout and
          len([t for t in state()["tasks"] if t.startswith("RPL-")]) == 4)
    r = run(["replenish", "--min-queued", "6", "--target", "8"], "2026-11-27T12:00:19Z")
    all_ids = [tid for tid in state()["tasks"] if tid.startswith("RPL-")]
    check("replenish generates unique next batch", len(all_ids) == 8 and
          len(set(all_ids)) == 8 and "RPL-EVIDENCE-0005" in all_ids, all_ids)

    with open(SUP, encoding="utf-8") as f:
        source = f.read()
    check("no local-time mktime call in supervisor_v2.py", not re.search(r"time\.mktime\(", source))
    check("calendar.timegm and timezone-aware UTC used",
          "calendar.timegm" in source and "timezone.utc" in source)
    sample = "2026-11-27T12:00:00Z"
    expected = calendar.timegm(time.strptime(sample, "%Y-%m-%dT%H:%M:%SZ"))
    import importlib.util
    spec = importlib.util.spec_from_file_location("supervisor_v2_under_test", SUP)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    check("UTC epoch equals calendar.timegm (locale/TZ independent)",
          mod.epoch_utc(sample) == expected, {"epoch_utc": mod.epoch_utc(sample), "timegm": expected})
    old_tz = os.environ.get("TZ")
    os.environ["TZ"] = "EST5EDT"
    if hasattr(time, "tzset"):
        time.tzset()
    local = time.mktime(time.strptime(sample, "%Y-%m-%dT%H:%M:%SZ"))
    log("TZ=EST5EDT local mktime(%s)=%s vs UTC timegm=%s (difference=%s s); "
        "supervisor uses the UTC value" % (sample, local, expected, local - expected))
    if old_tz is None:
        os.environ.pop("TZ", None)
    else:
        os.environ["TZ"] = old_tz
    if hasattr(time, "tzset"):
        time.tzset()

    r = run(["status"], "2026-11-27T12:00:20Z", extra_env={"TZ": "EST5EDT"})
    check("status under non-UTC TZ unchanged", r.returncode == 0 and '"queued": 8' in r.stdout)

    snap = os.path.join(TEST_STATE, "INFRA_SNAPSHOT.jsonl")
    r = run(["snapshot", snap], "2026-11-27T12:00:21Z")
    with open(snap, encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]
    check("snapshot has all isolated tasks", len(rows) == 11, len(rows))

    os.makedirs(REPLAY_STATE, exist_ok=True)
    shutil.copyfile(os.path.join(TEST_STATE, "queue_events.jsonl"),
                    os.path.join(REPLAY_STATE, "queue_events.jsonl"))
    r = run(["replay"], "2026-11-27T12:00:22Z", state=REPLAY_STATE)
    with open(os.path.join(REPLAY_STATE, "queue_state.json"), encoding="utf-8") as f:
        replayed = json.load(f)
    original = state()
    counts = lambda s: {k: sum(1 for t in s["tasks"].values() if t["status"] == k)
                        for k in ("queued", "running", "verified", "blocked", "reviewed")}
    check("replay rebuilds state from ledger", r.returncode == 0 and
          counts(replayed) == counts(original),
          {"replayed": counts(replayed), "original": counts(original)})
    reclaim_rows = [e for e in events() if e["event"] == "lease_reclaimed"]
    check("replay preserves retry facts and ledger stall evidence",
          replayed["tasks"]["INFRA-03"]["attempts"] == 1 and
          original["tasks"]["INFRA-03"]["attempts"] == 1 and
          reclaim_rows[0]["details"]["INFRA-03"]["stalled"] is True and
          replayed["tasks"]["INFRA-03"]["stall_detected"] ==
          original["tasks"]["INFRA-03"]["stall_detected"],
          json.dumps({"attempts": replayed["tasks"]["INFRA-03"]["attempts"],
                      "stall_in_ledger": reclaim_rows[0]["details"]["INFRA-03"]["stalled"],
                      "stall_state": replayed["tasks"]["INFRA-03"]["stall_detected"]}, sort_keys=True))

    ev = events()
    active = {}
    duplicate = []
    for e in ev:
        tids = [e["task"]] if e.get("task") else list(e.get("tasks") or [])
        for tid in tids:
            if e["event"] == "claim":
                if tid in active:
                    duplicate.append(tid)
                active[tid] = e.get("lease_id")
            elif e["event"] in ("lease_reclaimed", "fail", "block", "complete", "review"):
                active.pop(tid, None)
    check("ledger shows no overlapping un-released leases", not duplicate, duplicate)
    log("CLAIM_EVIDENCE " + json.dumps([{k: e.get(k) for k in ("ts", "event", "task", "worker", "lease_id")}
                                        for e in ev if e["event"] == "claim"], sort_keys=True))
    log("RECLAIM_EVIDENCE " + json.dumps([e for e in ev if e["event"] == "lease_reclaimed"], sort_keys=True))
    log("REJECT_EVIDENCE " + json.dumps([{k: e.get(k) for k in ("ts", "action", "worker", "reason")}
                                         for e in ev if e["event"] == "update_rejected"], sort_keys=True))
    log("REPLENISH_EVIDENCE " + json.dumps([{k: e.get(k) for k in
                                             ("ts", "event", "added", "queued_before", "queued_after")}
                                            for e in ev if e["event"].startswith("replenish")], sort_keys=True))
    return 0 if all(c["pass"] for c in checks) else 1


if __name__ == "__main__":
    try:
        rc = main()
    except Exception as exc:  # log harness errors too
        log("HARNESS_ERROR %r" % exc)
        rc = 1
    results = {"state_dir": "<private>/research_v7/state/infra_test",
               "supervisor": "<private>/research_v7/tools/supervisor_v2.py",
               "clock": "injected PROJECTOS_V7_NOW",
               "checks": checks, "passed": sum(1 for c in checks if c["pass"]),
               "total": len(checks), "exit_code": rc}
    with open(RESULTS, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, sort_keys=True)
        f.write("\n")
    log("SUMMARY %d/%d checks passed; exit=%d" % (results["passed"], results["total"], rc))
    def sanitize(line):
        return line.replace(PRIVATE_ROOT, "<private>/research_v7").replace(REPO_ROOT, "<repo>")

    with open(LOG, "w", encoding="utf-8") as f:
        f.write("\n".join(sanitize(line) for line in log_lines) + "\n")
    sys.exit(rc)
