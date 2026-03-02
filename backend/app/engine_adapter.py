from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from engine import ChartService
from engine.data.models.chart_data import ChartData
from engine.domain.interfaces.ichart_repository import IChartRepository
from engine.presentation.mappers.view_model_mapper import ViewModelMapper

from backend.app.ir_models import (
    AddRound,
    AddRow,
    CastOnAdditional,
    CastOnStart,
    ChartProgram,
    JoinCharts,
    KnittingCommand,
    PlaceMarker,
    PlaceOnHold,
    PlaceOnNeedle,
    RepeatRounds,
    RepeatRows,
)
from backend.app.preview_models import ChartPreview, MarkersBySide, PreviewError, RowMeta


class InMemoryChartRepository(IChartRepository):
    """Repository that avoids filesystem I/O (preview-only)."""

    def __init__(self) -> None:
        self._charts: Dict[str, ChartData] = {}

    def save_chart(self, chart_data: ChartData) -> None:
        self._charts[chart_data.name] = chart_data

    def load_chart(self, name: str) -> ChartData:
        return self._charts[name]

    def load_all_charts(self) -> List[ChartData]:
        return list(self._charts.values())

    def save_charts(self, charts: List[ChartData]) -> None:
        for c in charts:
            self.save_chart(c)


@dataclass(frozen=True)
class ExecutionContext:
    service: ChartService


def _markers_for(chart) -> MarkersBySide:
    # ChartSection.get_markers delegates to ChartQueries/MarkerManager.
    return MarkersBySide(RS=chart.get_markers("RS"), WS=chart.get_markers("WS"))


def execute_chart_program(program: ChartProgram, all_programs: Dict[str, ChartProgram]) -> ChartPreview:
    """
    Execute a single chart program and produce a preview payload.

    If an error occurs, execution for that chart stops at the failing command.
    """
    repo = InMemoryChartRepository()
    service = ChartService(chart_repository=repo)

    chart = service.create_chart(
        name=program.name,
        start_side=program.start_side,
        sts=program.sts,
        rows=program.rows,
    )

    errors: list[PreviewError] = []
    row_meta: list[RowMeta] = []

    # Simple "last hold slot" for MVP. Later we can support named hold buffers.
    last_hold: Optional[list] = None

    # For join, we need charts by name. MVP: create/join only if referenced charts exist in IR.
    # We execute joins by constructing the other chart up to its full program first if needed.
    created_charts: Dict[str, object] = {program.name: chart}

    def ensure_chart_built(chart_name: str) -> object:
        if chart_name in created_charts:
            return created_charts[chart_name]
        other_program = all_programs.get(chart_name)
        if other_program is None:
            raise ValueError(f"Unknown chart referenced: '{chart_name}'")
        other_preview = execute_chart_program(other_program, all_programs)
        # Rebuild chart for joining (preview execution already made one, but not returned).
        # For MVP: re-execute to get the ChartSection instance.
        other_chart = service.create_chart(
            name=other_program.name,
            start_side=other_program.start_side,
            sts=other_program.sts,
            rows=other_program.rows,
        )
        for idx, cmd in enumerate(other_program.commands):
            _execute_command(
                other_chart,
                cmd,
                idx,
                row_meta_out=None,
                errors_out=None,
                hold_slot=None,
                ensure_chart_built_fn=None,
                created_charts=None,
            )
        created_charts[chart_name] = other_chart
        return other_chart

    def _execute_command(
        chart_obj,
        cmd: KnittingCommand,
        cmd_index: int,
        row_meta_out: Optional[list[RowMeta]],
        errors_out: Optional[list[PreviewError]],
        hold_slot: Optional[dict],
        ensure_chart_built_fn,
        created_charts,
    ) -> None:
        # This helper is used by ensure_chart_built for MVP join support.
        # It intentionally omits row_meta/errors/hold behavior unless provided.
        if isinstance(cmd, CastOnStart):
            chart_obj.cast_on_start(cmd.count)
            return
        if isinstance(cmd, CastOnAdditional):
            chart_obj.cast_on(cmd.count)
            return
        if isinstance(cmd, PlaceMarker):
            chart_obj.place_marker(cmd.side, cmd.position)
            return
        if isinstance(cmd, PlaceOnHold):
            res = chart_obj.place_on_hold()
            if hold_slot is not None:
                hold_slot["last_hold"] = res
            return
        if isinstance(cmd, PlaceOnNeedle):
            if hold_slot is None or hold_slot.get("last_hold") is None:
                raise ValueError("place_on_needle requires a previous place_on_hold (MVP uses a single hold slot).")
            chart_obj.place_on_needle(hold_slot["last_hold"], cmd.join_side)
            return
        if isinstance(cmd, JoinCharts):
            if ensure_chart_built_fn is None:
                raise ValueError("join not available in this execution context")
            left = ensure_chart_built_fn(cmd.left_chart_name)
            right = ensure_chart_built_fn(cmd.right_chart_name)
            left.join(right)
            return

        # Row/round operations with meta capture when enabled.
        def record_row(is_round: bool, fn, pattern: str) -> None:
            before = chart_obj.get_current_num_of_stitches()
            fn(pattern)
            after = chart_obj.get_current_num_of_stitches()
            if row_meta_out is not None:
                row_meta_out.append(
                    RowMeta(
                        rowIndex=len(row_meta_out),
                        side=chart_obj.row_manager.get_last_row_side(),
                        isRound=is_round,
                        stitchCountBefore=before,
                        stitchCountAfter=after,
                    )
                )

        if isinstance(cmd, AddRow):
            record_row(False, chart_obj.add_row, cmd.pattern)
            return
        if isinstance(cmd, AddRound):
            record_row(True, chart_obj.add_round, cmd.pattern)
            return
        if isinstance(cmd, RepeatRows):
            for _ in range(cmd.times):
                for pat in cmd.patterns:
                    record_row(False, chart_obj.add_row, pat)
            return
        if isinstance(cmd, RepeatRounds):
            for _ in range(cmd.times):
                for pat in cmd.patterns:
                    record_row(True, chart_obj.add_round, pat)
            return

        raise ValueError(f"Unsupported command op: {cmd.op}")

    hold_slot = {"last_hold": None}

    for cmd_index, cmd in enumerate(program.commands):
        try:
            _execute_command(
                chart,
                cmd,
                cmd_index,
                row_meta_out=row_meta,
                errors_out=errors,
                hold_slot=hold_slot,
                ensure_chart_built_fn=ensure_chart_built,
                created_charts=created_charts,
            )
        except Exception as e:
            errors.append(PreviewError(commandIndex=cmd_index, message=str(e)))
            break

    last_row_side = chart.row_manager.get_last_row_side() if row_meta else None

    # Build view model for node-link visualization.
    serializer = service.serializer
    mapper = ViewModelMapper()
    chart_data: ChartData = service.export_chart(chart)
    chart_vm = mapper.to_view_model(chart_data)

    nodes_view = [
        {
            "id": n.id,
            "type": n.type,
            "x": n.x,
            "y": n.y,
            "row": n.row,
        }
        for n in chart_vm.nodes
    ]
    links_view = [
        {
            "source": l.source_id,
            "target": l.target_id,
        }
        for l in chart_vm.links
    ]

    return ChartPreview(
        chartName=program.name,
        rows=chart.rows,
        rowMeta=row_meta,
        markers=_markers_for(chart),
        errors=errors,
        currentStitchCount=chart.get_current_num_of_stitches(),
        lastRowSide=last_row_side,
        nodes=nodes_view,
        links=links_view,
    )

