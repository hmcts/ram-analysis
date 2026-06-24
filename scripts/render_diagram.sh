#!/usr/bin/env bash
#
# render_diagram.sh — wrapper that activates the project venv and invokes
# scripts/python/render_diagram.py with all forwarded args.
#
# Resolves paths relative to the script location so it can be run from
# anywhere (no dependency on the current working directory).
#
# Usage:
#   scripts/render_diagram.sh <input.dot> [output.png] [--dpi N] [--format png]
#   scripts/render_diagram.sh <input.d2>  [output.png]
#
# .d2 inputs render via D2 with the ELK layout engine (`brew install d2`) —
# the house standard for new boxes-and-lines architecture diagrams.
# .dot inputs render via Graphviz — retained for record/table-style renders
# (the as-is database schema diagrams).
#
# Honours the project rule "always use a virtual environment for Python
# commands" — the venv is created lazily on first run. The render script
# itself uses only the standard library, so no pip installs are required.

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." >/dev/null 2>&1 && pwd)"
VENV_DIR="$REPO_ROOT/.venv"
RENDER_PY="$SCRIPT_DIR/python/render_diagram.py"

if [[ ! -f "$RENDER_PY" ]]; then
  echo "error: render script not found at $RENDER_PY" >&2
  exit 1
fi

# D2 sources short-circuit to the d2 CLI (no venv needed)
if [[ "${1:-}" == *.d2 ]]; then
  if ! command -v d2 >/dev/null 2>&1; then
    echo "error: d2 not found on PATH — install with: brew install d2" >&2
    exit 1
  fi
  IN="$1"
  OUT="${2:-${IN%.d2}.png}"
  exec d2 --pad 24 "$IN" "$OUT"
fi

if [[ ! -d "$VENV_DIR" ]]; then
  echo "creating venv at $VENV_DIR ..."
  python3 -m venv "$VENV_DIR"
fi

# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

exec python "$RENDER_PY" "$@"
