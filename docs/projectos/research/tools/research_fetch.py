#!/usr/bin/env python3
"""ProjectOS V7 multi-strategy research fetcher (original helper).

Retrieves public pages with the cheapest suitable method first, escalating
only when needed. One browser instance per engine is reused across URLs;
images/fonts/media are blocked; every attempt is bounded. Access challenges
(Anubis, CAPTCHA, login walls, paywalls) are recorded and NOT circumvented.

Usage:
  python research_fetch.py --targets targets.json --out evidence.jsonl
"""
import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")
CHALLENGE = re.compile(
    r"(anubis|captcha|cf-challenge|just a moment|access denied|"
    r"enable javascript and cookies|verify you are human|prove your humanity|"
    r"robot check|checking your browser)", re.I)
BAD_TAGS = ("script", "style", "noscript", "svg", "iframe", "canvas")
MAX_BYTES = 5_000_000
TIMEOUT = 20
MIN_TEXT = 200


def utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Engines:
    """Lazy, reused browser instances. At most one page active at a time."""
    def __init__(self):
        self._pw = None
        self._browsers = {}

    def browser(self, engine):
        if self._pw is None:
            from playwright.sync_api import sync_playwright
            self._pw = sync_playwright().start()
        if engine not in self._browsers:
            launcher = {"chromium": self._pw.chromium, "firefox": self._pw.firefox,
                        "webkit": self._pw.webkit}[engine]
            self._browsers[engine] = launcher.launch(headless=True)
        return self._browsers[engine]

    def fetch(self, engine, url, wait="domcontentloaded"):
        b = self.browser(engine)
        ctx = b.new_context(user_agent=UA, locale="en-US")
        ctx.route("**/*", self._block_heavy)
        page = ctx.new_page()
        try:
            r = page.goto(url, wait_until=wait, timeout=TIMEOUT * 1000)
            page.wait_for_timeout(600)
            return {"status": r.status if r else None,
                    "text": page.locator("body").inner_text(timeout=5000),
                    "html": page.content()}
        finally:
            ctx.close()

    @staticmethod
    def _block_heavy(route):
        if route.request.resource_type in ("image", "font", "media"):
            route.abort()
        else:
            route.continue_()

    def close(self):
        for b in self._browsers.values():
            try:
                b.close()
            except Exception:
                pass
        if self._pw:
            try:
                self._pw.stop()
            except Exception:
                pass


def evaluate(url, html, text, tool, t0, note=""):
    low = (text or "")[:4000]
    challenge = bool(CHALLENGE.search(low))
    clean = re.sub(r"\s+", " ", text or "").strip()
    ok = (not challenge and len(clean) >= MIN_TEXT)
    return {
        "retrieved": utc(), "url": url, "tool": tool,
        "elapsed_ms": int((time.time() - t0) * 1000),
        "text_chars": len(clean), "lines": len((text or "").splitlines()),
        "challenge_detected": challenge,
        "status": "ok" if ok else ("access_restricted" if challenge else "insufficient_text"),
        "note": note,
        "text": clean[:20000],
    }


def direct(url, t0):
    r = requests.get(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"},
                     timeout=TIMEOUT)
    if len(r.content) > MAX_BYTES:
        raise ValueError("response_too_large")
    r.raise_for_status()
    html = r.text
    text = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)
    return evaluate(url, html, text, "requests+bs4", t0,
                    "http=%d bytes=%d" % (r.status_code, len(r.content))), html


def trafilatura_extract(url, html, t0):
    import trafilatura
    text = trafilatura.extract(html, include_comments=True, include_tables=True,
                               favor_recall=True) or ""
    return evaluate(url, html, text, "trafilatura", t0, "extracted from direct HTML")


def soup_extract(url, html, t0):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(BAD_TAGS):
        tag.decompose()
    text = soup.get_text("\n", strip=True)
    return evaluate(url, html, text, "bs4_cleanup", t0, "script/style removed")


def browser_fetch(engines, engine, url, t0):
    out = engines.fetch(engine, url)
    text = BeautifulSoup(out["html"], "html.parser").get_text("\n", strip=True)
    return evaluate(url, out["html"], text, "playwright_" + engine, t0,
                    "http=%s" % out["status"])


def fetch_text(url, tool, t0, note=""):
    r = requests.get(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"},
                     timeout=TIMEOUT)
    if len(r.content) > MAX_BYTES:
        raise ValueError("response_too_large")
    r.raise_for_status()
    return evaluate(url, r.text, BeautifulSoup(r.text, "html.parser").get_text("\n", strip=True),
                    tool, t0, note + " http=%d" % r.status_code)


def wayback(url, t0):
    cdx = ("https://web.archive.org/cdx/search/cdx?url=" + url +
           "&output=json&filter=statuscode:200&filter=mimetype:text/html&limit=5&from=2018")
    r = requests.get(cdx, headers={"User-Agent": UA}, timeout=TIMEOUT)
    rows = r.json()
    if len(rows) < 2:
        raise ValueError("no_snapshot")
    ts = rows[1][1]
    return fetch_text("https://web.archive.org/web/%sid_/%s" % (ts, url),
                      "wayback_machine", t0, "snapshot=%s" % ts)


def mediawiki_api(url, t0):
    from urllib.parse import urlparse, quote
    host = "https://" + urlparse(url).netloc
    page = urlparse(url).path.rsplit("/", 1)[-1]
    api = host + "/wiki/api.php?action=parse&page=" + quote(page) + "&prop=text&format=json&origin=*"
    r = requests.get(api, headers={"User-Agent": UA}, timeout=TIMEOUT)
    r.raise_for_status()
    html = (r.json().get("parse") or {}).get("text", {}).get("*", "")
    if not html:
        raise ValueError("empty_api_result")
    return evaluate(url, html, BeautifulSoup(html, "html.parser").get_text("\n", strip=True),
                    "mediawiki_api", t0, "api=" + api)


def reddit_json(url, t0):
    return fetch_text(url.rstrip("/") + ".json?raw_json=1", "reddit_json", t0,
                      "public JSON endpoint, no authentication")


def old_reddit(url, t0):
    return fetch_text(url.replace("www.reddit.com", "old.reddit.com"), "old_reddit", t0)


STRATEGIES = {
    "article": ["direct", "trafilatura", "bs4_cleanup", "playwright_chromium", "wayback"],
    "forum": ["direct", "wayback", "playwright_chromium", "playwright_firefox"],
    "wiki": ["direct", "mediawiki_api", "wayback", "playwright_chromium"],
    "code_docs": ["direct", "wayback", "bs4_cleanup", "playwright_firefox"],
    "reddit": ["reddit_json", "old_reddit", "wayback", "playwright_chromium"],
    "pdf": ["direct"],
}
FALLBACK = ["direct", "trafilatura", "bs4_cleanup", "playwright_chromium", "wayback"]


def fetch_one(engines, target):
    url = target["url"]
    family = target.get("family", "article")
    order = target.get("tools") or STRATEGIES.get(family, FALLBACK)
    results = []
    html_cache = None
    for tool in order:
        t0 = time.time()
        try:
            if tool == "direct":
                rec, html_cache = direct(url, t0)
            elif tool == "trafilatura":
                if html_cache is None:
                    rec, html_cache = direct(url, t0)
                rec = trafilatura_extract(url, html_cache, t0)
            elif tool == "bs4_cleanup":
                if html_cache is None:
                    rec, html_cache = direct(url, t0)
                rec = soup_extract(url, html_cache, t0)
            elif tool.startswith("playwright_"):
                rec = browser_fetch(engines, tool.split("_", 1)[1], url, t0)
            elif tool == "wayback":
                rec = wayback(url, t0)
            elif tool == "mediawiki_api":
                rec = mediawiki_api(url, t0)
            elif tool == "reddit_json":
                rec = reddit_json(url, t0)
            elif tool == "old_reddit":
                rec = old_reddit(url, t0)
            else:
                rec = {"retrieved": utc(), "url": url, "tool": tool,
                       "status": "unsupported", "note": "not implemented", "elapsed_ms": 0}
        except Exception as e:
            rec = {"retrieved": utc(), "url": url, "tool": tool,
                   "status": "error", "note": type(e).__name__ + ": " + str(e)[:200],
                   "elapsed_ms": int((time.time() - t0) * 1000), "text_chars": 0}
        results.append({k: v for k, v in rec.items() if k != "text"})
        if rec.get("status") == "ok":
            return {"id": target.get("id"), "family": family, "selected": tool,
                    "attempts": results, "text": rec.get("text", "")}
        if rec.get("status") == "access_restricted":
            # Never try to defeat a challenge; one alternate client family only.
            if tool == order[0] and len(order) > 1:
                continue
            break
    return {"id": target.get("id"), "family": family, "selected": None,
            "attempts": results, "text": ""}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--targets", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--text-dir", default="")
    a = ap.parse_args()
    targets = json.load(open(a.targets, encoding="utf-8"))
    engines = Engines()
    os.makedirs(os.path.dirname(os.path.abspath(a.out)) or ".", exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f, open(a.out + ".texts.jsonl", "w", encoding="utf-8") as tf:
        for t in targets:
            rec = fetch_one(engines, t)
            text = rec.pop("text", "")
            f.write(json.dumps(rec, sort_keys=True) + "\n")
            tf.write(json.dumps({"id": t.get("id"), "url": t.get("url"),
                                 "text": text}, sort_keys=True) + "\n")
            print(rec["id"], rec.get("selected"), rec["attempts"][-1]["status"],
                  rec["attempts"][-1].get("text_chars"), flush=True)
    engines.close()


if __name__ == "__main__":
    sys.exit(main())
