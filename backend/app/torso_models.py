from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


TorsoMode = Literal["size", "custom"]
TorsoSize = Literal["XS", "S", "M", "L", "XL", "2XL", "3XL", "4XL", "5XL"]


class MeasurementSet(BaseModel):
    # Core fields (inches)
    shoulder_width: float = Field(gt=0)
    back_length: float = Field(gt=0)
    bust_circ: float = Field(gt=0)
    waist_circ: float = Field(gt=0)
    hip_circ: float = Field(gt=0)
    armhole_depth: float = Field(gt=0)
    upper_arm_circ: float = Field(gt=0)
    arm_length: float = Field(gt=0)

    # Optional tuning fields (inches)
    apex_depth: Optional[float] = Field(default=None, gt=0)
    waist_to_hip: float = Field(default=8, gt=0)
    top_padding: float = Field(default=2, ge=0)
    ease: float = Field(default=0.0)


class TorsoSvgRequest(BaseModel):
    mode: TorsoMode
    size: Optional[TorsoSize] = None
    measurements: Optional[MeasurementSet] = None


class TorsoSvgResponse(BaseModel):
    svg: str
    viewBox: str
    width: float
    height: float

