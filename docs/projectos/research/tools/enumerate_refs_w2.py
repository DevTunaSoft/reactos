#!/usr/bin/env python3
"""W2-01 bounded branch/tag enumeration of verified fork-network members.

Read-only GitHub REST via the existing authorized `gh` CLI. No token handling,
no source import, no patch application, no builds. Writes append-only JSONL
evidence to the private state dir and a sanitized copy under the authorized
docs/projectos/research path on branch research/v7-wave1.
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

STATE = os.environ.get("PROJECTOS_V7_STATE", os.path.join(os.getcwd(), "state"))
PUB = os.environ.get(
    "PROJECTOS_V7_PUB",
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
)
FORKS = os.path.join(STATE, "fork_network_enriched.jsonl")
OUT_PRIV = os.path.join(STATE, "ref_enumeration.jsonl")
OUT_PUB = os.path.join(PUB, "REF_ENUMERATION_V7.jsonl")
MAX_PAGES = 5          # hard per-endpoint page cap (bounded run)
PER_PAGE = 100
ACTIVE_N = 12
ARCHIVED_N = 3
TS = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def gh(path):
    """Return (ok, payload_or_error_text, status_note)."""
    p = subprocess.run(
        ["gh", "api", path],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if p.returncode != 0:
        return False, (p.stderr or p.stdout).strip()[:400], "error"
    try:
        return True, json.loads(p.stdout), "200"
    except Exception as exc:  # noqa: BLE001 - evidence of malformed payload
        return False, "json_decode_error: %s" % exc, "malformed"


def paginate(full_name, kind):
    """Collect name->sha for branches or tags with a bounded page loop."""
    rows = []
    pages = []
    truncated = False
    for page in range(1, MAX_PAGES + 1):
        path = "repos/%s/%s?per_page=%d&page=%d" % (
            full_name, kind, PER_PAGE, page)
        ok, payload, status = gh(path)
        pages.append({"page": page, "endpoint": "GET /" + path,
                      "status": status, "retrieved": now()})
        if not ok or not isinstance(payload, list):
            truncated = True
            return rows, pages, truncated, (payload if not ok else "non_list")
        for item in payload:
            rows.append({
                "name": item.get("name"),
                "sha": (item.get("commit") or {}).get("sha"),
            })
        if len(payload) < PER_PAGE:
            return rows, pages, truncated, None
    truncated = True
    return rows, pages, truncated, None


def load_cohort():
    active, archived = [], []
    with open(FORKS, encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get("lineage_status") != "verified":
                continue
            rec = {
                "full_name": r.get("full_name"),
                "id": r.get("id"),
                "url": r.get("source_url")
                or ("https://github.com/" + str(r.get("full_name"))),
                "pushed_at": r.get("pushed_at_verified") or r.get("pushed_at"),
            }
            if r.get("archived"):
                archived.append(rec)
            else:
                active.append(rec)
    active.sort(key=lambda x: (x.get("pushed_at") or ""), reverse=True)
    archived.sort(key=lambda x: (x.get("pushed_at") or ""), reverse=True)
    return active[:ACTIVE_N], archived[:ARCHIVED_N]


def main():
    active, archived = load_cohort()
    cohort = [(r, "active_recent") for r in active] + \
             [(r, "archived_coverage") for r in archived]
    records = []
    all_shas = {}
    for rec, cohort_kind in cohort:
        full_name = rec["full_name"]
        ok, meta, status = gh("repos/" + full_name)
        if not ok or not isinstance(meta, dict):
            records.append({
                "record_type": "ref_enumeration", "task": "W2-01",
                "worker": "cron-20261127T055054Z", "retrieved": now(),
                "full_name": full_name, "repo_id": rec["id"],
                "cohort": cohort_kind, "url": rec["url"],
                "access_status": status,
                "error": str(meta)[:400],
                "test_status": "NOT RUN",
            })
            continue
        lic = meta.get("license") or {}
        branches, bpages, btrunc, berr = paginate(full_name, "branches")
        tags, tpages, ttrunc, terr = paginate(full_name, "tags")
        bshas = [b["sha"] for b in branches if b.get("sha")]
        tshas = [t["sha"] for t in tags if t.get("sha")]
        for sha in set(bshas + tshas):
            all_shas.setdefault(sha, []).append(full_name)
        # dedupe within repo: distinct tip SHAs and duplicate-tip groups
        seen = {}
        for b in branches:
            if b.get("sha"):
                seen.setdefault(b["sha"], []).append("branch:" + b["name"])
        for t in tags:
            if t.get("sha"):
                seen.setdefault(t["sha"], []).append("tag:" + t["name"])
        dup_groups = [v for v in seen.values() if len(v) > 1]
        records.append({
            "record_type": "ref_enumeration", "task": "W2-01",
            "worker": "cron-20261127T055054Z", "retrieved": TS,
            "full_name": full_name, "repo_id": rec["id"],
            "cohort": cohort_kind, "url": rec["url"],
            "api_base": "https://api.github.com/repos/" + full_name,
            "access_status": status, "archived": meta.get("archived"),
            "disabled": meta.get("disabled"),
            "default_branch": meta.get("default_branch"),
            "pushed_at": meta.get("pushed_at"),
            "parent": (meta.get("parent") or {}).get("full_name"),
            "license_spdx": lic.get("spdx_id"),
            "provenance": "verified fork-network member (W1-01 GraphQL parent); "
                          "public REST metadata; content treated as untrusted evidence",
            "branches_found": len(branches), "tags_found": len(tags),
            "distinct_tip_shas": len(set(bshas + tshas)),
            "duplicate_tip_groups": len(dup_groups),
            "duplicate_tip_examples": dup_groups[:5],
            "branches": branches, "tags": tags,
            "branch_pages": bpages, "tag_pages": tpages,
            "branch_truncated_at_cap": btrunc, "tag_truncated_at_cap": ttrunc,
            "branch_error": berr, "tag_error": terr,
            "patch_equivalence_dedupe": "NOT RUN (no patch import authorized)",
            "test_status": "NOT RUN",
        })
    cross = {sha: repos for sha, repos in all_shas.items() if len(repos) > 1}
    records.append({
        "record_type": "cross_fork_tip_dedupe_summary", "task": "W2-01",
        "worker": "cron-20261127T055054Z", "retrieved": TS,
        "repos_enumerated": len(records),
        "distinct_tip_shas_seen": len(all_shas),
        "tip_shas_shared_across_forks": len(cross),
        "examples": dict(list(cross.items())[:10]),
        "test_status": "NOT RUN",
    })
    with open(OUT_PRIV, "a", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    with open(OUT_PUB, "a", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    print("W2-01 retrieved=%s repos=%d records=%d cross_shared=%d" % (
        TS, len(cohort), len(records), len(cross)))
    for r in records[:-1]:
        print("  %-34s branches=%-4s tags=%-4s trunc=%s/%s lic=%s" % (
            r.get("full_name"), r.get("branches_found"), r.get("tags_found"),
            r.get("branch_truncated_at_cap"), r.get("tag_truncated_at_cap"),
            r.get("license_spdx")))


if __name__ == "__main__":
    main()
