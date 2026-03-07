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
    assert "place_on_hold" in preview.errors[0].message.lower()


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
    test_unknown_chart_in_join_fails()
    print("✓ test_unknown_chart_in_join_fails")
    print("\nAll engine_adapter tests passed.")


if __name__ == "__main__":
    test_place_on_hold_and_place_on_needle()
    print("✓ test_place_on_hold_and_place_on_needle passed")
    test_place_on_needle_without_hold_fails()
    print("✓ test_place_on_needle_without_hold_fails passed")
    test_join_charts()
    print("✓ test_join_charts passed")
    test_unknown_chart_in_join_fails()
    print("✓ test_unknown_chart_in_join_fails passed")
    print("\n✓ All engine_adapter tests passed!")
