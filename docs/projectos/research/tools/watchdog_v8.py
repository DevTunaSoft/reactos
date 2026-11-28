#!/usr/bin/env python3
"""Bounded watchdog for the single ProjectOS research supervisor.

--check reports actual scheduler/lease state; --recover may fire one bounded
manual run only when stale, enabled, no active lease and cooldown elapsed.
No nested supervisor, no restart loop.
"""
import argparse
import json
import os
import subprocess
import time
from datetime import datetime, timezone

JOB = "08b68a4bc9b8"
JOBS = os.environ.get("PROJECTOS_V7_CRON_JOBS",
                      os.path.expanduser("~/AppData/Local/hermes/cron/jobs.json"))
STATE = os.environ.get("PROJECTOS_V7_STATE_DIR", os.path.join(os.getcwd(), "state"))
STALE_MIN = 25
COOLDOWN_MIN = 30


def utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_ts(value):
    if not value:
        return 0
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return 0


def load_job(path=JOBS):
    d = json.load(open(path, encoding="utf-8"))
    jobs = d["jobs"]
    return next((j for j in jobs if j.get("id") == JOB), None)


def queue_state():
    p = os.path.join(STATE, "queue_state.json")
    if not os.path.exists(p):
        return {}
    return json.load(open(p, encoding="utf-8"))


def check(path=JOBS):
    job = load_job(path)
    st = queue_state()
    running = sum(1 for t in st.get("tasks", {}).values() if t.get("status") == "running")
    now = time.time()
    last = parse_ts(job.get("last_run_at") if job else None)
    age_min = round((now - last) / 60, 1) if last else None
    stale = bool(job and job.get("enabled") and (not last or age_min >= STALE_MIN))
    result = {
        "checked": utc(), "job": JOB, "enabled": bool(job and job.get("enabled")),
        "last_run_at": job.get("last_run_at") if job else None, "age_min": age_min,
        "stale": stale, "active_leases": running,
        "would_recover": stale and running == 0,
        "note": "single supervisor; watchdog never starts a second concurrent dispatcher",
    }
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--check", action="store_true")
    p.add_argument("--recover", action="store_true")
    p.add_argument("--jobs", default=JOBS)
    a = p.parse_args()
    r = check(a.jobs)
    with open(os.path.join(STATE, "watchdog.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(r, sort_keys=True) + "\n")
    print(json.dumps(r, sort_keys=True))
    if not a.recover:
        return 0
    if not r["would_recover"]:
        print("RECOVERY_SKIPPED")
        return 0
    cooldown = os.path.join(STATE, "watchdog_last_recovery")
    if os.path.exists(cooldown) and time.time() - os.path.getmtime(cooldown) < COOLDOWN_MIN * 60:
        print("RECOVERY_SKIPPED cooldown")
        return 0
    with open(cooldown, "w", encoding="utf-8") as f:
        f.write(utc())
    proc = subprocess.run(["hermes", "cron", "run", JOB], capture_output=True, text=True, timeout=60)
    print("RECOVERY_FIRED rc", proc.returncode, proc.stdout.strip()[:200], proc.stderr.strip()[:200])
    return 0


if __name__ == "__main__":
    main()
