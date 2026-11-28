#!/usr/bin/env python3
"""Integrator adoption of evidence-backed tasks that agents completed in isolated ledgers.

Single-writer lock, append-only ledger event, atomic state replacement. No
attempt counter changes: no lease was held on these tasks in the live queue.
"""
import json
import os
import time
from datetime import datetime, timezone

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "state")
EVENTS = os.path.join(BASE, "queue_events.jsonl")
STATE = os.path.join(BASE, "queue_state.json")
LOCK = os.path.join(BASE, ".queue.lock")
WORKER = "integrator-adopt-20261127T0627Z"
ADOPT = {
    "W3-07": "PRESS_RECONCILIATION_V7.jsonl: VideoCardz claims checked against PR #9646 only; nightly and 0.4.16 runtime claims not verifiable from that PR",
    "W5-02": "REVIEWER_ASSIGNMENT_V7.jsonl, COUNT_RECONCILIATION_V7.jsonl, TERMINOLOGY_CORRECTION_V7.jsonl; supervisor_v2 32/32 isolated tests passed",
}


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main():
    os.makedirs(BASE, exist_ok=True)
    for _ in range(50):
        try:
            fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            break
        except FileExistsError:
            if time.time() - os.path.getmtime(LOCK) > 600:
                os.unlink(LOCK)
            else:
                time.sleep(0.2)
    st = json.load(open(STATE, encoding="utf-8"))
    ts = now()
    events = []
    for tid, ev in ADOPT.items():
        t = st["tasks"][tid]
        if t["status"] == "verified":
            continue
        t["status"] = "verified"
        t["evidence"] = ev
        t["lease_owner"] = None
        t["lease_id"] = None
        t["lease_until"] = None
        events.append({"ts": ts, "event": "integrator_adopt", "task": tid,
                       "worker": WORKER, "evidence": ev,
                       "note": "evidence produced by agent in isolated ledger; no live lease held"})
    st["updated"] = ts
    with open(EVENTS, "a", encoding="utf-8") as f:
        for e in events:
            f.write(json.dumps(e, sort_keys=True) + "\n")
    tmp = STATE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(st, f, indent=2, sort_keys=True)
        f.write("\n")
    os.replace(tmp, STATE)
    os.unlink(LOCK)
    print("adopted:", [e["task"] for e in events])
    counts = {}
    for t in st["tasks"].values():
        counts[t["status"]] = counts.get(t["status"], 0) + 1
    print("counts:", json.dumps(counts, sort_keys=True))


if __name__ == "__main__":
    main()
