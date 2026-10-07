#!/usr/bin/env python3
"""Render a build booklet directory (cover.md + section-*.md) into a single view.html.

Usage: render_booklet.py <booklet-dir> [--open] [--out PATH]

Outlined sections have no file; they come from the rows of the cover's
"## The sections" table. No third-party dependencies: the Markdown is embedded
as JSON and rendered in the browser with marked + mermaid (loaded from a CDN).
"""
import argparse
import json
import re
import sys
import webbrowser
from datetime import datetime
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "viewer.html"

SEP = r"\s*[:\-—–]\s*"
STEP_RE = re.compile(rf"^Step\s+(\d+)\.(\d+){SEP}(.*)$", re.I)
RECAP_RE = re.compile(rf"^(?:Recap|Review)(?:{SEP}(.*))?$", re.I)
CHECKBOX_RE = re.compile(r"^\s*[-*]\s+\[([ xX])\]\s+Done\s*$", re.M)
FILE_RE = re.compile(r"^(?:section|bag)-(\d+)(?:-.*)?\.md$")
TYPE_RE = re.compile(r"\*\*Type:\*\*\s*(design|prototype|build)", re.I)
NAME_TYPE_RE = re.compile(r"\((design|prototype)\)", re.I)
TITLE_PREFIX_RE = re.compile(rf"^(?:Section|Bag)\s+\d+{SEP}", re.I)
UNWRITTEN = ("_Written when you finish this section._", "_Written when you finish this bag._")


def split_pages(md: str):
    """Split markdown into (h1_title, intro_md, [(h2_title, body_md), ...]), ignoring fenced code."""
    title, intro, pages, current, fence = None, [], [], None, None
    for line in md.splitlines():
        stripped = line.lstrip()
        m = re.match(r"^(`{3,}|~{3,})", stripped)
        if m:
            if fence is None:
                fence = m.group(1)
            elif stripped.startswith(fence):
                fence = None
            (current[1] if current else intro).append(line)
            continue
        if fence is None:
            if title is None and line.startswith("# "):
                title = line[2:].strip()
                continue
            if line.startswith("## "):
                if current:
                    pages.append(current)
                current = (line[3:].strip(), [])
                continue
        (current[1] if current else intro).append(line)
    if current:
        pages.append(current)
    return title, "\n".join(intro).strip(), [(t, "\n".join(b).strip()) for t, b in pages]


def classify(page_title: str, body: str):
    m = STEP_RE.match(page_title)
    if m:
        cb = CHECKBOX_RE.search(body)
        done = bool(cb and cb.group(1).lower() == "x")
        body = CHECKBOX_RE.sub("", body, count=1).strip() if cb else body
        return {"kind": "step", "num": f"{m.group(1)}.{m.group(2)}",
                "title": m.group(3).strip(), "done": done, "md": body}
    m = RECAP_RE.match(page_title)
    if m:
        written = bool(body.strip()) and not any(u in body for u in UNWRITTEN)
        return {"kind": "recap", "title": (m.group(1) or "").strip() or page_title,
                "written": written, "md": body}
    return {"kind": "page", "title": page_title, "md": body}


def parse_sections_table(cover_pages):
    """Rows of the cover's sections table: {num: {name, have, status, type, phase}}.

    Optional `### <Phase>` headings inside the page group the rows that follow them.
    """
    rows = {}
    for title, body in cover_pages:
        if not re.match(r"^the\s+(sections|bags)$", title.strip(), re.I):
            continue
        phase = None
        for line in body.splitlines():
            h = re.match(r"^#{3,4}\s+(.*\S)\s*$", line)
            if h:
                phase = h.group(1)
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 2:
                continue
            m = re.match(r"^(\d+)\.?$", cells[0])
            name = cells[1]
            if not m:  # also accept "| 1. Name | ..." style
                m2 = re.match(r"^(\d+)\.\s+(.*)$", cells[0])
                if not m2:
                    continue
                m, name, cells = m2, m2.group(2), [cells[0]] + cells
            t = NAME_TYPE_RE.search(name)
            rows[int(m.group(1))] = {
                "name": NAME_TYPE_RE.sub("", name).strip(" *"),
                "have": cells[2] if len(cells) > 2 else "",
                "status": cells[3] if len(cells) > 3 else "",
                "type": t.group(1).lower() if t else "build",
                "phase": phase,
            }
    return rows


def load_booklet(root: Path):
    cover_path = root / "cover.md"
    if not cover_path.exists():
        sys.exit(f"error: {cover_path} not found")
    c_title, c_intro, c_pages = split_pages(cover_path.read_text(encoding="utf-8"))
    cover = {"title": c_title or root.name, "intro": c_intro,
             "pages": [{"kind": "page", "title": t, "md": b} for t, b in c_pages]}
    table = parse_sections_table(c_pages)

    sections = {}
    for f in root.glob("*.md"):
        m = FILE_RE.match(f.name)
        if not m:
            continue
        num = int(m.group(1))
        title, intro, pages = split_pages(f.read_text(encoding="utf-8"))
        pages = [classify(t, b) for t, b in pages]
        steps = [p for p in pages if p["kind"] == "step"]
        if not steps:
            status = "outlined"
        elif all(s["done"] for s in steps):
            status = "done"
        else:
            status = "in-progress" if any(s["done"] for s in steps) else "ready"
        t = TYPE_RE.search(intro)
        sections[num] = {"file": f.name, "num": num,
                         "title": TITLE_PREFIX_RE.sub("", title or f.stem),
                         "type": t.group(1).lower() if t else table.get(num, {}).get("type", "build"),
                         "intro": intro, "pages": pages, "status": status}

    for num, row in table.items():
        if num in sections:
            continue
        note = f"> **You'll have:** {row['have']}" if row["have"] else ""
        after = re.search(r"after\s+([\d,\s&and]+)", row["status"] or "", re.I)
        if after:
            note += f"\n> **Waits on:** Section {after.group(1).strip()}"
        sections[num] = {"file": None, "num": num, "title": row["name"], "type": row["type"],
                         "intro": note, "pages": [], "status": "outlined"}

    for num, sec in sections.items():
        sec["phase"] = table.get(num, {}).get("phase")
    ordered = [sections[n] for n in sorted(sections)]
    current = next((s for s in ordered if s["status"] != "done"), None)
    for s in ordered:
        s["current"] = s is current

    features = []
    for sub in ("features", "sets"):
        d = root / sub
        if d.is_dir():
            features += [f"{sub}/{p.parent.name}" for p in sorted(d.glob("*/cover.md"))]

    return {"cover": cover, "sections": ordered, "features": features,
            "rendered": datetime.now().strftime("%Y-%m-%d %H:%M")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("booklet_dir")
    ap.add_argument("--out", help="output HTML path (default: <booklet_dir>/view.html)")
    ap.add_argument("--open", action="store_true", help="open in the default browser")
    args = ap.parse_args()

    root = Path(args.booklet_dir).expanduser().resolve()
    data = load_booklet(root)
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html = TEMPLATE.read_text(encoding="utf-8")
    html = html.replace("__BOOKLET_TITLE__", data["cover"]["title"].replace("<", "&lt;"))
    html = html.replace("__BOOKLET_DATA__", payload)

    out = Path(args.out).expanduser().resolve() if args.out else root / "view.html"
    out.write_text(html, encoding="utf-8")

    steps = [p for s in data["sections"] for p in s["pages"] if p["kind"] == "step"]
    done = sum(p["done"] for p in steps)
    outlined = sum(s["status"] == "outlined" for s in data["sections"])
    print(f"Wrote {out}")
    print(f"{len(data['sections'])} sections ({outlined} outlined), {done}/{len(steps)} written steps done")
    if args.open:
        webbrowser.open(out.as_uri())


if __name__ == "__main__":
    main()
