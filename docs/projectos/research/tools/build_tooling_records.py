#!/usr/bin/env python3
"""Build sanitized tool-effectiveness records from local smoke/revisit evidence."""
import json
import os
from datetime import datetime, timezone

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "state")
DEST = os.environ.get("PROJECTOS_V7_REPO", ".")


def utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def rows(name):
    p = os.path.join(BASE, name)
    if not os.path.exists(p):
        return []
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def main():
    out = []
    for r in rows("revisit_results.jsonl"):
        for a in r["attempts"]:
            out.append({
                "record_type": "source_retrieval", "retrieved": a.get("retrieved"),
                "source_id": r.get("id"), "family": r.get("family"), "url": r.get("url"),
                "tool": a.get("tool"), "status": a.get("status"),
                "text_chars": a.get("text_chars", 0), "elapsed_ms": a.get("elapsed_ms"),
                "note": (a.get("note") or "").replace("C:/Users/", "<user>/"),
                "selected_for_source": r.get("selected") == a.get("tool"),
                "tests": "NOT RUN",
            })
    for r in rows("tool_smoke.jsonl"):
        out.append({
            "record_type": "engine_smoke", "retrieved": r.get("retrieved"),
            "source_id": None, "family": "benchmark", "url": None,
            "tool": r.get("tool"), "status": r.get("status"),
            "text_chars": len(r.get("text") or ""), "elapsed_ms": r.get("elapsed_ms"),
            "launch_ms": r.get("launch_ms"),
            "note": ("launch=%sms rss_after=%sMB" % (r.get("launch_ms"), r.get("rss_chrome_mb_after"))),
            "selected_for_source": False, "tests": "NOT RUN",
        })
    for r in rows("tesseract_smoke.jsonl"):
        out.append({
            "record_type": "ocr_smoke", "retrieved": r.get("retrieved"), "tool": r.get("tool"),
            "status": r.get("status"), "text_chars": len(r.get("text") or ""),
            "elapsed_ms": r.get("elapsed_ms"), "note": "version " + str(r.get("version")),
            "source_id": None, "family": "benchmark", "url": None,
            "selected_for_source": False, "tests": "NOT RUN",
        })
    path = os.path.join(DEST, "docs", "projectos", "research", "TOOL_EFFECTIVENESS_V7.jsonl")
    with open(path, "w", encoding="utf-8") as f:
        for r in out:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    print("wrote", path, len(out), "records", utc())


if __name__ == "__main__":
    main()
