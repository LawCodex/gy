#!/usr/bin/env python3
"""Convert the Laws of Guyana chapter PDFs (_raw/gy, from mola.gov.gy) to Markdown."""
import datetime, json, os, re, subprocess, sys, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gy_pdfmd as pm

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
RAW = os.path.abspath(os.path.join(ROOT, "..", "_raw", "gy"))
PAGE = "https://mola.gov.gy/laws-of-guyana"
JUNK = [r"^LAWS OF GUYANA$", r"^L\.R\.O\.\s*\d+/\d{4}$", r"^\.{2,}$"]


def slugify(s):
    s = s.lower().replace("&", " and ").replace("’", "").replace("'", "")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:80].strip("-")


def q(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def front(d):
    out = ["---"]
    for k, v in d.items():
        if v is None or v == "":
            continue
        out.append(f"{k}: {v if isinstance(v, (int, float)) or k in ('date', 'last_amended', 'retrieved', 'type', 'jurisdiction', 'language', 'status') else q(v)}")
    out.append("---")
    return "\n".join(out) + "\n\n"


def pdf_ok(path):
    if not os.path.exists(path):
        return False
    with open(path, "rb") as f:
        head = f.read(5)
        f.seek(max(0, os.path.getsize(path) - 4096))
        tail = f.read()
    return head == b"%PDF-" and b"%%EOF" in tail and \
        subprocess.run(["pdfinfo", path], capture_output=True).returncode == 0


def main():
    retrieved = datetime.date.today().isoformat()
    for d in ("chapters", "constitution"):
        os.makedirs(os.path.join(ROOT, d), exist_ok=True)
    items = json.load(open(os.path.join(RAW, "list.json")))
    report = {"converted": [], "gaps": []}
    used = set()
    for it in items:
        fn = it.get("file") or re.sub(r"[^A-Za-z0-9._-]+", "_", urllib.parse.unquote(it["url"].split("/")[-1]))
        pdf = os.path.join(RAW, "pdf", fn)
        label = it["title"].strip()
        src_pdf = it["url"].replace(" ", "%20")
        if not pdf_ok(pdf):
            report["gaps"].append({"title": label, "reason": "PDF not downloadable / incomplete", "source": src_pdf})
            continue
        body, st = pm.pdf_to_md(pdf, extra_header_patterns=JUNK, anywhere_patterns=JUNK, tmpdir=RAW)
        if st["chars_per_page"] < 150:
            report["gaps"].append({"title": label, "reason": "PDF has no text layer (scan)", "source": src_pdf})
            continue
        cm = re.match(r"Chapter\s+(\d+):(\d+)\s*[-–]?\s*(.*)$", label, re.I)
        if cm:
            a, b, name = int(cm.group(1)), cm.group(2), cm.group(3).strip()
            cap = f"{a}:{b}"
            fname = f"cap-{a:03d}-{b}-{slugify(name)}"
        else:
            cap, name, fname = None, label, slugify(label)
        is_const = cap == "1:01"
        while fname in used:
            fname += "-2"
        used.add(fname)
        rel = ("constitution/" if is_const else "chapters/") + fname + ".md"
        p1 = subprocess.run(["pdftotext", "-l", "2", pdf, "-"], capture_output=True, text=True).stdout
        lro = re.search(r"L\.R\.O\.\s*(\d+/\d{4})", p1)
        act = re.search(r"\nAct\s*\n+\s*([^\n]{3,60})", p1)
        fm = {
            "title": name,
            "identifier": f"Cap. {cap}" if cap else None,
            "original_act": act.group(1).strip() if act else None,
            "type": "constitution" if is_const else "act",
            "jurisdiction": "gy", "language": "en",
            "status": "in_force",
            "revision": f"L.R.O. {lro.group(1)}" if lro else None,
            "volume": it.get("volume") or None,
            "source": PAGE,
            "source_pdf": src_pdf,
            "pages": st["pages"],
            "retrieved": retrieved,
        }
        with open(os.path.join(ROOT, rel), "w", encoding="utf-8") as f:
            f.write(front(fm) + f"# {name}\n\n" + body)
        report["converted"].append({"title": label, "file": rel, "quality": st["quality"]})
        print(rel, st["quality"], flush=True)
    json.dump(report, open(os.path.join(RAW, "convert_report.json"), "w"), indent=1)
    print(len(report["converted"]), "converted;", len(report["gaps"]), "gaps")


if __name__ == "__main__":
    main()
