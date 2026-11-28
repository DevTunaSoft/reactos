#!/usr/bin/env python3
"""V8-D01 original, research-only quality checks for published research records.

Independent of the published compliance validator: this module implements its
own bounded schema, URL-syntax, commit-SHA and cross-record-reference checks.
It never writes to the repository and performs no network access.

Usage:
    python research_quality_v8.py --root docs/projectos [--json OUT.json]

Exit status 0 means zero findings, 1 means one or more findings, 2 means the
supplied root was unusable.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from urllib.parse import urlparse

URL_RE = re.compile(r"https?://[^\s\"'<>)\]},]+")
NETLOC_RE = re.compile(r"[A-Za-z0-9.\-]+(?::\d+)?")
SHA_RE = re.compile(r"[0-9a-fA-F]{7,40}")
WAYBACK_HOST = "web.archive.org"
JSONL_SUFFIX = ".jsonl"
# Append-only correction records quote malformed observed URLs by design.
CORRECTIONS_LOG = "DATA_INTEGRITY_CORRECTIONS_V8.jsonl"

# A SHA is only checked in fields explicitly dedicated to commit identity.
SHA_FIELDS = frozenset({
    "sha", "pinned_sha", "pinned_commit", "base_commit", "audited_commit",
    "upstream_pin", "upstream_master_pin_sha", "exact_tip_sha", "commit_sha",
})
# Values in these fields must resolve to a record id published in the corpus.
REF_ID_FIELDS = frozenset({
    "record_id", "source_record_id", "target_record_id",
    "related_record_id", "supersedes", "parent_record_id",
})
FILE_REF_FIELDS = frozenset({"file_path", "source_file", "target_file", "audited_file"})


def iter_strings(value, path=""):
    """Yield (dotted path, string) pairs from nested JSON-compatible values."""
    if isinstance(value, dict):
        for key, val in value.items():
            yield from iter_strings(val, f"{path}.{key}" if path else str(key))
    elif isinstance(value, list):
        for idx, val in enumerate(value):
            yield from iter_strings(val, f"{path}[{idx}]")
    elif isinstance(value, str):
        yield path, value


def url_ok(url):
    """Return True for a syntactically usable research source endpoint."""
    if any(ch.isspace() for ch in url):
        return False
    try:
        parts = urlparse(url)
    except ValueError:
        return False
    if parts.scheme not in ("http", "https") or not parts.netloc:
        return False
    if "@" in parts.netloc or not NETLOC_RE.fullmatch(parts.netloc):
        return False
    nested = re.search(r"https?://", parts.path) or re.search(r"https?://", parts.query)
    if nested and parts.netloc.lower() != WAYBACK_HOST:
        return False
    return True


def sha_ok(value):
    """Null/unknown commit identity is allowed; any pinned value must be hex."""
    if value is None:
        return True
    if not isinstance(value, str):
        return False
    return bool(SHA_RE.fullmatch(value))


class Scan:
    def __init__(self, root):
        self.root = root
        self.findings = []
        self.counts = {
            "files": 0, "json_files": 0, "jsonl_files": 0, "records": 0,
            "ids": 0, "urls_checked": 0, "sha_values_checked": 0,
            "references_checked": 0,
        }
        self.records = []

    def fail(self, check, rel, detail, record_id=None):
        item = {"check": check, "file": rel, "detail": detail}
        if record_id is not None:
            item["record_id"] = record_id
        self.findings.append(item)

    def load(self):
        paths = []
        for base, _dirs, names in os.walk(self.root):
            for name in names:
                if os.path.splitext(name)[1].lower() in (".json", ".jsonl"):
                    paths.append(os.path.join(base, name))
        paths.sort()
        known_files = set()
        for path in paths:
            rel = os.path.relpath(path, self.root).replace("\\", "/")
            known_files.add(os.path.basename(rel))
            self.counts["files"] += 1
            try:
                with open(path, "rb") as fh:
                    raw = fh.read().decode("utf-8")
            except (OSError, UnicodeDecodeError) as exc:
                self.fail("SCHEMA_READ", rel, type(exc).__name__)
                continue
            if rel.lower().endswith(JSONL_SUFFIX):
                self.counts["jsonl_files"] += 1
                seen = set()
                for lineno, line in enumerate(raw.splitlines(), 1):
                    if not line.strip():
                        continue
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError as exc:
                        self.fail("SCHEMA_JSONL", rel, f"line {lineno}: {exc.msg}")
                        continue
                    self.counts["records"] += 1
                    if not isinstance(obj, dict):
                        self.fail("SCHEMA_RECORD", rel, f"line {lineno}: not an object")
                        continue
                    rid = obj.get("id")
                    if "id" in obj:
                        if isinstance(rid, str) and rid.strip():
                            self.counts["ids"] += 1
                        elif isinstance(rid, int) and not isinstance(rid, bool):
                            self.counts["ids"] += 1
                        else:
                            self.fail("SCHEMA_ID", rel, f"line {lineno}: invalid id", rid)
                        if isinstance(rid, (str, int)) and not isinstance(rid, bool):
                            key = str(rid)
                            if key in seen:
                                self.fail("SCHEMA_DUPLICATE_ID", rel, f"line {lineno}: repeated id", rid)
                            seen.add(key)
                    if "record_type" in obj and (
                        not isinstance(obj["record_type"], str) or not obj["record_type"].strip()
                    ):
                        self.fail("SCHEMA_RECORD_TYPE", rel, f"line {lineno}: invalid record_type", rid)
                    self.records.append((rel, obj))
            else:
                self.counts["json_files"] += 1
                try:
                    json.loads(raw)
                except json.JSONDecodeError as exc:
                    self.fail("SCHEMA_JSON", rel, f"line {exc.lineno}: {exc.msg}")
        return known_files

    def check_content(self, known_files):
        ids = {str(obj["id"]) for _rel, obj in self.records
               if isinstance(obj.get("id"), (str, int)) and not isinstance(obj.get("id"), bool)}
        for rel, obj in self.records:
            rid = obj.get("id")
            url_scan_allowed = os.path.basename(rel) != CORRECTIONS_LOG
            for field, value in iter_strings(obj):
                if url_scan_allowed and value.startswith(("http://", "https://")):
                    self.counts["urls_checked"] += 1
                    for match in URL_RE.finditer(value):
                        url = match.group(0).rstrip(".,;")
                        if not url_ok(url):
                            self.fail("URL_SYNTAX", rel, f"{field}: malformed endpoint", rid)
                if field.split(".")[-1].split("[")[0] in SHA_FIELDS and isinstance(value, str):
                    self.counts["sha_values_checked"] += 1
                    if not sha_ok(value):
                        self.fail("COMMIT_SHA", rel, f"{field}: non-hex commit value", rid)
            for field in REF_ID_FIELDS & set(obj):
                value = obj[field]
                if isinstance(value, str) and value.strip():
                    self.counts["references_checked"] += 1
                    if value not in ids:
                        self.fail("CROSS_RECORD_REF", rel, f"{field}: unknown record id {value}", rid)
            for field in FILE_REF_FIELDS & set(obj):
                value = obj[field]
                if isinstance(value, str) and value.strip().lower().endswith(JSONL_SUFFIX):
                    self.counts["references_checked"] += 1
                    if os.path.basename(value.replace("\\", "/")) not in known_files:
                        self.fail("CROSS_RECORD_REF", rel, f"{field}: missing corpus file", rid)

    def run(self):
        known_files = self.load()
        self.check_content(known_files)
        found = {}
        for finding in self.findings:
            found[finding["check"]] = found.get(finding["check"], 0) + 1
        return {"counts": dict(self.counts), "findings_by_check": found,
                "findings": self.findings, "verdict": "PASS" if not self.findings else "FAIL"}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", required=True, help="directory containing published JSON/JSONL records")
    ap.add_argument("--json", dest="json_out", default=None, help="optional report path (outside the repo)")
    args = ap.parse_args(argv)
    if not os.path.isdir(args.root):
        print(f"BLOCKED root not found: {args.root}")
        return 2
    report = Scan(args.root).run()
    print("SUMMARY " + " ".join(f"{k}={v}" for k, v in report["counts"].items()))
    print("VERDICT " + report["verdict"] + " findings=" + str(len(report["findings"])))
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2)
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
