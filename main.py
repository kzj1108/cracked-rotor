#!/usr/bin/env python3
"""一键出齐全部文献图 — 与 MATLAB RUN_ALL 对应。"""
import argparse
import os
import sys
from pathlib import Path

from cracked_rotor.reproduce import reproduce_all_figures


def main():
    ap = argparse.ArgumentParser(description="Cracked rotor — one-click all figures")
    ap.add_argument(
        "--out",
        default=os.environ.get("OUTPUT_DIR", "output"),
        help="Output directory",
    )
    ap.add_argument(
        "--quick",
        action="store_true",
        help="Coarser grid (faster, for CI)",
    )
    args = ap.parse_args()
    out = Path(args.out)
    if out.exists():
        cache = out / "sweep_cache_hb.mat"
        if cache.exists():
            try:
                cache.unlink()
                print("Removed stale cache (if any)")
            except OSError:
                pass
    print("=" * 60)
    print("  Cracked rotor — RUN_ALL (Python)")
    print(f"  Output: {out.resolve()}")
    print(f"  quick={args.quick}")
    print("=" * 60)
    try:
        reproduce_all_figures(out, quick=args.quick)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    print("=" * 60)
    print("  Done. PNG files:")
    for p in sorted(out.glob("*.png")):
        print(f"    {p.name}")
    print("=" * 60)


if __name__ == "__main__":
    main()
