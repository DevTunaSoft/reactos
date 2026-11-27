#!/usr/bin/env python3
"""Original ProjectOS V7 revalidation helper for round-2 findings F-01..F-12.

Reads the preserved round-2 record, verifies each cited immutable commit via
read-only GitHub API, and searches upstream PRs/issues for possible current
equivalents. Never modifies source, never executes retrieved code.
"""
import json
import os
import re
import subprocess
import sys
import urllib.parse
from datetime import datetime, timezone

BASE = os.environ.get("PROJECTOS_V7_STATE",
                      os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "state"))
RECORD = os.path.join(os.path.dirname(BASE), "FORK_ARCHAEOLOGY_ROUND_2.md")


def utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def gh_json(url):
    r = subprocess.run(["gh", "api", url], capture_output=True, text=True)
    if r.returncode != 0:
        return None, (r.stderr or "").strip().splitlines()[-1][:200]
    try:
        return json.loads(r.stdout), None
    except json.JSONDecodeError as e:
        return None, str(e)


TERMS = {
    "F-01": ["freeldr fat cluster", "FAT speedup"],
    "F-02": ["btrfs unaligned"],
    "F-03": ["freeldr btrfs sparse"],
    "F-04": ["CORE-17655", "wow64 process"],
    "F-05": ["CORE-13344", "usbxhci"],
    "F-06": ["CORE-13344", "pnp enumeration worker"],
    "F-07": ["MiCheckForUserStackOverflow"],
    "F-08": ["CORE-18200", "arm64 unwind"],
    "F-09": ["Longhorn", "modern hardware boot"],
    "F-10": ["ACPICA", "embedded controller address space"],
    "F-11": ["RAM disk IOCTL", "virtual disk"],
    "F-12": ["UEFI GOP freeldr"],
}


def main():
    text = open(RECORD, encoding="utf-8").read()
    out = []
    for fid in sorted(TERMS):
        m = re.search(rf"^- {fid} (https://github\.com/([^/]+)/reactos/commit/([0-9a-f]{{40}}))\s*(.*)$",
                      text, re.M)
        if not m:
            out.append({"id": fid, "status": "citation_not_parsed"})
            continue
        url, owner, sha, claim = m.group(1), m.group(2), m.group(3), m.group(4)
        rec = {"id": fid, "retrieved": utc(), "url": url, "owner": owner, "sha": sha,
               "author_report": claim.strip()}
        d, err = gh_json(f"repos/{owner}/reactos/commits/{sha}")
        if d and d.get("sha"):
            rec.update({
                "commit_verified": True,
                "commit_date": d["commit"]["author"]["date"],
                "commit_message": d["commit"]["message"].splitlines()[0],
                "files_changed": len(d.get("files", [])),
            })
        else:
            rec.update({"commit_verified": False, "error": err})
        search_hits = []
        for term in TERMS[fid]:
            q = urllib.parse.quote(f"repo:reactos/reactos {term}")
            d2, e2 = gh_json(f"search/issues?q={q}&per_page=5")
            if d2 and "items" in d2:
                for it in d2["items"][:5]:
                    search_hits.append({
                        "term": term, "number": it["number"], "title": it["title"],
                        "state": it["state"], "url": it["html_url"],
                        "merged": it.get("pull_request", {}).get("merged_at") is not None,
                    })
            else:
                search_hits.append({"term": term, "error": e2})
        rec["upstream_search_hits"] = search_hits
        rec["classification"] = ("citation_verified_equivalence_pending"
                                 if rec.get("commit_verified") else "citation_unverified")
        out.append(rec)
        print(fid, rec["classification"], len(search_hits), "search hits", flush=True)
    path = os.path.join(BASE, "revalidation.jsonl")
    with open(path, "w", encoding="utf-8") as f:
        for r in out:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    print("wrote", path, len(out))


if __name__ == "__main__":
    sys.exit(main())
