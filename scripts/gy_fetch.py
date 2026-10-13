#!/usr/bin/env python3
"""Fetch the Laws of Guyana (2022 Revised Edition, as published) from the
Ministry of Legal Affairs website, mola.gov.gy/laws-of-guyana.

Pages through the paginated chapter list (?page=N) and downloads each chapter
PDF into _raw/gy/pdf/.
"""
import json, os, re, subprocess, sys, time, urllib.parse
import requests
from bs4 import BeautifulSoup

BASE = "https://mola.gov.gy/laws-of-guyana"
UA = "LawCodex/1.0 (+https://github.com/LawCodex)"
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_raw", "gy")
DELAY = 1.0
s = requests.Session()
s.headers["User-Agent"] = UA


def get(url, **kw):
    for i in range(5):
        try:
            r = s.get(url, timeout=300, **kw)
            if r.status_code in (200, 404, 403):
                return r
        except requests.RequestException as e:
            print("  retry", url, e, file=sys.stderr)
        time.sleep(5 * (i + 1))
    raise RuntimeError("failed " + url)


def pdf_ok(path):
    if not os.path.exists(path):
        return False
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        head = f.read(5)
        f.seek(max(0, size - 4096))
        tail = f.read()
    if head != b"%PDF-" or b"%%EOF" not in tail:
        return False
    return subprocess.run(["pdfinfo", path], capture_output=True).returncode == 0


def main():
    os.makedirs(os.path.join(RAW, "pdf"), exist_ok=True)
    lp = os.path.join(RAW, "list.json")
    if os.path.exists(lp):
        items = json.load(open(lp))
    else:
        items, seen, page = [], set(), 1
        while True:
            soup = BeautifulSoup(get(BASE, params={"page": page}).text, "lxml")
            new = 0
            for card in soup.select("div.choose-card"):
                a = card.find("a", href=True)
                h = card.find("h6")
                if not a or not h or a["href"] in seen:
                    continue
                seen.add(a["href"])
                p = card.find("p")
                items.append({"title": h.get_text(" ", strip=True), "url": a["href"],
                              "volume": p.get_text(" ", strip=True).replace("Download", "").strip() if p else "",
                              "page": page})
                new += 1
            print("page", page, new, flush=True)
            if new == 0:
                break
            page += 1
            time.sleep(DELAY)
        json.dump(items, open(lp, "w"), indent=1)
    print(len(items), "items", flush=True)
    for n, it in enumerate(items):
        fn = re.sub(r"[^A-Za-z0-9._-]+", "_", urllib.parse.unquote(it["url"].split("/")[-1]))
        it["file"] = fn
        p = os.path.join(RAW, "pdf", fn)
        if pdf_ok(p):
            continue
        try:
            r = get(it["url"].replace(" ", "%20"))
        except RuntimeError as e:
            print(n, fn, "FAILED", e, flush=True)
            continue
        if r.status_code == 200 and r.content[:5] == b"%PDF-":
            cl = r.headers.get("content-length")
            if not cl or int(cl) == len(r.content):
                open(p, "wb").write(r.content)
        print(n, fn, pdf_ok(p), r.status_code, flush=True)
        time.sleep(DELAY)
    json.dump(items, open(lp, "w"), indent=1)


if __name__ == "__main__":
    main()
