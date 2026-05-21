"""One-click figures — literature style by default."""
from __future__ import annotations
from pathlib import Path

from .literature_plots import plot_all_literature


def reproduce_all_figures(out_dir: str | Path | None = None, quick: bool = False) -> Path:
    out = Path(out_dir or Path(__file__).resolve().parents[1] / "output")
    print(f"Output: {out}  quick={quick}  (literature style)")
    plot_all_literature(out, quick=quick)
    print("Done:", list(out.glob("*.png")))
    return out
