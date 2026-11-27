#!/usr/bin/env python3
"""W2-01 bounded commit pinning for three high-value ref tips (read-only)."""
import json
import os
import subprocess
from datetime import datetime, timezone

STATE = os.environ.get("PROJECTOS_V7_STATE", os.path.join(os.getcwd(), "state"))
PUB = os.environ.get(
    "PROJECTOS_V7_PUB",
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
)
PRIV_F = os.path.join(STATE, "ref_enumeration.jsonl")
PUB_F = os.path.join(PUB, "REF_ENUMERATION_V7.jsonl")
TS = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
TARGETS = [
    ("nitroos-org/reactos", "fix/fastfat-fat-write-race"),
    ("Kreijstal/reactos", "GSoC_2017/usbxhci"),
    ("nitroos-org/reactos", "feat/wow64-3c-win32k-thunks"),
]


def load_tip(repo, branch):
    for line in open(PRIV_F, encoding="utf-8"):
        r = json.loads(line)
        if r.get("full_name") == repo and r.get("record_type") == "ref_enumeration":
            for b in r.get("branches", []):
                if b.get("name") == branch:
                    return b.get("sha")
    return None


def gh(path):
    p = subprocess.run(["gh", "api", path], capture_output=True, text=True, timeout=60)
    if p.returncode != 0:
        return None, (p.stderr or p.stdout).strip()[:300]
    try:
        return json.loads(p.stdout), None
    except Exception as exc:  # noqa: BLE001
        return None, "decode_error: %s" % exc


records = []
for repo, branch in TARGETS:
    sha = load_tip(repo, branch)
    if not sha:
        records.append({"record_type": "ref_commit_pin", "task": "W2-01",
                        "worker": "cron-20261127T055054Z", "retrieved": TS,
                        "repo": repo, "ref": branch, "sha": None,
                        "error": "tip not found in W2-01 enumeration", "test_status": "NOT RUN"})
        continue
    cpath = "repos/%s/commits/%s" % (repo, sha)
    cdata, cerr = gh(cpath)
    upath = "repos/reactos/reactos/commits/%s" % sha
    udata, uerr = gh(upath)
    c = cdata if isinstance(cdata, dict) else {}
    rec = {
        "record_type": "ref_commit_pin", "task": "W2-01",
        "worker": "cron-20261127T055054Z", "retrieved": TS,
        "repo": repo, "ref": branch, "sha": sha,
        "commit_url": "https://github.com/%s/commit/%s" % (repo, sha),
        "api_url": "https://api.github.com/" + cpath,
        "access_status": "200" if cdata else "error",
        "message_first_line": ((c.get("commit") or {}).get("message") or "").split("\n")[0][:300],
        "author_date": (c.get("commit") or {}).get("author", {}).get("date"),
        "committer_date": (c.get("commit") or {}).get("committer", {}).get("date"),
        "author_login": (c.get("author") or {}).get("login"),
        "upstream_exact_sha_check": "https://api.github.com/" + upath,
        "upstream_exact_sha_present": isinstance(udata, dict),
        "upstream_check_note": "exact SHA membership in reactos/reactos only; "
                              "not a patch-equivalence test",
        "error": cerr,
        "provenance": "public REST; untrusted evidence; no code imported",
        "test_status": "NOT RUN",
    }
    records.append(rec)

for path in (PRIV_F, PUB_F):
    with open(path, "a", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
print("pinned=%d" % len(records))
for r in records:
    print("  %s | %s | %s | upstream_sha=%s | %s" % (
        r["repo"], r["ref"], (r["sha"] or "")[:12],
        r.get("upstream_exact_sha_present"),
        r.get("message_first_line")))
