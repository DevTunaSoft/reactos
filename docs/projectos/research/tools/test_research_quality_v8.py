#!/usr/bin/env python3
"""Bounded V8-D01 regressions for the original research quality checks.

Each test builds two tiny JSONL fixtures in a temporary directory: a corrected
fixture that must be clean and a seeded bad fixture that must trigger exactly
the named check. No network, no repository writes, no unbounded corpora.

Run: python -m unittest discover -s docs/projectos/research/tools -p 'test_research_quality_v8.py' -v
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import research_quality_v8 as rq

GOOD_FULL_SHA = "3e6033a613fbf7c5bd58aaeaa05af42514af59d5"
GOOD_SHORT_SHA = "065abb35f5e8"


def write_fixture(path, records):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        for record in records:
            fh.write(json.dumps(record, sort_keys=True) + "\n")


class QualityRegressions(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="v8d01-regression-")
        self.addCleanup(self.tmp.cleanup)
        self.root = self.tmp.name
        self.good = os.path.join(self.root, "good.jsonl")
        self.bad = os.path.join(self.root, "bad.jsonl")
        write_fixture(self.good, [
            {"id": "QA-GOOD-1", "record_type": "source_retrieval",
             "url": "https://example.org/resource", "sha": GOOD_FULL_SHA,
             "archived": "https://web.archive.org/web/20260101000000id_/https://example.org/original"},
            {"id": "QA-GOOD-2", "record_type": "correction",
             "record_id": "QA-GOOD-1", "file_path": "good.jsonl", "sha": GOOD_SHORT_SHA},
        ])
        write_fixture(self.bad, [
            {"id": "", "record_type": "source_retrieval",
             "url": "https://example.org/https://example.org/resource", "sha": "not-a-commit"},
            {"id": "", "record_type": "source_retrieval",
             "record_id": "QA-NOT-PUBLISHED", "file_path": "absent.jsonl", "sha": "zzzz"},
        ])
        self.good_report = rq.Scan(self.root).run()
        # Scan both files together, then filter findings per basename.
        self.by_file = {}
        for finding in self.good_report["findings"]:
            self.by_file.setdefault(finding["file"], []).append(finding)

    def checks(self, basename):
        return {item["check"] for item in self.by_file.get(basename, [])}

    def test_schema_rejects_empty_and_duplicate_ids(self):
        self.assertEqual(self.checks("good.jsonl") & {"SCHEMA_ID", "SCHEMA_DUPLICATE_ID"}, set())
        self.assertIn("SCHEMA_ID", self.checks("bad.jsonl"))
        self.assertIn("SCHEMA_DUPLICATE_ID", self.checks("bad.jsonl"))

    def test_url_syntax_rejects_duplicated_scheme_and_allows_archive(self):
        self.assertNotIn("URL_SYNTAX", self.checks("good.jsonl"))
        self.assertIn("URL_SYNTAX", self.checks("bad.jsonl"))
        self.assertTrue(rq.url_ok("https://web.archive.org/web/20260101000000id_/https://example.org/original"))
        self.assertFalse(rq.url_ok("https://example.org/https://example.org/resource"))

    def test_commit_sha_rejects_non_hex(self):
        self.assertNotIn("COMMIT_SHA", self.checks("good.jsonl"))
        self.assertIn("COMMIT_SHA", self.checks("bad.jsonl"))
        self.assertTrue(rq.sha_ok(GOOD_FULL_SHA))
        self.assertTrue(rq.sha_ok(GOOD_SHORT_SHA))
        self.assertFalse(rq.sha_ok("not-a-commit"))

    def test_cross_record_references_must_resolve(self):
        self.assertNotIn("CROSS_RECORD_REF", self.checks("good.jsonl"))
        self.assertIn("CROSS_RECORD_REF", self.checks("bad.jsonl"))
        bad_refs = [item for item in self.by_file.get("bad.jsonl", [])
                    if item["check"] == "CROSS_RECORD_REF"]
        self.assertEqual(len(bad_refs), 2)

    def test_cli_exit_codes(self):
        good_dir = os.path.join(self.root, "only_good")
        bad_dir = os.path.join(self.root, "only_bad")
        os.makedirs(good_dir)
        os.makedirs(bad_dir)
        write_fixture(os.path.join(good_dir, "good.jsonl"), [
            {"id": "QA-GOOD-1", "record_type": "source_retrieval", "url": "https://example.org/resource"},
        ])
        write_fixture(os.path.join(bad_dir, "bad.jsonl"), [
            {"id": "QA-BAD-1", "record_type": "source_retrieval",
             "url": "https://example.org/https://example.org/resource"},
        ])
        with contextlib.redirect_stdout(io.StringIO()):
            good_rc = rq.main(["--root", good_dir])
            bad_rc = rq.main(["--root", bad_dir])
        self.assertEqual(good_rc, 0)
        self.assertEqual(bad_rc, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
