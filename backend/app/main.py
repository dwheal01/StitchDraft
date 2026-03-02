from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.engine_adapter import execute_chart_program
from backend.app.ir_models import KnittingIR
from backend.app.preview_models import PreviewResponse

app = FastAPI(title="Knitting Pattern Builder API", version="0.1.0")

# MVP-friendly CORS: allow local dev frontends.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
def healthz() -> dict:
    return {"ok": True}


@app.post("/preview", response_model=PreviewResponse)
def preview(ir: KnittingIR) -> PreviewResponse:
    programs_by_name = {c.name: c for c in ir.charts}
    previews = [execute_chart_program(program, programs_by_name) for program in ir.charts]
    return PreviewResponse(charts=previews)

