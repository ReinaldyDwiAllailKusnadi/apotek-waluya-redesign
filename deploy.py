#!/usr/bin/env python3
"""Deploy the redesign to /var/www/apotek2, then verify every asset over HTTP.

Same contract as the other sites: copy index.html + only the WebP variants the
page actually references, then curl every one of them and fail on non-200.

Usage: python3 deploy.py
"""
import os, re, shutil, subprocess, sys

SRC = "/root/projects/apotek-redesign"
WEB = "/var/www/apotek2"
HOST = "http://127.0.0.1/apotek2"

html = open(f"{SRC}/index.html", encoding="utf-8").read()
refs = set(re.findall(r"assets/webp/([A-Za-z0-9_.-]+)", html))

shutil.rmtree(WEB, ignore_errors=True)
os.makedirs(f"{WEB}/assets/webp", exist_ok=True)
shutil.copy2(f"{SRC}/index.html", f"{WEB}/index.html")
copied = 0
for r in sorted(refs):
    s = f"{SRC}/assets/webp/{r}"
    if os.path.exists(s):
        shutil.copy2(s, f"{WEB}/assets/webp/{r}")
        copied += 1
    else:
        print(f"  !! referenced but missing on disk: {r}")


def du(p):
    return subprocess.run(["du", "-sh", p], capture_output=True, text=True).stdout.split()[0]


print(f"webroot: {du(WEB)} | {copied} variants + index.html")

fails = []
for r in sorted(refs):
    code = subprocess.run(
        ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", f"{HOST}/assets/webp/{r}"],
        capture_output=True, text=True).stdout.strip()
    if code != "200":
        fails.append((r, code))

page = subprocess.run(
    ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", f"{HOST}/"],
    capture_output=True, text=True).stdout.strip()

print(f"page /: {page} | assets OK: {len(refs) - len(fails)}/{len(refs)}")
print("FAILED:", fails[:10] if fails else "none")

sys.exit(1 if (fails or page != "200") else 0)
