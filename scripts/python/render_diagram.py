#!/usr/bin/env python3
"""
Render a Graphviz DOT source file to a raster image (PNG by default).

Generic and reusable: takes any .dot source path and produces a PNG (or other
Graphviz-supported format) at the requested output path. Uses the system
`dot` binary via subprocess — no third-party Python dependencies required.

Usage (direct):
    python3 scripts/python/render_diagram.py <input.dot> [output.png] [--dpi N] [--format png]

Usage (via shell wrapper):
    scripts/render_diagram.sh <input.dot> [output.png] [--dpi N] [--format png]

Exit codes:
    0  rendered successfully
    1  input file missing or `dot` binary unavailable
    2  dot rendering failed
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def render(dot_path: Path, out_path: Path, fmt: str = "png", dpi: int = 144) -> int:
    if not dot_path.is_file():
        print(f"error: input not found: {dot_path}", file=sys.stderr)
        return 1

    dot_bin = shutil.which("dot")
    if dot_bin is None:
        print(
            "error: `dot` (Graphviz) not found on PATH. Install via `brew install graphviz` "
            "(macOS) or `apt-get install graphviz` (Debian/Ubuntu).",
            file=sys.stderr,
        )
        return 1

    out_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [dot_bin, f"-T{fmt}", f"-Gdpi={dpi}", str(dot_path), "-o", str(out_path)]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"error: dot exited {result.returncode}", file=sys.stderr)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return 2

    print(f"rendered: {out_path}")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render a Graphviz DOT source to a raster image."
    )
    parser.add_argument("input", type=Path, help="Path to the .dot source file")
    parser.add_argument(
        "output",
        type=Path,
        nargs="?",
        default=None,
        help="Output image path (defaults to input with the format extension)",
    )
    parser.add_argument(
        "--format",
        default="png",
        help="Output format passed to dot -T (default: png)",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=144,
        help="Raster DPI for png/jpg output (default: 144)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    out = args.output or args.input.with_suffix(f".{args.format}")
    return render(args.input.resolve(), out.resolve(), fmt=args.format, dpi=args.dpi)


if __name__ == "__main__":
    sys.exit(main())
