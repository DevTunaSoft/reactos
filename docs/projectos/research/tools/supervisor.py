#!/usr/bin/env python3
"""ProjectOS V7 research queue supervisor (original, research-only helper).

Durable append-only event ledger + atomically materialized state. No network,
no credentials, no OS code access. Single-writer discipline via lockfile.
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

BASE = os.environ.get("PROJECTOS_V7_STATE",
                      os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "state"))
EVENTS = os.path.join(BASE, "queue_events.jsonl")
STATE = os.path.join(BASE, "queue_state.json")
LOCK = os.path.join(BASE, ".queue.lock")
STOP = os.path.join(BASE, "EMERGENCY_STOP")
LEASE_SECONDS = 900
MAX_ATTEMPTS = 3

STATUS = ("queued", "running", "verified", "blocked", "reviewed")


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def atomic_write(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


class Lock:
    def __init__(self):
        self.path = LOCK
        self.acquired = False

    def __enter__(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        for _ in range(50):
            try:
                fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                with os.fdopen(fd, "w") as f:
                    f.write(json.dumps({"pid": os.getpid(), "at": now()}))
                self.acquired = True
                return self
            except FileExistsError:
                try:
                    age = time.time() - os.path.getmtime(self.path)
                except OSError:
                    age = 0
                if age > 600:
                    try:
                        os.unlink(self.path)
                    except OSError:
                        pass
                else:
                    time.sleep(0.2)
        raise RuntimeError("queue lock busy")

    def __exit__(self, *exc):
        if self.acquired:
            try:
                os.unlink(self.path)
            except OSError:
                pass


def load():
    if not os.path.exists(STATE):
        return {"schema": 1, "tasks": {}, "cursors": {}, "updated": now()}
    with open(STATE, encoding="utf-8") as f:
        return json.load(f)


def event(kind, **kw):
    os.makedirs(BASE, exist_ok=True)
    rec = {"ts": now(), "event": kind}
    rec.update(kw)
    with open(EVENTS, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")
    return rec


def save(st, kind, **kw):
    st["updated"] = now()
    event(kind, **kw)
    atomic_write(STATE, st)


def seed(items):
    with Lock():
        st = load()
        added = 0
        for item in items:
            tid = item["id"]
            if tid in st["tasks"]:
                continue
            task = {
                "id": tid, "title": item.get("title", ""), "status": "queued",
                "lane": item.get("lane", ""), "priority": item.get("priority", 5),
                "attempts": 0, "lease_owner": None, "lease_until": None,
                "heartbeat": None, "next_action": item.get("next_action", ""),
                "evidence": None, "blocker": None, "created": now(),
            }
            st["tasks"][tid] = task
            added += 1
        if added:
            save(st, "seed", added=added)
    return added


def reclaim(st):
    t = time.time()
    freed = []
    for tid, task in st["tasks"].items():
        if task["status"] != "running":
            continue
        hb = task.get("heartbeat") or task.get("lease_until")
        try:
            age = t - time.mktime(time.strptime(hb, "%Y-%m-%dT%H:%M:%SZ"))
        except (TypeError, ValueError):
            age = 1e9
        if age > LEASE_SECONDS:
            if task["attempts"] >= MAX_ATTEMPTS:
                task["status"] = "blocked"
                task["blocker"] = "lease_expired_and_attempts_exhausted"
            else:
                task["status"] = "queued"
            task["lease_owner"] = None
            task["lease_until"] = None
            freed.append(tid)
    if freed:
        save(st, "lease_reclaimed", tasks=freed)
    return freed


def cmd_status(args):
    if os.path.exists(STOP):
        print("EMERGENCY STOP ACTIVE - no claims permitted")
    st = load()
    counts = {s: 0 for s in STATUS}
    for t in st["tasks"].values():
        counts[t["status"]] = counts.get(t["status"], 0) + 1
    print("updated:", st.get("updated"))
    print("counts:", json.dumps(counts, sort_keys=True))
    print("cursors:", json.dumps(st.get("cursors", {}), sort_keys=True))
    for tid, t in sorted(st["tasks"].items()):
        if t["status"] in ("queued", "running", "blocked"):
            print(f"  {tid:10s} {t['status']:8s} p{t['priority']} a{t['attempts']} :: {t['title'][:70]}")


def cmd_claim(args):
    if os.path.exists(STOP):
        print("BLOCKED: EMERGENCY_STOP present")
        return 2
    with Lock():
        st = load()
        reclaim(st)
        candidates = [t for t in st["tasks"].values() if t["status"] == "queued"]
        if not candidates:
            print("NO_QUEUED_TASKS")
            return 1
        candidates.sort(key=lambda t: (t["priority"], t["created"], t["id"]))
        t = candidates[0]
        t["status"] = "running"
        t["lease_owner"] = args.worker
        t["heartbeat"] = now()
        t["lease_until"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() + LEASE_SECONDS))
        save(st, "claim", task=t["id"], worker=args.worker)
        print(json.dumps(t, sort_keys=True))
    return 0


def cmd_beat(args):
    with Lock():
        st = load()
        t = st["tasks"].get(args.task)
        if not t:
            return 2
        t["heartbeat"] = now()
        t["lease_until"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() + LEASE_SECONDS))
        save(st, "heartbeat", task=args.task, worker=args.worker)
    return 0


def cmd_finish(args):
    with Lock():
        st = load()
        t = st["tasks"].get(args.task)
        if not t:
            return 2
        if args.fail:
            t["attempts"] += 1
            if t["attempts"] >= MAX_ATTEMPTS:
                t["status"] = "blocked"
                t["blocker"] = args.reason
            else:
                t["status"] = "queued"
            save(st, "fail", task=args.task, reason=args.reason, attempts=t["attempts"])
        elif args.block:
            t["status"] = "blocked"
            t["blocker"] = args.reason
            save(st, "block", task=args.task, reason=args.reason)
        else:
            t["status"] = "verified" if not args.review else "reviewed"
            t["evidence"] = args.evidence
            t["lease_owner"] = None
            t["lease_until"] = None
            save(st, "complete", task=args.task, evidence=args.evidence)
    return 0


def cmd_cursor(args):
    with Lock():
        st = load()
        st["cursors"][args.name] = json.loads(args.value)
        save(st, "cursor", name=args.name, value=args.value)
    return 0


def cmd_snapshot(args):
    st = load()
    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        for tid, t in sorted(st["tasks"].items()):
            row = {k: t.get(k) for k in ("id", "title", "lane", "priority", "status",
                                         "attempts", "next_action", "evidence", "blocker")}
            f.write(json.dumps(row, sort_keys=True) + "\n")
    print("snapshot:", args.out, len(st["tasks"]), "tasks")
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    s = sub.add_parser("seed")
    s.add_argument("file", help="JSON array of task objects")
    s = sub.add_parser("claim")
    s.add_argument("worker")
    s = sub.add_parser("beat")
    s.add_argument("task")
    s.add_argument("worker")
    s = sub.add_parser("finish")
    s.add_argument("task")
    s.add_argument("--evidence", default="")
    s.add_argument("--fail", action="store_true")
    s.add_argument("--block", action="store_true")
    s.add_argument("--review", action="store_true")
    s.add_argument("--reason", default="")
    s = sub.add_parser("cursor")
    s.add_argument("name")
    s.add_argument("value", help="JSON value")
    s = sub.add_parser("snapshot")
    s.add_argument("out")
    a = p.parse_args()
    if a.cmd == "status":
        return cmd_status(a)
    if a.cmd == "seed":
        with open(a.file, encoding="utf-8") as f:
            return print("seeded:", seed(json.load(f)))
    if a.cmd == "claim":
        return cmd_claim(a)
    if a.cmd == "beat":
        return cmd_beat(a)
    if a.cmd == "finish":
        return cmd_finish(a)
    if a.cmd == "cursor":
        return cmd_cursor(a)
    if a.cmd == "snapshot":
        return cmd_snapshot(a)
    return 1


if __name__ == "__main__":
    sys.exit(main() or 0)
