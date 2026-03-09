from __future__ import annotations

from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field


StartSide = Literal["RS", "WS"]


class CastOnStart(BaseModel):
    op: Literal["cast_on_start"]
    count: int = Field(ge=0)


class CastOnAdditional(BaseModel):
    op: Literal["cast_on_additional"]
    count: int = Field(ge=0)


class AddRow(BaseModel):
    op: Literal["add_row"]
    pattern: str


class AddRound(BaseModel):
    op: Literal["add_round"]
    pattern: str


class RepeatRows(BaseModel):
    op: Literal["repeat_rows"]
    times: int = Field(ge=0)
    patterns: list[str]


class RepeatRounds(BaseModel):
    op: Literal["repeat_rounds"]
    times: int = Field(ge=0)
    patterns: list[str]


class PlaceMarker(BaseModel):
    op: Literal["place_marker"]
    side: StartSide
    position: int = Field(ge=0)


class PlaceOnHold(BaseModel):
    op: Literal["place_on_hold"]
    name: str = "last"


class PlaceOnNeedle(BaseModel):
    op: Literal["place_on_needle"]
    join_side: StartSide
    from_hold: str = "last"
    source: str = "last"  # backward compat; prefer from_hold when both present
    cast_on_between: int = 0  # optional: insert N cast-on stitches between needle and hold


class JoinCharts(BaseModel):
    op: Literal["join"]
    left_chart_name: str
    right_chart_name: str


KnittingCommand = Annotated[
    Union[
        CastOnStart,
        CastOnAdditional,
        AddRow,
        AddRound,
        RepeatRows,
        RepeatRounds,
        PlaceMarker,
        PlaceOnHold,
        PlaceOnNeedle,
        JoinCharts,
    ],
    Field(discriminator="op"),
]


class ChartProgram(BaseModel):
    name: str
    start_side: StartSide
    sts: int = Field(ge=1)
    rows: int = Field(ge=1)
    commands: list[KnittingCommand] = Field(default_factory=list)


class KnittingIR(BaseModel):
    version: str
    charts: list[ChartProgram] = Field(default_factory=list)

