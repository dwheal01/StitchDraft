"""Tests for engine_adapter: holds, join, and preview execution."""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is in path
_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from backend.app.engine_adapter import execute_chart_program
from backend.app.ir_models import ChartProgram, KnittingIR


def test_place_on_hold_and_place_on_needle() -> None:
    """Place on hold and place on needle with single hold slot."""
    program = ChartProgram(
        name="hold_demo",
        start_side="RS",
        sts=22,
        rows=44,
        commands=[
            {"op": "cast_on_start", "count": 10},
            {"op": "add_row", "pattern": "repeat(k1)"},
            {"op": "add_row", "pattern": ""},  # Empty row - all stitches unconsumed
            {"op": "place_on_hold"},
            {"op": "add_row", "pattern": "repeat(k1)"},
            {"op": "place_on_needle", "join_side": "WS", "source": "last"},
            {"op": "add_row", "pattern": "repeat(k1)"},
        ],
    )
    ir = KnittingIR(version="0.1", charts=[program])
    programs_by_name = {c.name: c for c in ir.charts}
    preview = execute_chart_program(program, programs_by_name)

    assert preview.chartName == "hold_demo"
    assert len(preview.errors) == 0, f"Expected no errors, got: {preview.errors}"
    assert preview.currentStitchCount == 10
    assert len(preview.rows) > 0
    assert len(preview.nodes) > 0


def test_place_on_needle_without_hold_fails() -> None:
    """place_on_needle without prior place_on_hold should error."""
    program = ChartProgram(
        name="needle_no_hold",
        start_side="RS",
        sts=22,
        rows=44,
        commands=[
            {"op": "cast_on_start", "count": 10},
            {"op": "place_on_needle", "join_side": "RS", "source": "last"},
        ],
    )
    ir = KnittingIR(version="0.1", charts=[program])
    programs_by_name = {c.name: c for c in ir.charts}
    preview = execute_chart_program(program, programs_by_name)

    assert len(preview.errors) == 1
    msg = preview.errors[0].message.lower()
    assert "place_on_hold" in msg or "no stitches in hold" in msg


def test_join_charts() -> None:
    """Join two charts; left chart receives right chart's stitches."""
    join_demo = ChartProgram(
        name="join_demo",
        start_side="RS",
        sts=23,
        rows=21,
        commands=[
            {"op": "cast_on_start", "count": 10},
            {"op": "repeat_rows", "times": 3, "patterns": ["k1, inc, repeat(k1), inc, k1", "repeat(k1)"]},
            {"op": "join", "left_chart_name": "join_demo", "right_chart_name": "join_demo2"},
        ],
    )
    join_demo2 = ChartProgram(
        name="join_demo2",
        start_side="RS",
        sts=23,
        rows=21,
        commands=[
            {"op": "cast_on_start", "count": 10},
            {"op": "repeat_rows", "times": 3, "patterns": ["k1, inc, repeat(k1), inc, k1", "repeat(k1)"]},
        ],
    )
    ir = KnittingIR(version="0.1", charts=[join_demo, join_demo2])
    programs_by_name = {c.name: c for c in ir.charts}

    preview_left = execute_chart_program(join_demo, programs_by_name)
    assert preview_left.chartName == "join_demo"
    assert len(preview_left.errors) == 0, f"Expected no errors, got: {preview_left.errors}"
    # Joined chart should have more nodes than either alone
    assert len(preview_left.nodes) > 0
    assert preview_left.currentStitchCount > 10  # Both charts had 10+ after increases


def test_named_holds_via_ir() -> None:
    """Named holds: place on hold with name, place on needle from hold by name."""
    program = ChartProgram(
        name="named_holds_demo",
        start_side="RS",
        sts=22,
        rows=44,
        commands=[
            {"op": "cast_on_start", "count": 10},
            {"op": "add_row", "pattern": "repeat(k1)"},
            {"op": "place_marker", "side": "RS", "position": 3},
            {"op": "add_row", "pattern": "repeat(k1), sm"},
            {"op": "place_on_hold", "name": "left"},
            {"op": "add_row", "pattern": ""},
            {"op": "place_on_hold", "name": "right"},
            {"op": "place_on_needle", "from_hold": "left", "join_side": "WS"},
            {"op": "place_on_needle", "from_hold": "right", "join_side": "RS"},
        ],
    )
    ir = KnittingIR(version="0.1", charts=[program])
    programs_by_name = {c.name: c for c in ir.charts}
    preview = execute_chart_program(program, programs_by_name)
    assert preview.chartName == "named_holds_demo"
    assert len(preview.errors) == 0, f"Expected no errors, got: {preview.errors}"
    assert preview.currentStitchCount == 10


def test_preview_bind_off_and_cast_on_additional() -> None:
    """Bind-off (bo) and cast_on_additional: preview rows contain 'bo', rowMeta reflects stitch counts."""
    program = ChartProgram(
        name="bo_demo",
        start_side="RS",
        sts=22,
        rows=44,
        commands=[
            {"op": "cast_on_start", "count": 10},
            {"op": "add_round", "pattern": "repeat(k1)"},
            {"op": "cast_on_additional", "count": 2},
            {"op": "add_round", "pattern": "bo3, repeat(k1)"},
        ],
    )
    ir = KnittingIR(version="0.1", charts=[program])
    programs_by_name = {c.name: c for c in ir.charts}
    preview = execute_chart_program(program, programs_by_name)

    assert preview.chartName == "bo_demo"
    assert len(preview.errors) == 0, f"Expected no errors, got: {preview.errors}"
    assert preview.currentStitchCount == 9, "10 + 2 - 3 = 9"
    # At least one row should contain "bo" tokens (each row is list of stitch type strings)
    has_bo_row = any("bo" in row for row in preview.rows)
    assert has_bo_row, f"Preview rows should contain 'bo'; rows={preview.rows}"
    # rowMeta should have entry for the bo row with stitchCountAfter < stitchCountBefore
    assert len(preview.rowMeta) >= 2
    before_bo = next((m for m in preview.rowMeta if m.stitchCountAfter == 9), None)
    assert before_bo is not None, "rowMeta should reflect stitch count 9 after bo3"


def test_bind_off_row_markers_2_left_5_bo_3_right() -> None:
    """With cast on 10, repeat 2 rows, place marker RS 2, WS 3, add row with sm/bo/sm the last row is 2 k, 5 bo, 3 k."""
    program = ChartProgram(
        name="bo_markers",
        start_side="RS",
        sts=22,
        rows=28,
        commands=[
            {"op": "cast_on_start", "count": 10},
            {"op": "repeat_rows", "times": 2, "patterns": ["repeat(k1)"]},
            {"op": "place_marker", "side": "RS", "position": 2},
            {"op": "place_marker", "side": "WS", "position": 3},
            {"op": "add_row", "pattern": "repeat(k1), sm, repeat(bo), sm, repeat(k1)"},
        ],
    )
    ir = KnittingIR(version="0.1", charts=[program])
    programs_by_name = {c.name: c for c in ir.charts}
    preview = execute_chart_program(program, programs_by_name)

    assert preview.chartName == "bo_markers"
    assert len(preview.errors) == 0, f"Expected no errors, got: {preview.errors}"
    assert len(preview.rows) >= 4
    last_row = preview.rows[-1]
    expected = ["k", "k", "bo", "bo", "bo", "bo", "bo", "k", "k", "k"]
    assert last_row == expected, (
        f"Last row should be 2 k, 5 bo, 3 k (2 left, middle bound off, 3 right); got {last_row}"
    )
    assert preview.currentStitchCount == 5  # 2 + 3 live after 5 bo


def test_unknown_chart_in_join_fails() -> None:
    """Join referencing unknown chart should error."""
    program = ChartProgram(
        name="bad_join",
        start_side="RS",
        sts=22,
        rows=44,
        commands=[
            {"op": "cast_on_start", "count": 10},
            {"op": "join", "left_chart_name": "bad_join", "right_chart_name": "nonexistent"},
        ],
    )
    ir = KnittingIR(version="0.1", charts=[program])
    programs_by_name = {c.name: c for c in ir.charts}
    preview = execute_chart_program(program, programs_by_name)

    assert len(preview.errors) == 1
    assert "nonexistent" in preview.errors[0].message.lower() or "unknown" in preview.errors[0].message.lower()


if __name__ == "__main__":
    test_place_on_hold_and_place_on_needle()
    print("✓ test_place_on_hold_and_place_on_needle")
    test_place_on_needle_without_hold_fails()
    print("✓ test_place_on_needle_without_hold_fails")
    test_join_charts()
    print("✓ test_join_charts")
    test_named_holds_via_ir()
    print("✓ test_named_holds_via_ir")
    test_preview_bind_off_and_cast_on_additional()
    print("✓ test_preview_bind_off_and_cast_on_additional")
    test_bind_off_row_markers_2_left_5_bo_3_right()
    print("✓ test_bind_off_row_markers_2_left_5_bo_3_right")
    test_unknown_chart_in_join_fails()
    print("✓ test_unknown_chart_in_join_fails")
    print("\nAll engine_adapter tests passed.")
