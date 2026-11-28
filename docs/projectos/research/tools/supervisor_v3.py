#!/usr/bin/env python3
"""ProjectOS V7 research queue supervisor v2 (isolated, research-only copy).

Fixes over tools/supervisor.py: UTC-only lease arithmetic, worker+lease identity
on every mutation, retry increment on expired-lease reclaim, bounded exponential
backoff via available_at, meaningful-progress stall detection, and an idempotent
replenish command for unattended hourly continuation. No network, no credentials,
no OS code access. The live supervisor.py and live state are never touched here.

Test-only knobs (never set in production): PROJECTOS_V7_NOW=<UTC Z timestamp>,
PROJECTOS_V7_LEASE_SECONDS, PROJECTOS_V7_STALL_SECONDS,
PROJECTOS_V7_BACKOFF_BASE_SECONDS, PROJECTOS_V7_BACKOFF_MAX_SECONDS.
"""
import argparse
import calendar
import hashlib
import json
import os
import sys
import time
import uuid
from datetime import datetime, timedelta, timezone

FMT = "%Y-%m-%dT%H:%M:%SZ"
BASE = os.environ.get(
    "PROJECTOS_V7_STATE",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "state"),
)
EVENTS = os.path.join(BASE, "queue_events.jsonl")
STATE = os.path.join(BASE, "queue_state.json")
LOCK = os.path.join(BASE, ".queue.lock")
STOP = os.path.join(BASE, "EMERGENCY_STOP")
STATUS = ("queued", "running", "verified", "blocked", "reviewed")


def cfg(name, default):
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


LEASE_SECONDS = cfg("PROJECTOS_V7_LEASE_SECONDS", 900)
STALL_SECONDS = cfg("PROJECTOS_V7_STALL_SECONDS", 6 * 3600)
BACKOFF_BASE = cfg("PROJECTOS_V7_BACKOFF_BASE_SECONDS", 60)
BACKOFF_MAX = cfg("PROJECTOS_V7_BACKOFF_MAX_SECONDS", 3600)
MAX_ATTEMPTS = cfg("PROJECTOS_V7_MAX_ATTEMPTS", 3)
MIN_QUEUED = cfg("PROJECTOS_V7_MIN_QUEUED", 3)
TARGET_QUEUED = cfg("PROJECTOS_V7_TARGET_QUEUED", 6)
LOCK_STALE_SECONDS = 600


class Reject(Exception):
    """An ownership, lease or evidence precondition failed; no state change."""


def parse_utc(value):
    if not isinstance(value, str):
        raise ValueError("not a UTC timestamp")
    return datetime.strptime(value, FMT).replace(tzinfo=timezone.utc)


def utc_now():
    injected = os.environ.get("PROJECTOS_V7_NOW")
    return parse_utc(injected) if injected else datetime.now(timezone.utc)


def stamp(dt=None):
    return (dt or utc_now()).strftime(FMT)


def epoch_utc(value):
    """UTC epoch seconds. NEVER time.mktime (local-time interpretation)."""
    return calendar.timegm(time.strptime(value, FMT))


def age_seconds(value):
    return epoch_utc(stamp()) - epoch_utc(value)


def plus_seconds(value, seconds):
    return stamp(parse_utc(value) + timedelta(seconds=seconds))


def backoff(attempts):
    """Bounded exponential delay: base*2^(attempts-1), capped at BACKOFF_MAX."""
    return min(BACKOFF_MAX, BACKOFF_BASE * (2 ** max(0, int(attempts) - 1)))


def atomic_write(path, obj):
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
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
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    f.write(json.dumps({"pid": os.getpid(), "at": stamp()}, sort_keys=True))
                self.acquired = True
                return self
            except FileExistsError:
                try:
                    with open(self.path, encoding="utf-8") as f:
                        at = json.load(f).get("at")
                    stale = not at or age_seconds(at) > LOCK_STALE_SECONDS
                except (OSError, ValueError, TypeError):
                    stale = True
                if stale:
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
        return {"schema": 2, "tasks": {}, "cursors": {}, "updated": stamp()}
    with open(STATE, encoding="utf-8") as f:
        return json.load(f)


def read_events():
    if not os.path.exists(EVENTS):
        return []
    with open(EVENTS, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def event(kind, **kw):
    os.makedirs(BASE, exist_ok=True)
    rec = {"ts": stamp(), "event": kind}
    rec.update(kw)
    with open(EVENTS, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")
    return rec


def save(st, kind, **kw):
    st["updated"] = stamp()
    event(kind, **kw)
    atomic_write(STATE, st)


def new_task(item, when=None):
    ts = stamp(when)
    return {
        "id": item["id"],
        "title": item.get("title", ""),
        "status": "queued",
        "lane": item.get("lane", ""),
        "priority": item.get("priority", 5),
        "attempts": 0,
        "lease_owner": None,
        "lease_id": None,
        "lease_until": None,
        "heartbeat": None,
        "progress_at": None,
        "stall_detected": False,
        "available_at": ts,
        "next_action": item.get("next_action", ""),
        "evidence": None,
        "blocker": None,
        "reviewer": None,
        "created": ts,
    }


def cleanup_lease(task):
    task["lease_owner"] = None
    task["lease_id"] = None
    task["lease_until"] = None


def require_owner(task, worker, lease_id, action):
    """All mutations must come from the current owner with the live lease id."""
    if not task:
        raise Reject("unknown_task")
    if task.get("status") != "running":
        raise Reject("not_running")
    if not worker or task.get("lease_owner") != worker:
        raise Reject("not_owner")
    if not lease_id or task.get("lease_id") != lease_id:
        raise Reject("lease_identity_mismatch")
    hb = task.get("heartbeat")
    until = task.get("lease_until")
    if not hb or not until:
        raise Reject("missing_lease")
    now_epoch = epoch_utc(stamp())
    if now_epoch >= epoch_utc(until) or age_seconds(hb) > LEASE_SECONDS:
        raise Reject("lease_expired")


def ledger_active_leases():
    """Defensive re-check against a concurrent writer between status and claim."""
    active = {}
    for ev in read_events():
        tids = [ev["task"]] if ev.get("task") else list(ev.get("tasks") or [])
        for tid in tids:
            if ev["event"] == "claim":
                active[tid] = {"ts": ev["ts"], "lease_id": ev.get("lease_id")}
            elif ev["event"] in ("lease_reclaimed", "fail", "block", "complete", "review"):
                active.pop(tid, None)
    return active


def reclaim(st):
    now = stamp()
    now_epoch = epoch_utc(now)
    freed, details = [], {}
    for tid, task in st["tasks"].items():
        if task.get("status") != "running":
            continue
        hb = task.get("heartbeat")
        until = task.get("lease_until")
        expiry = epoch_utc(until) if until else (epoch_utc(hb) + LEASE_SECONDS if hb else 0)
        heartbeat_fresh = bool(hb) and age_seconds(hb) <= LEASE_SECONDS
        if now_epoch < expiry and heartbeat_fresh:
            continue
        attempts = int(task.get("attempts", 0)) + 1
        progress_at = task.get("progress_at")
        stalled = (
            not task.get("evidence")
            and (not progress_at or now_epoch - epoch_utc(progress_at) > STALL_SECONDS)
            and not heartbeat_fresh
        )
        delay = backoff(attempts)
        task["attempts"] = attempts
        task["stall_detected"] = stalled
        task["available_at"] = plus_seconds(now, delay)
        if attempts >= MAX_ATTEMPTS:
            task["status"] = "blocked"
            task["blocker"] = "stalled_retry_exhausted" if stalled else "lease_expired_retry_exhausted"
        else:
            task["status"] = "queued"
            task["blocker"] = "stalled_no_meaningful_progress" if stalled else None
        cleanup_lease(task)
        freed.append(tid)
        details[tid] = {
            "attempts": attempts,
            "backoff_seconds": delay,
            "available_at": task["available_at"],
            "stalled": stalled,
            "status": task["status"],
        }
    if details:
        save(st, "lease_reclaimed", tasks=freed, details=details)
    return details



CONTROL_DIR = os.environ.get(
    "PROJECTOS_V7_CONTROL_DIR",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "state"),
)
MANDATORY_CONTROLS = ("V8_MASTER", "OPERATIONAL_CORRECTION", "CONTROL")


def control_status():
    """Return (ok, detail): verify authoritative checksums before any claim."""
    exp_path = os.path.join(CONTROL_DIR, "control_expectations.json")
    if not os.path.exists(exp_path):
        return False, "expectations_missing"
    try:
        exp = json.load(open(exp_path, encoding="utf-8"))["files"]
    except Exception as exc:
        return False, "expectations_unreadable:" + type(exc).__name__
    verified = {}
    for name in MANDATORY_CONTROLS:
        spec = exp.get(name)
        if not spec:
            return False, "expectation_missing:" + name
        path = os.path.join(CONTROL_DIR, spec["path"])
        if not os.path.exists(path):
            return False, "control_file_missing:" + name
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        actual = h.hexdigest()
        if actual != spec["sha256"]:
            return False, "checksum_mismatch:" + name
        verified[name] = actual[:12]
    return True, verified


def cmd_verify_control(args):
    ok, detail = control_status()
    print(json.dumps({"ok": ok, "detail": detail}, sort_keys=True))
    return 0 if ok else 2


def cmd_status(args):
    if os.path.exists(STOP):
        print("EMERGENCY STOP ACTIVE - no claims permitted")
    st = load()
    counts = {s: 0 for s in STATUS}
    for task in st["tasks"].values():
        counts[task["status"]] = counts.get(task["status"], 0) + 1
    now_epoch = epoch_utc(stamp())
    waiting = [tid for tid, t in st["tasks"].items()
               if t["status"] == "queued" and epoch_utc(t.get("available_at", stamp())) <= now_epoch]
    print("updated:", st.get("updated"))
    print("counts:", json.dumps(counts, sort_keys=True))
    print("available_now:", len(waiting), "stalled:",
          sum(1 for t in st["tasks"].values() if t.get("stall_detected")))
    print("cursors:", json.dumps(st.get("cursors", {}), sort_keys=True))
    print("ledger_active_leases:", len(ledger_active_leases()))
    for tid, t in sorted(st["tasks"].items()):
        if t["status"] in ("queued", "running", "blocked"):
            print("  %-18s %-8s p%s a%s avail=%s%s" % (
                tid, t["status"], t["priority"], t["attempts"],
                t.get("available_at"), " STALLED" if t.get("stall_detected") else ""))


def cmd_seed(args):
    with open(args.file, encoding="utf-8") as f:
        items = json.load(f)
    with Lock():
        st = load()
        added = []
        for item in items:
            tid = item["id"]
            if tid in st["tasks"]:
                continue
            st["tasks"][tid] = new_task(item)
            added.append(tid)
        if added:
            save(st, "seed", added=len(added), items=[
                {k: v for k, v in item.items() if k in ("id", "title", "lane", "priority", "next_action")}
                for item in items if item["id"] in added
            ])
    print("seeded:", len(added), json.dumps(added, sort_keys=True))
    return 0


DEFAULT_TEMPLATE = [
    {"key": "EVIDENCE", "title": "Re-check canonical evidence against immutable SHAs",
     "lane": "D", "priority": 5,
     "next_action": "Re-read one canonical record and verify its cited immutable SHA; append corrections only."},
    {"key": "COVERAGE", "title": "Extend coverage matrix with explicit denominators",
     "lane": "B", "priority": 5,
     "next_action": "Record searched lanes, retrieval URLs and explicit unknown counts; no inference."},
    {"key": "REVIEW", "title": "Independent evidence review of a pending finding",
     "lane": "D", "priority": 4,
     "next_action": "Assign a reviewer independent of the original researcher; cite exact source lines."},
    {"key": "PROVENANCE", "title": "Revalidate source provenance and licensing metadata",
     "lane": "C", "priority": 5,
     "next_action": "Verify source URL, revision and license from primary records; record uncertainty."},
]


def cmd_replenish(args):
    template = DEFAULT_TEMPLATE
    if args.template:
        with open(args.template, encoding="utf-8") as f:
            template = json.load(f)
    with Lock():
        st = load()
        queued = sum(1 for t in st["tasks"].values() if t["status"] == "queued")
        if queued >= args.min_queued:
            save(st, "replenish_skipped", queued=queued, min_queued=args.min_queued,
                 reason="backlog_above_threshold")
            print("REPLENISH_SKIPPED queued=%d min_queued=%d" % (queued, args.min_queued))
            return 0
        need = max(0, args.target - queued)
        seq = int(st.get("cursors", {}).get("replenish_seq", 0))
        added, items = [], []
        for tpl in template[:need]:
            seq += 1
            tid = "RPL-%s-%04d" % (tpl["key"], seq)
            if tid in st["tasks"]:
                continue
            item = dict(tpl)
            item["id"] = tid
            st["tasks"][tid] = new_task(item)
            added.append(tid)
            items.append({k: item.get(k) for k in ("id", "title", "lane", "priority", "next_action")})
        st.setdefault("cursors", {})["replenish_seq"] = seq
        if added:
            save(st, "replenish", added=len(added), items=items, queued_before=queued,
                 queued_after=queued + len(added), min_queued=args.min_queued, target=args.target)
        print("replenished:", len(added), json.dumps(added, sort_keys=True))
    return 0


def cmd_claim(args):
    if os.path.exists(STOP):
        print("BLOCKED: EMERGENCY_STOP present")
        return 2
    ok, control = control_status()
    if not ok:
        print("REJECTED: stale_control " + str(control))
        return 2
    with Lock():
        st = load()
        reclaimed = reclaim(st)
        active = ledger_active_leases()
        now_epoch = epoch_utc(stamp())
        candidates = [
            t for t in st["tasks"].values()
            if t["status"] == "queued"
            and epoch_utc(t.get("available_at", stamp())) <= now_epoch
            and t["id"] not in active
        ]
        if not candidates:
            if not reclaimed:
                print("NO_QUEUED_TASKS")
            else:
                print("NO_QUEUED_TASKS reclaimed=" + json.dumps(sorted(reclaimed), sort_keys=True))
            return 1
        candidates.sort(key=lambda t: (t["priority"], t.get("available_at", ""), t["created"], t["id"]))
        task = candidates[0]
        task["status"] = "running"
        task["lease_owner"] = args.worker
        task["lease_id"] = uuid.uuid4().hex
        task["heartbeat"] = stamp()
        task["lease_until"] = plus_seconds(stamp(), LEASE_SECONDS)
        task["stall_detected"] = False
        save(st, "claim", task=task["id"], worker=args.worker, lease_id=task["lease_id"],
             lease_until=task["lease_until"], skipped_active_leases=sorted(active),
             control_verified=control)
        print(json.dumps({k: task.get(k) for k in
                          ("id", "status", "attempts", "lease_owner", "lease_id",
                           "lease_until", "available_at", "stall_detected")}, sort_keys=True))
    return 0


def mutate_beat(args):
    with Lock():
        st = load()
        task = st["tasks"].get(args.task)
        require_owner(task, args.worker, args.lease_id, "beat")
        task["heartbeat"] = stamp()
        task["lease_until"] = plus_seconds(stamp(), LEASE_SECONDS)
        progress = bool(getattr(args, "progress_note", None))
        if progress:
            task["progress_at"] = stamp()
            task["stall_detected"] = False
            task["progress_note"] = args.progress_note
        save(st, "heartbeat", task=args.task, worker=args.worker, lease_id=args.lease_id,
             meaningful_progress=progress, progress_note=args.progress_note or "")
    return 0


def mutate_finish(args, kind):
    with Lock():
        st = load()
        task = st["tasks"].get(args.task)
        require_owner(task, args.worker, args.lease_id, kind)
        reason = getattr(args, "reason", "") or ""
        if kind == "fail" or (kind == "finish" and args.fail):
            attempts = int(task["attempts"]) + 1
            task["attempts"] = attempts
            task["available_at"] = plus_seconds(stamp(), backoff(attempts))
            cleanup_lease(task)
            if attempts >= MAX_ATTEMPTS:
                task["status"] = "blocked"
                task["blocker"] = reason or "attempts_exhausted"
            else:
                task["status"] = "queued"
                task["blocker"] = None
            save(st, "fail", task=args.task, worker=args.worker, lease_id=args.lease_id,
                 reason=reason, attempts=attempts, available_at=task["available_at"],
                 backoff_seconds=backoff(attempts), status=task["status"])
        elif kind == "block" or (kind == "finish" and args.block):
            task["status"] = "blocked"
            task["blocker"] = reason or "blocked_by_worker"
            cleanup_lease(task)
            save(st, "block", task=args.task, worker=args.worker, lease_id=args.lease_id,
                 reason=task["blocker"])
        else:
            evidence = (getattr(args, "evidence", "") or "").strip()
            if not evidence:
                raise Reject("evidence_required_for_completion")
            reviewer = None
            if kind == "review" or getattr(args, "review", False):
                reviewer = args.reviewer or args.worker
                if reviewer == task["lease_owner"]:
                    raise Reject("reviewer_must_be_independent")
            task["evidence"] = evidence
            task["progress_at"] = stamp()
            task["stall_detected"] = False
            task["status"] = "reviewed" if reviewer else "verified"
            task["reviewer"] = reviewer
            cleanup_lease(task)
            save(st, "review" if reviewer else "complete", task=args.task, worker=args.worker,
                 lease_id=args.lease_id, evidence=evidence, reviewer=reviewer,
                 status=task["status"])
    return 0


def cmd_cursor(args):
    with Lock():
        st = load()
        st.setdefault("cursors", {})[args.name] = json.loads(args.value)
        save(st, "cursor", name=args.name, value=args.value)
    return 0


def cmd_snapshot(args):
    st = load()
    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        for tid, t in sorted(st["tasks"].items()):
            row = {k: t.get(k) for k in (
                "id", "title", "lane", "priority", "status", "attempts", "available_at",
                "stall_detected", "next_action", "evidence", "blocker", "reviewer")}
            f.write(json.dumps(row, sort_keys=True) + "\n")
    print("snapshot:", args.out, len(st["tasks"]), "tasks")
    return 0


def cmd_replay(args):
    """Rebuild state from the append-only ledger; never invent missing seed items."""
    events = read_events()
    if not events:
        print("REPLAY_EMPTY no ledger at", EVENTS)
        return 2
    st = {"schema": 2, "tasks": {}, "cursors": {}, "updated": events[-1]["ts"]}
    warnings = []

    def seed_items(items, ts):
        for item in items or []:
            tid = item.get("id")
            if tid and tid not in st["tasks"]:
                st["tasks"][tid] = new_task(item, parse_utc(ts))

    for ev in events:
        kind, ts, tid = ev["event"], ev["ts"], ev.get("task")
        if kind == "seed":
            if ev.get("items"):
                seed_items(ev["items"], ts)
            else:
                warnings.append("legacy seed at %s lacks item definitions" % ts)
        elif kind == "replenish":
            seed_items(ev.get("items"), ts)
        elif kind == "cursor":
            st.setdefault("cursors", {})[ev["name"]] = json.loads(ev["value"])
        elif kind == "lease_reclaimed":
            for reclaimed_id, detail in (ev.get("details") or {}).items():
                rtask = st["tasks"].get(reclaimed_id)
                if not rtask:
                    continue
                rtask.update(status=detail.get("status", "queued"),
                             attempts=detail.get("attempts", rtask["attempts"] + 1),
                             available_at=detail.get("available_at", ts),
                             stall_detected=detail.get("stalled", False))
                cleanup_lease(rtask)
        elif not tid or tid not in st["tasks"]:
            continue
        else:
            task = st["tasks"][tid]
            when = parse_utc(ts)
            if kind == "claim":
                task.update(status="running", lease_owner=ev.get("worker"),
                            lease_id=ev.get("lease_id"), heartbeat=ts,
                            lease_until=ev.get("lease_until") or plus_seconds(ts, LEASE_SECONDS),
                            stall_detected=False)
            elif kind == "heartbeat":
                task["heartbeat"] = ts
                task["lease_until"] = ev.get("lease_until") or plus_seconds(ts, LEASE_SECONDS)
                if ev.get("meaningful_progress"):
                    task["progress_at"] = ts
                    task["stall_detected"] = False
            elif kind == "fail":
                task.update(status=ev.get("status", "queued"), attempts=ev.get("attempts", task["attempts"]),
                            available_at=ev.get("available_at", ts))
                cleanup_lease(task)
            elif kind == "block":
                task.update(status="blocked", blocker=ev.get("reason"))
                cleanup_lease(task)
            elif kind in ("complete", "review"):
                task.update(status=ev.get("status", "reviewed" if kind == "review" else "verified"),
                            evidence=ev.get("evidence"), reviewer=ev.get("reviewer"),
                            progress_at=ts, stall_detected=False)
                cleanup_lease(task)
    if warnings and not args.allow_partial:
        print("REPLAY_INCOMPLETE")
        for warning in warnings:
            print("  " + warning)
        return 2
    atomic_write(STATE, st)
    counts = {s: sum(1 for t in st["tasks"].values() if t["status"] == s) for s in STATUS}
    print("replayed:", len(events), "events ->", len(st["tasks"]), "tasks",
          json.dumps(counts, sort_keys=True))
    if warnings:
        print("warnings:", len(warnings))
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    sub.add_parser("verify-control")
    s = sub.add_parser("seed")
    s.add_argument("file", help="JSON array of task objects")
    s = sub.add_parser("claim")
    s.add_argument("worker")
    s = sub.add_parser("beat")
    s.add_argument("--task", required=True)
    s.add_argument("--worker", required=True)
    s.add_argument("--lease-id", required=True)
    s.add_argument("--progress-note", default="")
    s = sub.add_parser("finish")
    s.add_argument("--task", required=True)
    s.add_argument("--worker", required=True)
    s.add_argument("--lease-id", required=True)
    s.add_argument("--evidence", default="")
    s.add_argument("--fail", action="store_true")
    s.add_argument("--block", action="store_true")
    s.add_argument("--review", action="store_true")
    s.add_argument("--reviewer", default="")
    s.add_argument("--reason", default="")
    s = sub.add_parser("complete")
    s.add_argument("--task", required=True)
    s.add_argument("--worker", required=True)
    s.add_argument("--lease-id", required=True)
    s.add_argument("--evidence", required=True)
    s = sub.add_parser("review")
    s.add_argument("--task", required=True)
    s.add_argument("--worker", required=True)
    s.add_argument("--lease-id", required=True)
    s.add_argument("--evidence", required=True)
    s.add_argument("--reviewer", required=True)
    s = sub.add_parser("replenish")
    s.add_argument("--template", default="")
    s.add_argument("--min-queued", type=int, default=MIN_QUEUED)
    s.add_argument("--target", type=int, default=TARGET_QUEUED)
    s = sub.add_parser("cursor")
    s.add_argument("name")
    s.add_argument("value", help="JSON value")
    s = sub.add_parser("snapshot")
    s.add_argument("out")
    s = sub.add_parser("replay")
    s.add_argument("--allow-partial", action="store_true")
    a = p.parse_args()
    handlers = {
        "status": cmd_status, "seed": cmd_seed, "claim": cmd_claim,
        "beat": mutate_beat, "cursor": cmd_cursor, "snapshot": cmd_snapshot,
        "replenish": cmd_replenish, "replay": cmd_replay,
        "verify-control": cmd_verify_control,
    }
    try:
        if a.cmd in handlers:
            return handlers[a.cmd](a) or 0
        if a.cmd == "finish":
            return mutate_finish(a, "finish")
        if a.cmd == "complete":
            return mutate_finish(a, "complete")
        if a.cmd == "review":
            return mutate_finish(a, "review")
    except Reject as exc:
        print("REJECTED: %s" % exc)
        event("update_rejected", task=getattr(a, "task", None), action=a.cmd,
              worker=getattr(a, "worker", None), reason=str(exc))
        return 3
    return 1


if __name__ == "__main__":
    sys.exit(main() or 0)
