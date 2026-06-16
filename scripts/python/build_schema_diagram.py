#!/usr/bin/env python3
"""Schema model + companion markdown for the JI as-is database.

This module is the single source of truth for the schema graph: it loads the
parsed DDL, backfills PKs, infers FK relationships and assigns tables to domain
clusters. `build_schema_diagram_d2.py` imports these functions to render the
diagrams (D2 + ELK) — the diagrams are NOT generated here.

What this script produces when run directly:
  - `ji_schema_companion.md` — trigger reference, external-reference inventory,
    FK-inference rationale and the full inferred-FK table.

Pipeline:
  1. Load `ji_schema.json` (produced by `parse_ji_ddl.py`).
  2. Backfill missing PKs from unique indexes named `*_PK`.
  3. Build PK→owner map; infer FK relationships from column-name conventions
     with HIGH / MEDIUM / LOW confidence.
  4. Assign each TBL_* table to a domain cluster.
  5. Write the companion markdown.

Exclusions:
  - TMP_* tables are NOT modelled (per user direction).
  - Foreign keys are ALL inferred — no explicit FK constraints exist in the
    source DDL. Confidence is HIGH / MEDIUM / EXTERNAL.

Output goes to `docs/architecture/asis/database/`.

History: this script used to emit Graphviz DOT + PNG diagrams. Diagram
generation moved to D2 + ELK (`build_schema_diagram_d2.py`); the DOT path was
removed once it became redundant.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
DB_DIR = REPO_ROOT / "docs" / "architecture" / "asis" / "database"
SCHEMA_JSON = DB_DIR / "ji_schema.json"

# ---------------------------------------------------------------------------
# Domain clustering
# ---------------------------------------------------------------------------
# Each cluster: (cluster_key, display_label, list_of_table_names, palette_color)
# Palette colors are soft pastels distinct from each other.

CLUSTERS: List[Tuple[str, str, List[str], str]] = [
    (
        "judges-profile",
        "Judges Profile & Reference",
        [
            "TBL_JUDGES",
            "TBL_JUDGES_MASTER",
            "TBL_JUDGES_USER_LINKS",
            "TBL_JUDGE_TYPES",
            "TBL_JUDGE_STATUSES",
            "TBL_JUDGE_CIRCUITS",
            "TBL_LEADERSHIP_JUDGE_TYPES",
            "TBL_JUDGE_TYPE_PROMOTION",
        ],
        "#E3F2FD",  # light blue
    ),
    (
        "judges-patterns",
        "Working Patterns, Tickets & Stats",
        [
            "TBL_JUDGES_WORK_PATTERNS",
            "TBL_JUDGES_WP_DETAIL",
            "TBL_JUDGES_JURIS_SPLIT",
            "TBL_JUDGE_JURIS",
            "TBL_JUDGE_TICKET_TYPES",
            "TBL_JUDGES_TICKETS",
            "TBL_JUDGE_COURTS_LINK",
            "TBL_JUDGE_FEE_RATES",
            "TBL_JUDGES_ANNUAL_LEAVE",
            "TBL_JUDGES_BOOKING_STATS",
            "TBL_JUDGES_MONTHLY_STATS",
        ],
        "#E8F5E9",  # light green
    ),
    (
        "absence-cover",
        "Absence & Cover Workflow",
        [
            "TBL_JI_ABS_OB",
            "TBL_JI_ABS_OB_DETAIL",
            "TBL_JI_ABS_OB_CATS",
            "TBL_JI_ABS_OB_TYPES",
            "TBL_JI_ABS_OB_VAC_OPTS",
            "TBL_JI_VACANCIES",
            "TBL_JI_VACANCY_GROUPS",
            "TBL_JI_VAC_CANCEL_REASONS",
        ],
        "#FFF3E0",  # light orange
    ),
    (
        "bookings-sittings",
        "Bookings & Sittings",
        [
            "TBL_JI_FP_BOOKINGS",
            "TBL_JI_FP_BOOKING_DETAIL",
            "TBL_JI_FP_BOOKING_TYPES",
            "TBL_JI_FP_CANCELLERS",
            "TBL_JI_PLANNED_SITTINGS",
        ],
        "#FCE4EC",  # light pink
    ),
    (
        "reference-work",
        "Reference Data — Work, Durations, Areas, Links",
        [
            "TBL_JI_PLANNED_WORK_TYPES",
            "TBL_JI_PLANNED_WORK_CATS",
            "TBL_JI_ACTUAL_WORK_TYPES",
            "TBL_JI_ACTUAL_WORK_CATS",
            "TBL_JI_SITTING_DURS",
            "TBL_JI_AREAS",
            "TBL_JI_EXTRA_NWDS",
            "TBL_JI_LOC_JT_AWD_LINKS",
            "TBL_JI_LOC_JT_PWD_LINKS",
            "TBL_JI_LOC_JT_SD_LINKS",
            "TBL_JI_UA_JT_LINKS",
        ],
        "#F3E5F5",  # light purple
    ),
    (
        "audit-cross-cutting",
        "Audit & Cross-cutting",
        [
            "TBL_JI_CHANGES",
            "TBL_JI_CHANGE_TYPES",
            "TBL_JI_RESTR_ITIN_USERS",
        ],
        "#FFFDE7",  # light yellow
    ),
]

# ---------------------------------------------------------------------------
# External-reference column hints
# ---------------------------------------------------------------------------
# Columns that almost certainly refer to tables NOT in this PDF. These get a
# special "External" marker in the diagram and are documented separately.

EXTERNAL_REF_HINTS: Dict[str, str] = {
    "LOC_ID": "External: LOCATIONS / OFFICES (not in this PDF)",
    "LOC_TYPE_ID": "External: LOCATION TYPES (not in this PDF)",
    "BASE_LOC_ID": "External: LOCATIONS (not in this PDF)",
    "BASE_LOC_TYPE_ID": "External: LOCATION TYPES (not in this PDF)",
    "HEARING_LOC_ID": "External: LOCATIONS (not in this PDF)",
    "HEARING_LOC_TYPE_ID": "External: LOCATION TYPES (not in this PDF)",
    "REGION_ID": "External: REGIONS (not in this PDF)",
    "CUT_COURTROOM_ID": "External: COURTROOMS / CUT_* (not in this PDF)",
    "CUT_OWNER_ID": "External: COURTROOMS / CUT_* (not in this PDF)",
    "COURT_ID": "External: COURTS (not in this PDF)",
    "HMCS_LEGAL_TIER_CODE": "External: HMCS Legal Tier codes (not in this PDF)",
    "FP_STATUS_ID": "External: FP Status lookup (not in this PDF)",
    "LONDON_WT_STATUS_ID": "External: London Weighting Status lookup (not in this PDF)",
    "OPT_USER_ID": "External: OPT users (not in this PDF)",
    "FILL_ACTION_ID": "External: Fill Action lookup (not in this PDF)",
    "ABS_OB_LENGTH_TYPE_ID": "External: Absence Length Type lookup (not in this PDF)",
    "VACANCY_STATUS_ID": "External: Vacancy Status lookup (not in this PDF)",
    "SITTING_TYPE_ID": "External: Sitting Type lookup (not in this PDF)",
}

# ---------------------------------------------------------------------------
# Loading + PK backfill
# ---------------------------------------------------------------------------


def load_schema() -> Dict:
    schema = json.loads(SCHEMA_JSON.read_text())
    # Filter to production tables only (drop TMP_*)
    schema["tables"] = {
        name: t for name, t in schema["tables"].items()
        if not name.startswith("TMP_")
    }
    # Backfill missing PKs from unique *_PK indexes
    for name, t in schema["tables"].items():
        if t["primary_key"]:
            continue
        for idx in t["indexes"]:
            if idx["unique"] and idx["name"].endswith("_PK"):
                t["primary_key"] = {
                    "name": idx["name"],
                    "columns": idx["columns"],
                    "from_index": True,
                }
                break
    return schema


# ---------------------------------------------------------------------------
# FK inference
# ---------------------------------------------------------------------------


def build_pk_map(schema: Dict) -> Dict[str, str]:
    """Map: PK column name → owner table.

    Only single-column PKs participate (composite PKs are link-table style).
    """
    pk_map: Dict[str, str] = {}
    for name, t in schema["tables"].items():
        pk = t.get("primary_key")
        if not pk or len(pk["columns"]) != 1:
            continue
        col = pk["columns"][0]
        # If two tables claim the same PK column, prefer the one whose name
        # contains the PK column name (more specific owner). This handles e.g.
        # tables that legitimately re-use a code column.
        if col in pk_map:
            existing = pk_map[col]
            # Heuristic: shorter name wins if both contain the column
            if name in existing:
                continue
            if existing in name:
                pk_map[col] = name
                continue
        pk_map[col] = name
    return pk_map


def infer_fks(schema: Dict, pk_map: Dict[str, str]) -> List[Dict]:
    """For every non-PK column in every table, look for FK candidates.

    Returns list of dicts: {from_table, from_col, to_table, to_col, confidence,
    note?}
    """
    fks: List[Dict] = []
    for name, t in schema["tables"].items():
        pk = t.get("primary_key") or {"columns": []}
        pk_cols = set(pk["columns"])
        for col in t["columns"]:
            cname = col["name"]
            # Skip the PK columns themselves
            if cname in pk_cols and len(pk["columns"]) == 1:
                continue
            # Skip non-ID-ish columns
            if not (cname.endswith("_ID") or cname.endswith("_CODE")
                    or cname.endswith("_TYPE") or cname == "JUDGE_CODE"):
                continue

            # External-reference hint check
            if cname in EXTERNAL_REF_HINTS:
                fks.append({
                    "from_table": name,
                    "from_col": cname,
                    "to_table": "_EXTERNAL_",
                    "to_col": cname,
                    "confidence": "external",
                    "note": EXTERNAL_REF_HINTS[cname],
                })
                continue

            # HIGH: exact PK match
            if cname in pk_map and pk_map[cname] != name:
                fks.append({
                    "from_table": name,
                    "from_col": cname,
                    "to_table": pk_map[cname],
                    "to_col": cname,
                    "confidence": "high",
                })
                continue

            # MEDIUM: column ends with a known PK column (prefixed reference)
            # e.g. START_SITTING_DUR_ID → SITTING_DUR_ID → TBL_JI_SITTING_DURS
            #      JI_PLANNED_WORK_TYPE_ID → ? matches no PK exactly
            matched = False
            best_match = None
            best_pk_len = 0
            for pk_col, owner in pk_map.items():
                # Match only when the suffix is at least 5 chars to avoid noise
                # like X_ID matching all *_ID columns.
                if len(pk_col) < 5:
                    continue
                if cname == pk_col:
                    continue  # already handled above
                # Prefix-with-underscore match: column is "<PREFIX>_<PK>"
                if cname.endswith("_" + pk_col):
                    if len(pk_col) > best_pk_len:
                        best_pk_len = len(pk_col)
                        best_match = (pk_col, owner)
            if best_match is not None:
                pk_col, owner = best_match
                if owner != name:
                    fks.append({
                        "from_table": name,
                        "from_col": cname,
                        "to_table": owner,
                        "to_col": pk_col,
                        "confidence": "medium",
                    })
                    matched = True
            if matched:
                continue

            # LOW: column has *_ID suffix but no PK match; might be unmapped.
            # Skip silently — including these would create noise.

    return fks


# ---------------------------------------------------------------------------
# Cluster helpers (shared with the D2 diagram generator)
# ---------------------------------------------------------------------------


def table_cluster_map() -> Dict[str, str]:
    out = {}
    for key, _label, tables, _color in CLUSTERS:
        for t in tables:
            out[t] = key
    return out


# ---------------------------------------------------------------------------
# Companion markdown
# ---------------------------------------------------------------------------


def build_companion_md(schema: Dict, fks: List[Dict]) -> str:
    """Build the companion reference markdown: triggers, externals, FK rationale."""
    lines = ["# JI as-is database — diagram companion reference", ""]
    lines.append("This document accompanies the PNG schema diagrams in this folder. It contains:")
    lines.append("")
    lines.append("- Trigger reference (every trigger, its table, timing, event, and body)")
    lines.append("- External-reference inventory (columns pointing to tables NOT in this PDF)")
    lines.append("- FK inference confidence notes")
    lines.append("")

    # --- Trigger reference ---
    lines.append("## Trigger reference")
    lines.append("")
    lines.append("All 24 triggers extracted from the source DDL. Triggers are predominantly mechanical: `BI_*` (before-insert) assign the PK from a sequence; `BU_*` (before-update) maintain `LAST_MODIFIED_BY` / `LAST_MODIFIED_DATE` audit columns.")
    lines.append("")
    lines.append("| Table | Trigger | Timing | Event | Purpose (summary) |")
    lines.append("|---|---|---|---|---|")
    for tname in sorted(schema["tables"]):
        t = schema["tables"][tname]
        for tr in t["triggers"]:
            timing = tr["timing"].capitalize()
            event = tr["event"]
            body = tr["body"]
            # Determine summary purpose
            if "nextval" in body and "PK" in tr["name"].upper() or "BI_" in tr["name"]:
                purpose = "Auto-assign PK from sequence"
            elif "LAST_MODIFIED" in body.upper():
                purpose = "Maintain LAST_MODIFIED_BY/DATE audit"
            elif "nextval" in body:
                purpose = "Auto-assign PK from sequence"
            else:
                purpose = "—"
            lines.append(f"| `{tname}` | `{tr['name']}` | {timing} | {event} | {purpose} |")
    lines.append("")
    lines.append("### Trigger bodies (full)")
    lines.append("")
    for tname in sorted(schema["tables"]):
        t = schema["tables"][tname]
        if not t["triggers"]:
            continue
        lines.append(f"#### `{tname}`")
        lines.append("")
        for tr in t["triggers"]:
            lines.append(f"**`{tr['name']}`** — {tr['timing']} {tr['event']}")
            lines.append("")
            lines.append("```sql")
            lines.append(tr["body"])
            lines.append("```")
            lines.append("")

    # --- External references ---
    lines.append("## External-reference inventory")
    lines.append("")
    lines.append("These columns reference tables that are **NOT present in the source PDF**. Likely live in a separate reference-data dump (locations, regions, courtrooms, OPT user accounts, status lookups). Confirm with the data-dictionary owner before treating them as authoritative.")
    lines.append("")
    lines.append("| Column | Inferred target | Tables using it |")
    lines.append("|---|---|---|")
    # Group external refs by column name
    by_col: Dict[str, Set[str]] = {}
    for fk in fks:
        if fk["confidence"] != "external":
            continue
        by_col.setdefault(fk["from_col"], set()).add(fk["from_table"])
    for col in sorted(by_col):
        users = ", ".join(f"`{t}`" for t in sorted(by_col[col]))
        hint = EXTERNAL_REF_HINTS.get(col, "External")
        lines.append(f"| `{col}` | {hint} | {users} |")
    lines.append("")

    # --- FK inference notes ---
    lines.append("## FK inference notes")
    lines.append("")
    lines.append("The source DDL contains **zero explicit `FOREIGN KEY` constraints**. Every relationship in the diagrams is inferred from column-naming conventions. Confidence buckets:")
    lines.append("")
    lines.append("- **HIGH (solid line, blue)** — column name exactly matches another table's primary-key column. Example: `JI_ABS_OB_ID` in `TBL_JI_VACANCIES` matches `TBL_JI_ABS_OB.JI_ABS_OB_ID`.")
    lines.append("- **MEDIUM (dashed line, grey)** — column is a *prefixed* version of another table's PK column (≥ 5-char suffix). Example: `START_SITTING_DUR_ID` and `END_SITTING_DUR_ID` both end with `SITTING_DUR_ID`, the PK of `TBL_JI_SITTING_DURS`.")
    lines.append("- **EXTERNAL (dotted line, light grey)** — column references a table outside this PDF.")
    lines.append("")
    lines.append("Columns ending in `_ID` or `_CODE` that match neither rule are flagged in the diagram body but no edge is drawn. They may be valid FK references to tables not yet identified.")
    lines.append("")
    lines.append("### Counts")
    lines.append("")
    n_high = sum(1 for fk in fks if fk["confidence"] == "high")
    n_med = sum(1 for fk in fks if fk["confidence"] == "medium")
    n_ext = sum(1 for fk in fks if fk["confidence"] == "external")
    lines.append(f"- HIGH confidence FKs: **{n_high}**")
    lines.append(f"- MEDIUM confidence FKs: **{n_med}**")
    lines.append(f"- EXTERNAL references: **{n_ext}**")
    lines.append("")

    # --- All inferred FKs table ---
    lines.append("### All inferred FKs")
    lines.append("")
    lines.append("| Source table | Source column | → | Target table | Target column | Confidence |")
    lines.append("|---|---|---|---|---|---|")
    for fk in sorted(fks, key=lambda f: (f["from_table"], f["from_col"])):
        if fk["to_table"] == "_EXTERNAL_":
            tgt_table = "_(external)_"
            tgt_col = "—"
        else:
            tgt_table = f"`{fk['to_table']}`"
            tgt_col = f"`{fk['to_col']}`"
        lines.append(
            f"| `{fk['from_table']}` | `{fk['from_col']}` | → | {tgt_table} | {tgt_col} | {fk['confidence']} |"
        )
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    if not SCHEMA_JSON.exists():
        print(f"error: run parse_ji_ddl.py first; {SCHEMA_JSON} not found", file=sys.stderr)
        return 1

    schema = load_schema()
    print(f"Loaded {len(schema['tables'])} production tables")

    pk_map = build_pk_map(schema)
    print(f"PK map: {len(pk_map)} single-column PKs available for FK matching")

    fks = infer_fks(schema, pk_map)
    n_high = sum(1 for fk in fks if fk["confidence"] == "high")
    n_med = sum(1 for fk in fks if fk["confidence"] == "medium")
    n_ext = sum(1 for fk in fks if fk["confidence"] == "external")
    print(f"FKs inferred: {n_high} HIGH, {n_med} MEDIUM, {n_ext} EXTERNAL")

    # Detect tables outside any cluster (parser sanity)
    assigned = {t for _, _, ts, _ in CLUSTERS for t in ts}
    unassigned = [t for t in schema["tables"] if t not in assigned]
    if unassigned:
        print(f"WARNING: unassigned tables not in any cluster: {unassigned}", file=sys.stderr)

    # Companion markdown (diagrams are generated by build_schema_diagram_d2.py)
    md_path = DB_DIR / "ji_schema_companion.md"
    md_path.write_text(build_companion_md(schema, fks))
    print(f"wrote {md_path.name}")

    print("\nDone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
