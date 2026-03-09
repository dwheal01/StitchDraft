from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.app.engine_adapter import execute_chart_program
from backend.app.ir_models import KnittingIR
from backend.app.preview_models import PreviewResponse
from backend.app.join_graph import validate_join_graph
from backend.app.torso_generator import CYC_MEASUREMENTS, generate_torso_svg_custom, generate_torso_svg_from_size
from backend.app.torso_models import TorsoSvgRequest, TorsoSvgResponse

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
    # Validate join dependency graph (detect cycles) before executing.
    order, cycle = validate_join_graph(programs_by_name)
    if cycle is not None:
        cycle_str = " -> ".join(cycle)
        raise HTTPException(status_code=400, detail=f"Join cycle detected: {cycle_str}")

    # Execute charts in dependency order so any chart referenced in a join
    # is built before the chart that joins it.
    programs_by_order = [programs_by_name[name] for name in order if name in programs_by_name]
    previews_by_name = {p.chartName: p for p in (execute_chart_program(p, programs_by_name) for p in programs_by_order)}
    # Return previews in original IR order for consistent UI.
    previews = [previews_by_name[p.name] for p in ir.charts if p.name in previews_by_name]
    return PreviewResponse(charts=previews)


@app.get("/torso/sizes")
def torso_sizes() -> dict:
    return {"sizes": CYC_MEASUREMENTS}


@app.post("/torso/svg", response_model=TorsoSvgResponse)
def torso_svg(req: TorsoSvgRequest) -> TorsoSvgResponse:
    if req.mode == "size":
        if not req.size:
            raise HTTPException(status_code=400, detail="size is required when mode='size'")
        svg, view_box, width, height = generate_torso_svg_from_size(req.size)
        return TorsoSvgResponse(svg=svg, viewBox=view_box, width=width, height=height)

    if req.mode == "custom":
        if req.measurements is None:
            raise HTTPException(status_code=400, detail="measurements is required when mode='custom'")
        m = req.measurements
        svg, view_box, width, height = generate_torso_svg_custom(
            shoulder_width=m.shoulder_width,
            back_length=m.back_length,
            bust_circ=m.bust_circ,
            waist_circ=m.waist_circ,
            hip_circ=m.hip_circ,
            armhole_depth=m.armhole_depth,
            upper_arm_circ=m.upper_arm_circ,
            arm_length=m.arm_length,
            apex_depth=m.apex_depth,
            waist_to_hip=m.waist_to_hip,
            top_padding=m.top_padding,
            ease=m.ease,
        )
        return TorsoSvgResponse(svg=svg, viewBox=view_box, width=width, height=height)

    raise HTTPException(status_code=400, detail=f"Unsupported mode: {req.mode}")

