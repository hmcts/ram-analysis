#!/usr/bin/env python3
"""Apply the Open Knowledge Format (OKF) interoperability surface to the RAM
Pathfinder planning artefacts.

OKF (https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf) is
"a directory of markdown files with YAML frontmatter" exposing a small set of
standard, queryable fields: the mandatory `type` plus `title`, `description`,
`resource`, `tags`, `timestamp`. This script ADDS those fields to each
artefact's frontmatter **without disturbing any existing BMAD field** (the OKF
spec defines the interoperability surface, not the content model — the two
coexist). Existing keys are never overwritten, so the script is idempotent.

Run:  python3 scripts/python/apply_okf_frontmatter.py [--dry-run]
Scope: _bmad-output/planning-artifacts/**/*.md
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_html as bh  # SRC, map_out_relpath

FM_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
TOPKEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):", re.MULTILINE)
H1_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)
DATEKEYS = ("revisedAt", "last_updated", "lastEdited", "validationDate",
            "assessmentDate", "storiedAt", "date", "assessmentDate")
DATE_VAL_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")


def okf_type(rel: str, name: str) -> str:
    if rel == "prd":
        return "PRD"
    if rel == "architecture":
        return "Architecture"
    if rel == "architecture-summary":
        return "Architecture Summary"
    if rel.startswith("architecture/sequence-diagrams/"):
        return "Sequence Diagram"
    if rel.startswith("architecture/diagrams/"):
        return "Diagram"
    if rel.startswith("architecture/analysis/"):
        return "Analysis"
    if rel.startswith("architecture/"):
        return "Architecture Shard"
    if rel == "epics" or rel == "epics/index":
        return "Epics Index"
    if rel == "epics/framework":
        return "Framework"
    if rel == "epics/fr-coverage-map":
        return "FR Coverage Map"
    if rel == "epics/requirements-inventory":
        return "Requirements Inventory"
    if rel.endswith("/index") and "phase-0" in rel:
        return "Phase Index"
    if "validation-report" in name or "prd-validation" in name:
        return "Validation Report"
    if re.search(r"epic-\d", name):
        return "Epic"
    if "sprint-change-proposal" in name:
        return "Sprint Change Proposal"
    if "implementation-readiness" in name:
        return "Readiness Report"
    return "Document"


def okf_tags(rel: str, type_: str, body: str) -> list:
    tags = ["ram-pathfinder"]
    if rel == "prd" or "PRD" in type_:
        tags.append("prd")
    if rel.startswith("architecture") or "Architecture" in type_ or type_ in ("Sequence Diagram", "Diagram", "Analysis"):
        tags.append("architecture")
    if rel.startswith("epics") or type_ in ("Epic", "Framework", "FR Coverage Map", "Requirements Inventory", "Phase Index", "Epics Index"):
        tags.append("epics")
    if type_ in ("Sprint Change Proposal", "Readiness Report", "Validation Report"):
        tags.append("change-control")
    if "phase-0" in rel:
        tags.append("phase-0")
    if "sscs" in body.lower()[:4000]:
        tags.append("sscs")
    return tags


def first_para(body: str) -> str:
    # body already has frontmatter stripped
    skip = False
    for raw in body.splitlines():
        line = raw.strip()
        if line.startswith("```"):
            skip = not skip
            continue
        if skip or not line:
            continue
        if line[0] in "#>|" or line.startswith(("- ", "* ", "+ ")) or re.match(r"^\d+\.\s", line):
            continue
        if line.startswith("---"):
            continue
        return line
    return ""


def plain(text: str) -> str:
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[\^[^\]]+\]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def truncate(s: str, n: int = 200) -> str:
    if len(s) <= n:
        return s
    cut = s[:n]
    dot = cut.rfind(". ")
    if dot > 60:
        return cut[:dot + 1]
    sp = cut.rfind(" ")
    return (cut[:sp] if sp > 0 else cut).rstrip() + "…"


def q(s: str) -> str:
    return "'" + s.replace("'", "''") + "'"


def derive(md: Path):
    rel = md.relative_to(bh.SRC).with_suffix("").as_posix()
    name = md.name.lower()
    text = md.read_text(encoding="utf-8", errors="replace")
    fm_m = FM_RE.match(text)
    fm = fm_m.group(1) if fm_m else ""
    body = text[fm_m.end():] if fm_m else text
    existing = set(TOPKEY_RE.findall(fm))

    type_ = okf_type(rel, name)
    h1 = H1_RE.search(body)
    title = plain(h1.group(1)) if h1 else rel.split("/")[-1]
    desc = truncate(plain(first_para(body))) or title

    # timestamp from an existing date-ish frontmatter field, else file mtime
    ts = None
    for k in DATEKEYS:
        m = re.search(rf"^{k}:\s*(.+)$", fm, re.MULTILINE)
        if m:
            d = DATE_VAL_RE.search(m.group(1))
            if d:
                ts = d.group(1)
                break
    if not ts:
        import datetime
        ts = datetime.date.fromtimestamp(md.stat().st_mtime).isoformat()

    resource = bh.map_out_relpath(rel) + ".html"
    tags = okf_tags(rel, type_, body)

    # Only OKF keys that are MISSING (idempotent; never overwrite BMAD/existing)
    candidates = [
        ("type", q(type_)),
        ("title", q(title)),
        ("description", q(desc)),
        ("resource", q(resource)),
        ("tags", "[" + ", ".join(tags) + "]"),
        ("timestamp", q(ts)),
    ]
    add = [(k, v) for k, v in candidates if k not in existing]
    return rel, fm_m, add, text


def main() -> int:
    dry = "--dry-run" in sys.argv
    files = sorted(bh.SRC.rglob("*.md"))
    changed = 0
    for md in files:
        rel, fm_m, add, text = derive(md)
        if not add:
            continue
        changed += 1
        block = "".join(f"{k}: {v}\n" for k, v in add)
        if dry:
            print(f"\n{rel}")
            for k, v in add:
                print(f"   + {k}: {v}")
            continue
        if fm_m:
            new = text[:fm_m.start()] + "---\n" + block + fm_m.group(1) + "\n---\n" + text[fm_m.end():]
        else:
            new = "---\n" + block + "---\n\n" + text
        md.write_text(new, encoding="utf-8")
    verb = "would update" if dry else "updated"
    print(f"\nOKF frontmatter: {verb} {changed}/{len(files)} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
