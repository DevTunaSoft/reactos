#!/usr/bin/env python3
"""Read-only regression validator for ProjectOS public research artifacts.

Checks, across docs/projectos:
  * JSON / JSONL parse validity
  * duplicate record ids within a JSONL file
  * URL syntax (including duplicated/nested schemes)
  * self-reported record counts vs actual non-blank lines
  * WoW64 missing-path summary/tally consistency
  * banned private-state / credential strings

Usage: python validate_research_artifacts.py [--repo PATH] [--json OUT.json]
Exit status 0 = no failures, 1 = one or more failures. Never writes to the repo.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from urllib.parse import urlparse

URL_RE = re.compile(r"https?://[^\s\"'<>)\]},]+")
ID_FIELD = "id"
SELF_COUNT_FIELDS = ("records", "record_count", "total_records", "n_records", "num_records")
CROSS_FILE_KEYS = ("source_file", "target_file", "audited_file", "file", "source", "path", "files_audited")
COUNT_CLAIM_RE = re.compile(r"\b([A-Z][A-Z0-9_]*\.jsonl)\s+(\d+)\s+records?\b", re.I)

BANNED = (
    ("personal_absolute_path", re.compile(r"[A-Za-z]:[/\\]Users[/\\][A-Za-z0-9._\-]{3,}")),
    ("private_workspace_path", re.compile(r"(?i)ProjectOS[/\\]private")),

    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b|\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
    ("secret_assignment", re.compile(r"(?i)\b(?:api[_-]?key|access[_-]?token|secret|password|passwd|client_secret)\b\s*[:=]\s*[\"']?[A-Za-z0-9_\-]{8,}")),
    ("private_key_block", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
)


def iter_strings(value, path=""):
    if isinstance(value, dict):
        for key, val in value.items():
            yield from iter_strings(val, f"{path}.{key}")
    elif isinstance(value, list):
        for idx, val in enumerate(value):
            yield from iter_strings(val, f"{path}[{idx}]")
    elif isinstance(value, str):
        yield path, value


class Gate:
    def __init__(self, docs_dir):
        self.docs_dir = docs_dir
        self.failures = []
        self.checks = 0

    def fail(self, code, detail):
        self.failures.append({"check": code, "detail": detail})

    def url_ok(self, url):
        try:
            parts = urlparse(url)
        except ValueError:
            return False
        if parts.scheme not in ("http", "https") or not parts.netloc:
            return False
        if any(ch.isspace() for ch in url) or "@" in parts.netloc:
            return False
        if not re.fullmatch(r"[A-Za-z0-9.\-]+(?::\d+)?", parts.netloc):
            return False
        # Wayback Machine URLs legitimately embed the original URL in path/query.
        nested = re.search(r"https?://", parts.path) or re.search(r"https?://", parts.query)
        if nested and parts.netloc.lower() != "web.archive.org":
            return False
        return True

    def scan_urls(self, label, text):
        if "DATA_INTEGRITY_CORRECTIONS_V8.jsonl" in label:
            return  # this append-only record intentionally contains malformed observed URLs
        for match in URL_RE.finditer(text):
            url = match.group(0).rstrip(".,;")
            if not self.url_ok(url):
                self.fail("URL_SYNTAX", f"{label}: malformed URL {url[:160]}")

    def scan_banned(self, label, text):
        for name, pattern in BANNED:
            hit = pattern.search(text)
            if hit:
                self.fail("BANNED_STRING", f"{label}: {name} at offset {hit.start()}")

    def run(self):
        files = []
        for base, _dirs, names in os.walk(self.docs_dir):
            for name in names:
                files.append(os.path.join(base, name))
        files.sort()

        json_count = jsonl_count = id_count = url_count = 0
        line_counts = {}
        parsed_jsonl = {}

        for path in files:
            rel = os.path.relpath(path, os.path.dirname(self.docs_dir)).replace("\\", "/")
            ext = os.path.splitext(name_of(path))[1].lower()
            try:
                raw = open(path, "rb").read().decode("utf-8")
            except (OSError, UnicodeDecodeError) as exc:
                self.fail("READ_ERROR", f"{rel}: {type(exc).__name__}")
                continue

            self.scan_banned(rel, raw)
            if ext in (".md", ".txt"):
                self.scan_urls(rel, raw)

            if ext == ".json":
                json_count += 1
                try:
                    obj = json.loads(raw)
                except json.JSONDecodeError as exc:
                    self.fail("JSON_INVALID", f"{rel}: line {exc.lineno}: {exc.msg}")
                    continue
                for field, value in iter_strings(obj):
                    if re.match(r"https?://", value):
                        url_count += 1
                        self.scan_urls(f"{rel}{field}", value)

            elif ext == ".jsonl":
                jsonl_count += 1
                records = []
                ids = set()
                for lineno, line in enumerate(raw.splitlines(), 1):
                    if not line.strip():
                        continue
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError as exc:
                        self.fail("JSONL_INVALID", f"{rel}:{lineno}: {exc.msg}")
                        continue
                    records.append((lineno, obj))
                    rid = obj.get(ID_FIELD) if isinstance(obj, dict) else None
                    if isinstance(rid, str):
                        id_count += 1
                        if rid in ids:
                            self.fail("DUPLICATE_ID", f"{rel}:{lineno}: duplicate id {rid}")
                        ids.add(rid)
                    for field, value in iter_strings(obj):
                        if re.match(r"https?://", value):
                            url_count += 1
                            self.scan_urls(f"{rel}:{lineno}{field}", value)
                line_counts[os.path.basename(path)] = len(records)
                parsed_jsonl[rel] = records

                # Self-reported counts in summary records.
                for lineno, obj in records:
                    if not isinstance(obj, dict):
                        continue
                    rtype = str(obj.get("record_type", "")).lower()
                    rid = str(obj.get(ID_FIELD, ""))
                    if "summary" not in rtype and not rid.endswith("-SUMMARY"):
                        continue
                    if any(k in obj for k in CROSS_FILE_KEYS):
                        continue
                    candidates = [(k, v) for k, v in obj.items()
                                  if k.lower() in SELF_COUNT_FIELDS and isinstance(v, int) and not isinstance(v, bool)]
                    counts = obj.get("counts")
                    if isinstance(counts, dict):
                        candidates += [("counts." + k, v) for k, v in counts.items()
                                       if k.lower() in SELF_COUNT_FIELDS and isinstance(v, int) and not isinstance(v, bool)]
                    for field, reported in candidates:
                        if reported != len(records):
                            self.fail("RECORD_COUNT", f"{rel}:{lineno} {rid} {field}={reported}, actual={len(records)}")

        # Explicit "<file>.jsonl N records" claims anywhere in the docs tree.
        for path in files:
            rel = os.path.relpath(path, os.path.dirname(self.docs_dir)).replace("\\", "/")
            try:
                raw = open(path, "rb").read().decode("utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if "DATA_INTEGRITY_CORRECTIONS_V8.jsonl" in rel:
                continue  # correction records quote the defective claims as data
            for match in COUNT_CLAIM_RE.finditer(raw):
                target, claimed = match.group(1), int(match.group(2))
                if target in line_counts and claimed != line_counts[target]:
                    self.fail("RECORD_COUNT", f"{rel}: claims {target} {claimed} records, actual={line_counts[target]}")

        # WoW64 missing-path summaries must agree with path-presence records.
        wow64_rel = "projectos/research/WOW64_GAP_AUDIT_W9.jsonl"
        if wow64_rel in parsed_jsonl:
            recs = [obj for _n, obj in parsed_jsonl[wow64_rel] if isinstance(obj, dict)]
            paths = [r for r in recs if r.get("record_type") == "wow64_path_presence"]
            absent = sum(1 for r in paths if r.get("present") is False)
            present = sum(1 for r in paths if r.get("present") is True)
            for rec in recs:
                label = f"{wow64_rel} {rec.get('id')}"
                if rec.get("record_type") == "summary":
                    for field, expected in (("path_checks", len(paths)),
                                            ("paths_absent", absent),
                                            ("paths_present", present)):
                        if field in rec and rec[field] != expected:
                            self.fail("WOW64_SUMMARY", f"{label}: {field}={rec[field]}, actual={expected}")
                if rec.get("record_type") == "verdict" and absent and not rec.get("exact_components_absent_at_pin_and_master"):
                    self.fail("WOW64_SUMMARY", f"{label}: empty absent-components list while {absent} paths are absent")

        self.checks = 6
        return {
            "files": len(files), "json": json_count, "jsonl": jsonl_count,
            "ids": id_count, "urls": url_count, "failures": len(self.failures),
        }


def name_of(path):
    return os.path.basename(path)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--docs", default="docs/projectos")
    ap.add_argument("--json", dest="json_out", default=None)
    args = ap.parse_args()
    docs = os.path.join(args.repo, args.docs)
    if not os.path.isdir(docs):
        print(f"BLOCKED docs directory not found: {docs}")
        return 2
    gate = Gate(docs)
    stats = gate.run()
    for failure in gate.failures:
        print(f"FAIL {failure['check']} {failure['detail']}")
    print("SUMMARY " + " ".join(f"{k}={v}" for k, v in stats.items()))
    print(f"CHECKS categories=json,jsonl,ids,urls,counts,wow64,banned status={'PASS' if not stats['failures'] else 'FAIL'}")
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump({"stats": stats, "failures": gate.failures}, fh, indent=2)
    return 0 if not stats["failures"] else 1


if __name__ == "__main__":
    sys.exit(main())
