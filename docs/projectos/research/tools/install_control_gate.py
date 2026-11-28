#!/usr/bin/env python3
"""Create supervisor_v3 with enforced directive/checksum control verification."""
import os
import shutil

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(HERE, "tools", "supervisor.py")
DST = os.path.join(HERE, "tools", "supervisor_v3.py")
text = open(SRC, encoding="utf-8").read()

text = text.replace("import calendar\n", "import calendar\nimport hashlib\n", 1)

gate = '''

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

'''
text = text.replace("\ndef cmd_status(args):", gate + "\ndef cmd_status(args):", 1)

old = '''    if os.path.exists(STOP):
        print("BLOCKED: EMERGENCY_STOP present")
        return 2
    with Lock():
        st = load()
        reclaimed = reclaim(st)'''
new = '''    if os.path.exists(STOP):
        print("BLOCKED: EMERGENCY_STOP present")
        return 2
    ok, control = control_status()
    if not ok:
        print("REJECTED: stale_control " + str(control))
        return 2
    with Lock():
        st = load()
        reclaimed = reclaim(st)'''
assert old in text
text = text.replace(old, new, 1)

old2 = '''        save(st, "claim", task=task["id"], worker=args.worker, lease_id=task["lease_id"],
             lease_until=task["lease_until"], skipped_active_leases=sorted(active))'''
new2 = '''        save(st, "claim", task=task["id"], worker=args.worker, lease_id=task["lease_id"],
             lease_until=task["lease_until"], skipped_active_leases=sorted(active),
             control_verified=control)'''
assert old2 in text
text = text.replace(old2, new2, 1)

text = text.replace('    sub.add_parser("status")\n',
                    '    sub.add_parser("status")\n    sub.add_parser("verify-control")\n', 1)
text = text.replace('"replenish": cmd_replenish, "replay": cmd_replay,\n',
                    '"replenish": cmd_replenish, "replay": cmd_replay,\n'
                    '        "verify-control": cmd_verify_control,\n', 1)

with open(DST, "w", encoding="utf-8") as f:
    f.write(text)
print("wrote", DST, len(text))
