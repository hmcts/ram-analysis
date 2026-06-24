#!/usr/bin/env python3
"""Build schema diagrams as D2 sources (rendered to PNG via the ELK engine).

This is the D2 counterpart to ``build_schema_diagram.py``. It reuses that
module's schema loading, PK backfill, FK inference and domain clustering so the
two generators can never drift apart — only the rendering target differs:

  - ``build_schema_diagram.py``  → Graphviz DOT  (legacy record/table render)
  - ``build_schema_diagram_d2.py`` → D2 + ELK     (house standard, this file)

Why D2 + ELK:
  - native ``sql_table`` shape gives proper ER tables with column-level edge
    attachment and PK/FK/UNQ markers — no hand-rolled HTML labels;
  - the ELK ("Eclipse Layout Kernel") engine routes connections orthogonally
    and minimises crossings, which is exactly what was asked for.

Each emitted ``.d2`` file pins the layout engine in-file via
``vars.d2-config.layout-engine: elk`` so it renders correctly through the
shared ``scripts/render_diagram.sh`` wrapper (which does not pass ``--layout``).

Output goes to ``docs/architecture/asis/database/`` alongside the source data,
overwriting the per-area PNGs so existing README links keep working.

Faithfulness vs. the DOT version:
  - PK / FK (in-area) / UK markers are preserved as native sql_table constraints.
  - Cross-area and external references are shown by folding the target into the
    column's type cell (e.g. ``NUMBER → TBL_JUDGES``) with NO edge drawn — same
    rule as the DOT diagrams.
  - The per-column ``NN`` (NOT NULL) marker is intentionally dropped from the
    visual to cut noise; nullability remains in ``ji_schema.json``.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Reuse the single source of truth for schema/FK/cluster logic.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_schema_diagram as g  # noqa: E402

REPO_ROOT = g.REPO_ROOT
DB_DIR = g.DB_DIR
CLUSTERS = g.CLUSTERS
EXTERNAL_REF_HINTS = g.EXTERNAL_REF_HINTS

# Gray header bar for every detail-diagram table (sql_table `style.fill`
# colours the title bar; rows stay white). Medium gray keeps the white title
# text legible.
DETAIL_HEADER_FILL = "#6e7781"

# Tables to drop from a specific area's DETAIL diagram only (the overview still
# lists them). Keyed by cluster key.
DETAIL_EXCLUDE: Dict[str, Set[str]] = {
    "judges-patterns": {"TBL_JUDGES_MONTHLY_STATS"},
}

# Edge styling per FK confidence (mirrors the DOT palette).
EDGE_STYLE = {
    "high": 'style.stroke: "#1f6feb"; style.stroke-width: 2',
    "medium": 'style.stroke: "#6c757d"; style.stroke-width: 1; style.stroke-dash: 4',
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def d2_quote(s: str) -> str:
    """Wrap a value in double quotes, escaping embedded quotes."""
    return '"' + s.replace('"', '\\"') + '"'


def trigger_badge(triggers: List[Dict]) -> str:
    """Plain-text trigger badge, e.g. ``[BI BU]``. Empty when no triggers."""
    if not triggers:
        return ""
    seen: Set[str] = set()
    for tr in triggers:
        seen.add(f"{tr['timing'][0].upper()}{tr['event'][0].upper()}")
    return " [" + " ".join(sorted(seen)) + "]"


def safe_id(name: str) -> str:
    """A D2-safe identifier (clusters use hyphens; D2 keys prefer underscores)."""
    return re.sub(r"[^A-Za-z0-9_]", "_", name)


def external_hint_compact(col: str) -> str:
    hint = EXTERNAL_REF_HINTS.get(col, "external")
    return hint.replace("External: ", "").replace(" (not in this PDF)", "")


# ---------------------------------------------------------------------------
# Detail diagram (one per cluster) — full sql_table ER view
# ---------------------------------------------------------------------------


def build_detail_d2(schema: Dict, fks: List[Dict], cluster_key: str,
                    cluster_label: str, cluster_tables: List[str], color: str) -> str:
    pk_map = g.build_pk_map(schema)
    # Drop any tables excluded from this area's detail view (overview keeps them).
    excluded = DETAIL_EXCLUDE.get(cluster_key, set())
    cluster_tables = [t for t in cluster_tables if t not in excluded]
    cluster_set = set(cluster_tables)

    # Intra-cluster FK edges only (both ends inside this area).
    intra_fks = [
        fk for fk in fks
        if fk["from_table"] in cluster_set
        and fk["to_table"] in cluster_set
        and fk["to_table"] != "_EXTERNAL_"
    ]
    # Map (table -> column) FK origins for marker/type decisions.
    fk_by_table_col: Dict[Tuple[str, str], Dict] = {
        (fk["from_table"], fk["from_col"]): fk for fk in fks
    }

    lines: List[str] = [
        "vars: { d2-config: { layout-engine: elk } }",
        "direction: right",
        "",
        f"title: |md",
        f"  ## JI as-is schema — {cluster_label}",
        f"  PK / FK (in-area) / UNQ markers · trigger badges `[B/A × I/U/D]` · "
        f"intra-area FK edges only · cross-area & external refs shown in the type cell",
        f"| {{ near: top-center; style.font-size: 22 }}",
        "",
    ]

    for tbl_name in cluster_tables:
        tbl = schema["tables"].get(tbl_name)
        if not tbl:
            continue
        pk = tbl.get("primary_key") or {"columns": []}
        pk_cols = set(pk["columns"])
        uk_cols: Set[str] = set()
        for idx in tbl["indexes"]:
            if idx["unique"] and "_UK" in idx["name"]:
                uk_cols.update(idx["columns"])

        badge = trigger_badge(tbl["triggers"])
        label = tbl_name + badge
        lines.append(f"{tbl_name}: {d2_quote(label)} {{")
        lines.append("  shape: sql_table")
        lines.append(f'  style.fill: "{DETAIL_HEADER_FILL}"')
        for col in tbl["columns"]:
            cname = col["name"]
            ctype = col["type"]
            constraints: List[str] = []
            type_str = ctype

            if cname in pk_cols:
                constraints.append("primary_key")

            fk = fk_by_table_col.get((tbl_name, cname))
            if fk:
                if fk["confidence"] == "external":
                    type_str = f"{ctype} → {external_hint_compact(cname)}"
                elif fk["to_table"] in cluster_set:
                    if cname not in pk_cols:
                        constraints.append("foreign_key")
                else:
                    type_str = f"{ctype} → {fk['to_table']}"

            if cname in uk_cols and cname not in pk_cols:
                constraints.append("unique")

            constraint_str = ""
            if constraints:
                constraint_str = " {constraint: [" + "; ".join(constraints) + "]}"
            lines.append(f"  {cname}: {d2_quote(type_str)}{constraint_str}")
        lines.append("}")
        lines.append("")

    # Intra-cluster FK edges, column-to-column.
    drawn: Set[Tuple[str, str]] = set()
    for fk in intra_fks:
        src = f'{fk["from_table"]}.{fk["from_col"]}'
        dst = f'{fk["to_table"]}.{fk["to_col"]}'
        key = (src, dst)
        if key in drawn:
            continue
        drawn.add(key)
        style = EDGE_STYLE.get(fk["confidence"], EDGE_STYLE["high"])
        lines.append(f"{src} -> {dst}: {{ {style} }}")

    lines.append("")
    lines.append("legend: |md")
    lines.append("  **Legend** — "
                 "`PK` primary · `FK` in-area (line) · `UNQ` unique · "
                 "`→ TBL_X` cross-area ref (no line) · `→ hint` external (not in PDF)  ")
    lines.append("  ━━ blue solid = HIGH-confidence FK · - - grey dashed = MEDIUM-confidence FK")
    lines.append("| { near: bottom-center; style.font-size: 13 }")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Overview diagram — clusters as containers + aggregate inter-area edges
# ---------------------------------------------------------------------------


def build_overview_d2(schema: Dict, fks: List[Dict]) -> str:
    cmap = g.table_cluster_map()

    # Aggregate inter-cluster FK counts (skip externals + intra-cluster).
    cluster_edges: Dict[Tuple[str, str], int] = {}
    for fk in fks:
        if fk["to_table"] == "_EXTERNAL_" or fk["confidence"] == "external":
            continue
        c_from = cmap.get(fk["from_table"])
        c_to = cmap.get(fk["to_table"])
        if not c_from or not c_to or c_from == c_to:
            continue
        cluster_edges[(c_from, c_to)] = cluster_edges.get((c_from, c_to), 0) + 1

    lines: List[str] = [
        "vars: { d2-config: { layout-engine: elk } }",
        "direction: right",
        "",
        "title: |md",
        "  ## JI as-is database schema — overview",
        "  46 production tables in 6 areas · inter-area FK relationships aggregated "
        "(edge label = count) · 0 explicit FK constraints in source DDL",
        "| { near: top-center; style.font-size: 22 }",
        "",
    ]

    for key, label, tables, color in CLUSTERS:
        cid = safe_id(key)
        present = [t for t in tables if t in schema["tables"]]
        clabel = f"{label} ({len(present)} tables)"
        lines.append(f"{cid}: {d2_quote(clabel)} {{")
        lines.append(f'  style.fill: "{color}"')
        lines.append('  style.stroke: "#999"')
        lines.append("  grid-columns: 1")
        for tbl_name in present:
            tbl = schema["tables"][tbl_name]
            ncols = len(tbl["columns"])
            badge = trigger_badge(tbl["triggers"])
            node_label = f"{tbl_name} ({ncols}){badge}"
            lines.append(f"  {tbl_name}: {d2_quote(node_label)} {{ shape: rectangle; "
                         f'style.fill: "#ffffff"; style.font-size: 13 }}')
        lines.append("}")
        lines.append("")

    for (c_from, c_to), count in cluster_edges.items():
        width = min(1 + count // 3, 6)
        lines.append(
            f'{safe_id(c_from)} -> {safe_id(c_to)}: {d2_quote(str(count))} '
            f'{{ style.stroke: "#1f6feb"; style.stroke-width: {width}; '
            f'style.font-color: "#0a3069" }}'
        )

    lines.append("")
    lines.append("legend: |md")
    lines.append("  **Legend** — box = area · `TBL_NAME (n)` n = column count · "
                 "`[B/A × I/U/D]` = trigger badge  ")
    lines.append("  Arrow label = count of inferred inter-area FKs (stroke width scales with count)")
    lines.append("| { near: bottom-center; style.font-size: 13 }")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def render_d2(d2_path: Path, png_path: Path) -> None:
    subprocess.run(["d2", "--pad", "24", str(d2_path), str(png_path)], check=True)


def main() -> int:
    if not g.SCHEMA_JSON.exists():
        print(f"error: run parse_ji_ddl.py first; {g.SCHEMA_JSON} not found", file=sys.stderr)
        return 1
    if shutil.which("d2") is None:
        print("error: d2 not found on PATH — install with: brew install d2", file=sys.stderr)
        return 1

    schema = g.load_schema()
    print(f"Loaded {len(schema['tables'])} production tables")
    pk_map = g.build_pk_map(schema)
    fks = g.infer_fks(schema, pk_map)
    n_high = sum(1 for fk in fks if fk["confidence"] == "high")
    n_med = sum(1 for fk in fks if fk["confidence"] == "medium")
    n_ext = sum(1 for fk in fks if fk["confidence"] == "external")
    print(f"FKs inferred: {n_high} HIGH, {n_med} MEDIUM, {n_ext} EXTERNAL")

    overview_d2 = DB_DIR / "ji_schema_overview.d2"
    overview_png = DB_DIR / "ji_schema_overview.png"
    overview_d2.write_text(build_overview_d2(schema, fks))
    print(f"wrote {overview_d2.name}")
    render_d2(overview_d2, overview_png)
    print(f"rendered {overview_png.name}")

    for key, label, tables, color in CLUSTERS:
        d2_path = DB_DIR / f"ji_schema_{key}.d2"
        png_path = DB_DIR / f"ji_schema_{key}.png"
        d2_path.write_text(build_detail_d2(schema, fks, key, label, tables, color))
        print(f"wrote {d2_path.name}")
        render_d2(d2_path, png_path)
        print(f"rendered {png_path.name}")

    print("\nDone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
