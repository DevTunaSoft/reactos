#!/usr/bin/env python3
"""One-off integrator: align live queue with already-published agent evidence."""
import json
import os
import subprocess
import sys

TOOL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools", "supervisor.py")
WORKER = "integrator-20261127T0624Z"
EV = {
    "W5-01": ("USB3_GAP_V7.jsonl: txtsetup.sif lacks USB\\ROOT_HUB30 / PCI\\CC_0C0330 and "
              "usbxhci/ucx01000/usbhub3 load entries; open PR #9865 and PR #9750; runtime NOT RUN"),
    "W3-04": ("WIKI_CONTRADICTION_V7.jsonl: Supported_USB_Devices rev 56222 (2025-12-15) says "
              "usbxHCI.sys non-existent; claim dates to rev 30811 (2012-02-02), before merged PR #9646"),
    "W3-07": ("PRESS_RECONCILIATION_V7.jsonl: VideoCardz claims checked against PR #9646 only; "
              "nightly and 0.4.16 runtime claims not verifiable from that PR"),
    "W5-02": ("REVIEWER_ASSIGNMENT_V7.jsonl, COUNT_RECONCILIATION_V7.jsonl, "
              "TERMINOLOGY_CORRECTION_V7.jsonl; supervisor_v2 32/32 isolated tests passed"),
}


def run(args):
    return subprocess.run([sys.executable, TOOL] + args, capture_output=True, text=True)


def main():
    st_path = os.path.join(os.path.dirname(TOOL), "..", "state", "queue_state.json")
    st = json.load(open(st_path, encoding="utf-8"))
    for tid in EV:
        task = st["tasks"][tid]
        if task["status"] == "running" and task.get("lease_owner") == WORKER:
            lease = task["lease_id"]
        else:
            r = run(["claim", WORKER])
            if r.returncode != 0 or not r.stdout.strip().startswith("{"):
                print("CLAIM_FAILED", tid, r.stdout[:160], r.stderr[:120])
                continue
            got = json.loads(r.stdout)
            lease = got["lease_id"]
            print("CLAIMED", got["id"], lease)
            if got["id"] != tid:
                # Finish whatever was claimed with a truthful no-evidence failure,
                # then retry the intended task on the next pass.
                f = run(["finish", "--task", got["id"], "--worker", WORKER, "--lease-id", lease,
                         "--fail", "--reason", "integrator_reconciliation_retry"])
                print("RELEASED", got["id"], f.returncode)
                continue
        f = run(["finish", "--task", tid, "--worker", WORKER, "--lease-id", lease,
                 "--evidence", EV[tid]])
        print("FINISHED", tid, "rc", f.returncode, f.stdout[:160], f.stderr[:120])
    print(run(["status"]).stdout)


if __name__ == "__main__":
    main()
