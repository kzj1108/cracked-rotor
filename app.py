"""FastAPI app for Render — trigger figure generation via HTTP."""
import os
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, JSONResponse

from cracked_rotor.reproduce import reproduce_all_figures

app = FastAPI(title="Cracked Rotor HB Figures")
OUT = Path(os.environ.get("OUTPUT_DIR", "output"))


@app.get("/")
def health():
    return {
        "status": "ok",
        "matlab_source": "cracked_rotor_matlab (unchanged)",
        "docs": "/docs",
        "generate_quick": "/generate?quick=true",
        "generate_full": "/generate?quick=false",
        "figures": "/figures/{filename}.png",
    }


@app.api_route("/generate", methods=["GET", "POST"])
def generate(quick: bool = Query(True, description="Coarse grid (true) or paper grid (false)")):
    """Browser: open /generate?quick=true — no Postman or cmd needed."""
    out = reproduce_all_figures(OUT, quick=quick)
    files = sorted(p.name for p in out.glob("*.png"))
    return JSONResponse(
        {
            "output_dir": str(out),
            "quick": quick,
            "files": files,
            "download_examples": [f"/figures/{n}" for n in files[:3]],
        }
    )


@app.get("/figures/{name}")
def get_figure(name: str):
    path = OUT / name
    if not path.is_file():
        return JSONResponse({"error": "not found"}, status_code=404)
    return FileResponse(path)
