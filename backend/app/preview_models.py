from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


StartSide = Literal["RS", "WS"]


class PreviewError(BaseModel):
    commandIndex: int = Field(ge=0)
    message: str


class RowMeta(BaseModel):
    rowIndex: int = Field(ge=0)
    side: StartSide
    isRound: bool
    stitchCountBefore: int = Field(ge=0)
    stitchCountAfter: int = Field(ge=0)


class MarkersBySide(BaseModel):
    RS: list[int] = Field(default_factory=list)
    WS: list[int] = Field(default_factory=list)


class NodeView(BaseModel):
    id: str
    type: str
    x: float
    y: float
    row: int


class LinkView(BaseModel):
    source: str
    target: str


class ChartPreview(BaseModel):
    chartName: str
    rows: list[list[str]] = Field(default_factory=list)
    rowMeta: list[RowMeta] = Field(default_factory=list)
    markers: MarkersBySide = Field(default_factory=MarkersBySide)
    errors: list[PreviewError] = Field(default_factory=list)
    currentStitchCount: int = Field(ge=0)
    lastRowSide: Optional[StartSide] = None
    nodes: list[NodeView] = Field(default_factory=list)
    links: list[LinkView] = Field(default_factory=list)


class PreviewResponse(BaseModel):
    charts: list[ChartPreview] = Field(default_factory=list)

