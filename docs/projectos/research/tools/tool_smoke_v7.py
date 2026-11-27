#!/usr/bin/env python3
"""Original V7 tool smoke benchmark: compatibility, launch cost, cleanup.

No credentials, no network challenges, no simultaneous engines. Each engine is
launched, fetched from a local data URL, and closed before the next starts.
"""
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

import psutil

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NODE = os.path.join(HERE, "node_tools")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"


def utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def rss_mb():
    total = 0
    for p in psutil.process_iter(["name", "memory_info"]):
        try:
            if "chrome" in (p.info.get("name") or "").lower() or "firefox" in (p.info.get("name") or "").lower():
                total += p.info["memory_info"].rss
        except (psutil.NoSuchProcess, psutil.AccessDenied, KeyError):
            continue
    return round(total / 1048576, 1)


def playwright_smoke():
    from playwright.sync_api import sync_playwright
    out = []
    with sync_playwright() as pw:
        for name in ("chromium", "firefox", "webkit"):
            t0 = time.time()
            rec = {"tool": "playwright_" + name, "retrieved": utc()}
            try:
                b = getattr(pw, name).launch(headless=True)
                rec["launch_ms"] = int((time.time() - t0) * 1000)
                p = b.new_page()
                p.goto("data:text/html,<h1>V7 smoke</h1><p>engine_ok</p>")
                rec["text"] = p.locator("body").inner_text()
                rec["status"] = "ok" if "engine_ok" in rec["text"] else "unexpected_text"
                b.close()
                rec["rss_chrome_mb_after"] = rss_mb()
            except Exception as e:
                rec["status"] = "error"
                rec["error"] = type(e).__name__ + ": " + str(e)[:180]
            rec["elapsed_ms"] = int((time.time() - t0) * 1000)
            out.append(rec)
            print(name, rec["status"], rec["elapsed_ms"], flush=True)
    return out


def node_smoke(tool, script):
    t0 = time.time()
    rec = {"tool": tool, "retrieved": utc()}
    try:
        r = subprocess.run(["node", "-e", script], cwd=NODE, capture_output=True,
                           text=True, timeout=90)
        rec["status"] = "ok" if r.returncode == 0 else "error"
        rec["stdout"] = r.stdout.strip()[:300]
        rec["stderr"] = r.stderr.strip()[:200]
    except Exception as e:
        rec["status"] = "error"
        rec["error"] = type(e).__name__ + ": " + str(e)[:180]
    rec["elapsed_ms"] = int((time.time() - t0) * 1000)
    print(tool, rec["status"], rec["elapsed_ms"], flush=True)
    return rec


def selenium_smoke():
    t0 = time.time()
    rec = {"tool": "selenium_chrome", "retrieved": utc()}
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        o = Options()
        o.add_argument("--headless=new")
        o.add_argument("--no-sandbox")
        o.binary_location = CHROME
        d = webdriver.Chrome(options=o)
        d.get("data:text/html,<h1>V7 smoke</h1><p>engine_ok</p>")
        rec["text"] = d.find_element("tag name", "body").text
        rec["status"] = "ok" if "engine_ok" in rec["text"] else "unexpected_text"
        d.quit()
    except Exception as e:
        rec["status"] = "error"
        rec["error"] = type(e).__name__ + ": " + str(e)[:180]
    rec["elapsed_ms"] = int((time.time() - t0) * 1000)
    print("selenium", rec["status"], rec["elapsed_ms"], flush=True)
    return rec


def main():
    out = []
    out += playwright_smoke()
    out.append(node_smoke("puppeteer_core_chrome",
        "(async()=>{const p=require('puppeteer-core');const b=await p.launch({executablePath:" +
        json.dumps(CHROME) + ",headless:true,args:['--no-sandbox']});const pg=await b.newPage();" +
        "await pg.goto('data:text/html,<h1>V7 smoke</h1><p>engine_ok</p>');" +
        "console.log(await pg.evaluate(()=>document.body.innerText));await b.close();})()"
        ".catch(e=>{console.error(e.message);process.exit(1)})"))
    out.append(node_smoke("lightpanda_node",
        "const p=require('@lightpanda/browser');console.log(Object.keys(p).join(','))"))
    out.append(selenium_smoke())
    with open(os.path.join(HERE, "state", "tool_smoke.jsonl"), "w", encoding="utf-8") as f:
        for r in out:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    print("wrote", len(out), "records")


if __name__ == "__main__":
    main()
