#!/usr/bin/env python3
"""Read-only projection of append-only corrections onto a scratch mirror.

The published corpus is never edited. This helper copies docs/projectos into a
scratch directory and applies proposed correction records to that copy only,
so validators can report an in-memory 'after' count without a history rewrite.

Usage:
    python project_corrections_v8.py --source docs/projectos \
        --corrections docs/projectos/research/DATA_INTEGRITY_CORRECTIONS_V8.jsonl \
        --out <scratch-root>            # mirror is written to <scratch-root>/projectos
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from collections import Counter


def replace_strings(value, needle, replacement):
    """Return (new value, number of replacements) without mutating the input."""
    if isinstance(value, str):
        count = value.count(needle)
        return value.replace(needle, replacement), count
    if isinstance(value, dict):
        result = {}
        total = 0
        for key, val in value.items():
            new_val, n = replace_strings(val, needle, replacement)
            result[key] = new_val
            total += n
        return result, total
    if isinstance(value, list):
        result = []
        total = 0
        for val in value:
            new_val, n = replace_strings(val, needle, replacement)
            result.append(new_val)
            total += n
        return result, total
    return value, 0


def set_field(record, field, value):
    parts = field.split(".")
    target = record
    for part in parts[:-1]:
        target = target.setdefault(part, {})
    target[parts[-1]] = value


def load(path):
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", required=True)
    ap.add_argument("--corrections", required=True)
    ap.add_argument("--out", required=True, help="fresh scratch directory")
    args = ap.parse_args(argv)
    if not os.path.isdir(args.source) or os.path.exists(args.out):
        print("BLOCKED: source missing or scratch output already exists")
        return 2

    mirror = os.path.join(args.out, "projectos")
    shutil.copytree(args.source, mirror)
    # Correction file paths use two conventions (docs/projectos/... and
    # projectos/...), so resolve every referenced basename in the mirror once.
    mirror_files = {}
    for base, _dirs, names in os.walk(mirror):
        for name in names:
            mirror_files.setdefault(name, []).append(os.path.join(base, name))
    corrections = load(args.corrections)
    by_file = {}
    written = {}
    applied = Counter()
    files_changed = set()
    records_changed = set()

    for corr in corrections:
        rel = corr["file_path"].replace("\\", "/")
        name = os.path.basename(rel)
        candidates = mirror_files.get(name, [])
        if len(candidates) != 1:
            applied["missing_target_file"] += 1
            continue
        target = candidates[0]
        if name not in by_file:
            by_file[name] = load(target)
            written[name] = target
        records = by_file[name]
        matches = [(idx, r) for idx, r in enumerate(records)
                   if str(r.get("id")) == str(corr["record_id"])]
        if len(matches) != 1:
            applied["missing_target_record"] += 1
            continue
        idx, record = matches[0]
        dtype = corr["defect_type"]
        observed = corr["observed_value"]
        corrected = corr["corrected_value"]
        changed = False
        if dtype == "malformed_hardware_source_url":
            before = json.dumps(record, sort_keys=True)
            record, n = replace_strings(record, observed, corrected)
            records[idx] = record
            changed = n > 0
            if not changed:
                if corrected in before:
                    applied["already_applied_duplicate_field"] += 1
                else:
                    applied["unapplied_url"] += 1
        elif dtype == "reported_record_count":
            if " records" in observed and ".jsonl" in observed:
                record, n = replace_strings(record, observed, corrected)
                records[idx] = record
                changed = n > 0
            elif "=" in observed:
                field, _old_raw = observed.split("=", 1)
                _new_field, raw = corrected.split("=", 1)
                value = int(raw) if raw.isdigit() else raw
                set_field(record, field, value)
                changed = True
        elif dtype == "inconsistent_wow64_missing_path_summary":
            field, old_raw = observed.split("=", 1)
            _new_field, raw = corrected.split("=", 1)
            if old_raw == "[]":
                absent = [r for r in records
                          if r.get("record_type") == "wow64_path_presence" and r.get("present") is False]
                value = [{"path": r.get("path"), "ref": r.get("ref")} for r in absent]
            else:
                value = int(raw) if raw.isdigit() else raw
            set_field(record, field, value)
            changed = True
        if changed:
            applied[dtype] += 1
            files_changed.add(name)
            records_changed.add(corr["record_id"])

    for name, records in by_file.items():
        with open(written[name], "w", encoding="utf-8", newline="\n") as fh:
            for record in records:
                fh.write(json.dumps(record, sort_keys=True) + "\n")

    summary = {
        "corrections_total": len(corrections),
        "corrections_applied": dict(applied),
        "files_changed": len(files_changed),
        "records_changed": len(records_changed),
        "mirror": "projectos (scratch only; source untouched)",
    }
    ok = sum(v for k, v in applied.items()
             if not k.startswith("missing") and k != "unapplied_url")
    print(json.dumps(summary, sort_keys=True))
    return 0 if ok == len(corrections) else 1


if __name__ == "__main__":
    sys.exit(main())
