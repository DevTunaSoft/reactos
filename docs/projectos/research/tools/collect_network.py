#!/usr/bin/env python3
"""Original ProjectOS V7 research collector: fork lineage + candidate validation.

Uses only `gh api` (existing authorized credentials) and public read endpoints.
No token is read, printed or written by this script. Output: JSONL + summary.
"""
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

BASE = os.environ.get("PROJECTOS_V7_STATE",
                      os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "state"))
FIELDS = ("id databaseId nameWithOwner isArchived isFork isDisabled pushedAt "
          "defaultBranchRef{name} parent{nameWithOwner databaseId}")


def utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def gh_json(args, retries=3):
    for attempt in range(retries):
        r = subprocess.run(["gh", "api"] + args, capture_output=True, text=True)
        # gh exits non-zero when a GraphQL response contains field errors, but
        # partial `data` is still valid evidence for the aliases that resolved.
        try:
            parsed = json.loads(r.stdout)
            if isinstance(parsed, dict) and "data" in parsed:
                if parsed.get("errors"):
                    parsed["data"]["_errors"] = [
                        e.get("message", "unknown") for e in parsed["errors"]
                    ]
                return parsed["data"], None
        except (json.JSONDecodeError, ValueError):
            pass
        if r.returncode == 0:
            try:
                return json.loads(r.stdout), None
            except json.JSONDecodeError as e:
                return None, "bad_json:" + str(e)
        err = (r.stderr or "").strip().splitlines()[-1] if r.stderr.strip() else "exit_" + str(r.returncode)
        if "rate limit" in err.lower() or "secondary rate" in err.lower():
            time.sleep(30 * (attempt + 1))
            continue
        return None, err[:200]
    return None, "retries_exhausted"


def graphql_batch(repos):
    """repos: list of (alias, owner, name). Returns dict alias -> object|None."""
    parts = []
    for alias, owner, name in repos:
        o = json.dumps(owner)
        n = json.dumps(name)
        parts.append(f'{alias}:repository(owner:{o},name:{n}){{{FIELDS}}}')
    q = "query { rateLimit{cost remaining limit} " + " ".join(parts) + " }"
    data, err = gh_json(["graphql", "-f", "query=" + q])
    if err or not isinstance(data, dict):
        return {}, err or "no_data", None
    return data, None, data.get("rateLimit")


def enrich_forks(rows):
    out, errors, cost = [], [], 0
    for start in range(0, len(rows), 100):
        chunk = rows[start:start + 100]
        batch = []
        for i, r in enumerate(chunk):
            owner, _, name = r["full_name"].partition("/")
            batch.append((f"r{i}", owner, name))
        data, err, rl = graphql_batch(batch)
        if err:
            errors.append({"page": start // 100 + 1, "error": err})
            time.sleep(2)
            continue
        cost += (rl or {}).get("cost", 0) or 0
        for i, r in enumerate(chunk):
            g = data.get(f"r{i}")
            rec = dict(r)
            rec["graphql_id"] = (g or {}).get("id")
            rec["parent_verified"] = ((g or {}).get("parent") or {}).get("nameWithOwner")
            rec["parent_database_id"] = ((g or {}).get("parent") or {}).get("databaseId")
            rec["is_fork_verified"] = (g or {}).get("isFork")
            rec["is_archived_verified"] = (g or {}).get("isArchived")
            rec["pushed_at_verified"] = (g or {}).get("pushedAt")
            rec["lineage_status"] = "verified" if g else "unresolved_graphql"
            rec["source_url"] = "https://github.com/" + r["full_name"]
            out.append(rec)
        print(f"fork page {start // 100 + 1}: {len(chunk)} -> {sum(1 for x in out[-len(chunk):] if x['lineage_status']=='verified')} verified", flush=True)
    return out, errors, cost


def validate_candidates(rows):
    out, errors, cost = [], [], 0
    for start in range(0, len(rows), 100):
        chunk = rows[start:start + 100]
        batch = []
        for i, r in enumerate(chunk):
            owner, _, name = r["repository"].partition("/")
            batch.append((f"r{i}", owner, name))
        data, err, rl = graphql_batch(batch)
        if err:
            errors.append({"page": start // 100 + 1, "error": err})
            time.sleep(2)
            continue
        cost += (rl or {}).get("cost", 0) or 0
        missing = []
        for i, r in enumerate(chunk):
            g = data.get(f"r{i}")
            rec = dict(r)
            rec["retrieved"] = utc()
            if g:
                rec.update({
                    "live_status": "public",
                    "current_full_name": g.get("nameWithOwner"),
                    "database_id": g.get("databaseId"),
                    "archived": g.get("isArchived"),
                    "is_fork": g.get("isFork"),
                    "parent": ((g.get("parent") or {}).get("nameWithOwner")),
                    "pushed_at": g.get("pushedAt"),
                    "verification": "graphql_name_lookup",
                })
                if g.get("nameWithOwner") != r["repository"]:
                    rec["renamed"] = True
            else:
                rec["live_status"] = "unresolved_by_name"
                rec["verification"] = "graphql_name_lookup_null"
                missing.append(r)
            out.append(rec)
        # Resolve stale names by numeric repository ID via REST read endpoint.
        for r in missing:
            rid = r.get("id")
            if not rid:
                continue
            d, e = gh_json(["repositories/" + str(rid), "--jq",
                            '{full_name,id,archived,fork,message}'])
            for rec in out:
                if rec.get("id") == rid and rec.get("live_status") == "unresolved_by_name":
                    if d and d.get("id"):
                        rec.update({
                            "live_status": "public_renamed",
                            "current_full_name": d.get("full_name"),
                            "archived": d.get("archived"),
                            "is_fork": d.get("fork"),
                            "verification": "rest_id_lookup",
                            "renamed": True,
                        })
                    else:
                        rec["live_status"] = "unavailable_or_private"
                        rec["verification"] = "rest_id_lookup_failed"
                        rec["error"] = e
        print(f"candidate page {start // 100 + 1}: {len(chunk)} checked", flush=True)
    return out, errors, cost


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")


def main():
    os.makedirs(BASE, exist_ok=True)
    forks = [json.loads(l) for l in open(os.path.join(BASE, "fork_network_raw.jsonl"), encoding="utf-8") if l.strip()]
    cands = [json.loads(l) for l in open(os.path.join(BASE, "..", "FORK_SEARCH_CANDIDATES.jsonl"), encoding="utf-8") if l.strip()]
    cands = [c for c in cands if "repository" in c and "id" in c]
    print("forks:", len(forks), "candidates:", len(cands), flush=True)
    enriched, e1, c1 = enrich_forks(forks)
    validated, e2, c2 = validate_candidates(cands)
    write_jsonl(os.path.join(BASE, "fork_network_enriched.jsonl"), enriched)
    write_jsonl(os.path.join(BASE, "candidates_validated.jsonl"), validated)
    summary = {
        "retrieved": utc(),
        "fork_rows": len(enriched),
        "fork_lineage_verified": sum(1 for r in enriched if r["lineage_status"] == "verified"),
        "fork_lineage_unresolved": sum(1 for r in enriched if r["lineage_status"] != "verified"),
        "candidate_rows": len(validated),
        "candidate_public": sum(1 for r in validated if r.get("live_status") in ("public", "public_renamed")),
        "candidate_renamed": sum(1 for r in validated if r.get("renamed")),
        "candidate_unavailable": sum(1 for r in validated if r.get("live_status") == "unavailable_or_private"),
        "graphql_cost": c1 + c2,
        "errors": e1 + e2,
        "method": "gh api --paginate (REST list, follows Link headers) + gh api graphql batches of 100 + REST /repositories/{id} fallback",
    }
    with open(os.path.join(BASE, "collector_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)
    print(json.dumps(summary, indent=2, sort_keys=True), flush=True)


if __name__ == "__main__":
    sys.exit(main())
