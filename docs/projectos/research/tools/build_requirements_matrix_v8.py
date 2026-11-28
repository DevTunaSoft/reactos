#!/usr/bin/env python3
"""Build a machine-readable requirements traceability matrix for V7 + V8."""
import argparse, hashlib, json, re, datetime

NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sections(path, pattern):
    text = open(path, encoding="utf-8").read()
    lines = text.splitlines()
    out = []
    current = None
    for i, line in enumerate(lines):
        m = re.match(pattern, line.strip())
        if m:
            if current:
                out.append(current)
            current = {"heading": line.strip(), "start": i, "lines": [line.strip()]}
        elif current is not None:
            current["lines"].append(line.strip())
    if current:
        out.append(current)
    return out, hashlib.sha256(text.encode()).hexdigest()


def record(rid, directive, heading, body, status="not_started"):
    clean = " ".join(x for x in body if x and not x.startswith("#"))[:900]
    return {
        "id": rid,
        "directive": directive,
        "section": heading.lstrip("# ").strip(),
        "required_behavior": clean,
        "objective_acceptance_criteria": [
            "Primary evidence exists for each asserted obligation",
            "Evidence is reproducible from pinned source or commit",
            "No OS implementation or authorization-boundary change is claimed"
        ],
        "verification_procedure": "Inspect cited primary evidence; reconcile against the canonical ledger and current repository state.",
        "status": status,
        "supporting_evidence": [],
        "responsible_assignment": None,
        "dependencies": [],
        "known_limitations": [],
        "last_verification_date": NOW,
        "next_corrective_action": "Create or update a specific research assignment if evidence is absent or stale."
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("v7")
    ap.add_argument("v8")
    ap.add_argument("output")
    args = ap.parse_args()
    records = []
    v8secs, v8hash = sections(args.v8, r"^##\s+\d+\.")
    v7secs, v7hash = sections(args.v7, r"^##\s+|^\d+\.\s+")
    for idx, s in enumerate(v8secs, 1):
        rid = f"V8-{idx:02d}"
        status = "evidence_collected" if idx in (1, 21, 25) else "not_started"
        records.append(record(rid, f"V8 sha256:{v8hash}", s["heading"], s["lines"], status))
        bullets = [l for l in s["lines"] if l.startswith("- ") or re.match(r"^\d+\.\s", l)]
        for j, b in enumerate(bullets, 1):
            records.append(record(f"{rid}-O{j:02d}", f"V8 sha256:{v8hash}", s["heading"], [b]))
    for idx, s in enumerate(v7secs, 1):
        rid = f"V7-{idx:02d}"
        records.append(record(rid, f"V7 sha256:{v7hash}", s["heading"], s["lines"]))
    with open(args.output, "w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"wrote {len(records)} requirements to {args.output}")
    print("v8_sha256", v8hash)
    print("v7_sha256", v7hash)


if __name__ == "__main__":
    main()
