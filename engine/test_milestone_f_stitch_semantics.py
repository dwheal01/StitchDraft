"""Milestone F: Stitch semantics parity — cast-on additional, marker removal (rm), bind-off (bo).

Tests that the engine correctly supports:
- Additional cast-on after start (cast_on)
- Marker removal via pattern token "rm"
- Bind-off (bo, boN) reducing stitch count and appearing in rows
- Regression flows from main.py and flirt.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.domain.factories.chart_section_factory import ChartSectionFactory
from engine import ChartService
from engine.domain.interfaces.ichart_repository import IChartRepository
from engine.data.models.chart_data import ChartData


# --- Marker removal (rm): pattern-string only, no separate IR op ---


def test_marker_removal_rm_in_pattern():
    """Place a marker, then work a row that includes 'rm'; marker should be removed."""
    factory = ChartSectionFactory()
    chart = factory.create_with_defaults(name="rm_test", start_side="RS")
    chart.cast_on_start(10)
    chart.place_marker("RS", 3)
    assert 3 in chart.get_markers("RS"), "Marker should be placed at 3"
    chart.add_row("k3, rm, repeat(k1)")  # 3 knit, remove marker, knit to end (7 sts)
    assert 3 not in chart.get_markers("RS"), "Marker at 3 should be removed after rm"
    assert chart.get_current_num_of_stitches() == 10, "Stitch count unchanged by rm"


def test_marker_removal_round():
    """Round with rm (e.g. raglan flow): place marker, add round with bo and rm."""
    factory = ChartSectionFactory()
    chart = factory.create_with_defaults(name="rm_round_test", start_side="RS")
    chart.cast_on_start(20)
    chart.place_marker("WS", 4)
    assert 4 in chart.get_markers("WS")
    chart.add_round("bo4, repeat(k1), rm")
    assert 4 not in chart.get_markers("WS"), "Marker should be removed by rm in round"
    assert chart.get_current_num_of_stitches() == 16, "bo4: 20 - 4 = 16"


# --- Bind-off (bo / boN) ---


def test_bind_off_reduces_stitch_count():
    """Bind-off consumes stitches; stitch count after row should decrease."""
    factory = ChartSectionFactory()
    chart = factory.create_with_defaults(name="bo_test", start_side="RS")
    chart.cast_on_start(10)
    chart.add_row("bo3, repeat(k1)")
    assert chart.get_current_num_of_stitches() == 7, "bo3: 10 - 3 = 7"


def test_bind_off_boN_syntax():
    """bo4, bo7, bo13 etc. should parse and reduce count correctly."""
    factory = ChartSectionFactory()
    chart = factory.create_with_defaults(name="boN_test", start_side="RS")
    chart.cast_on_start(20)
    chart.add_row("bo7, repeat(k1)")
    assert chart.get_current_num_of_stitches() == 13, "bo7: 20 - 7 = 13"


def test_bind_off_appears_in_rows():
    """Expanded row should contain 'bo' tokens for preview."""
    factory = ChartSectionFactory()
    chart = factory.create_with_defaults(name="bo_rows_test", start_side="RS")
    chart.cast_on_start(10)
    chart.add_row("bo2, k2, repeat(k1)")
    rows = chart.rows
    assert len(rows) >= 2, "Should have cast-on row and one worked row"
    last_row = rows[-1]
    assert "bo" in last_row, "Last row should contain 'bo' tokens"


# --- Cast-on additional ---


def test_cast_on_additional_after_row():
    """Cast on more stitches after first row; count should increase."""
    factory = ChartSectionFactory()
    chart = factory.create_with_defaults(name="co_add_test", start_side="RS")
    chart.cast_on_start(10)
    chart.add_row("repeat(k1)")
    assert chart.get_current_num_of_stitches() == 10
    chart.cast_on(2)
    assert chart.get_current_num_of_stitches() == 12, "cast_on(2): 10 + 2 = 12"


def test_cast_on_additional_after_round():
    """Cast on after add_round runs without error (sleeve flow uses this)."""
    factory = ChartSectionFactory()
    chart = factory.create_with_defaults(name="co_add_round_test", start_side="RS")
    chart.cast_on_start(60)
    chart.repeat_rounds(["repeat(k1, p1)"], 2)
    chart.add_round("repeat(k2, inc)")
    n_before = chart.get_current_num_of_stitches()
    chart.cast_on(1)
    n_after = chart.get_current_num_of_stitches()
    assert n_after >= n_before, "cast_on(1) should not decrease stitches"
    assert n_after == n_before + 1, "cast_on(1) should add exactly 1 stitch"


# --- Regression: demo flows (no errors, expected counts) ---


def test_regression_lobster_back_flow():
    """Reproduce engine/flirt.py lobster_back flow; must complete without error."""
    repo = _InMemoryRepo()
    service = ChartService(chart_repository=repo)
    back = service.create_chart(name="lobster_back", start_side="RS", sts=22, rows=44)
    back.cast_on_start(41)
    back.repeat_rows(["k2, inc, repeat(k1), inc, k2", "repeat(k1)"], 17)
    back.add_row("repeat(k1,p1)")
    back.repeat_rows(["work est"], 3)
    assert back.get_current_num_of_stitches() >= 41
    service.save_charts([back])


def test_regression_sleeve_flow():
    """Sleeve flow: cast_on_start, repeat_rounds, add_round(...).cast_on(1), bo7."""
    repo = _InMemoryRepo()
    service = ChartService(chart_repository=repo)
    sleeve = service.create_chart(name="sleeve", start_side="RS", sts=23, rows=21)
    sleeve.cast_on_start(60)
    sleeve.repeat_rounds(["repeat(k1, p1)"], 15)
    sleeve.add_round("repeat(k2, inc)").cast_on(1)
    sleeve.repeat_rounds(["repeat(k1)"], 2)
    sleeve.add_round("bo7, repeat(k1)")
    sleeve.repeat_rounds(["repeat(k1)"], 2)
    # After repeat(k2, inc) on 60 sts we gain stitches; +1 cast_on; -7 bo. Expect net reduction from bo7.
    final_count = sleeve.get_current_num_of_stitches()
    assert final_count >= 70 and final_count <= 95, f"Expected sleeve count in range, got {final_count}"
    service.save_charts([sleeve])


def test_regression_raglan_back_flow():
    """Raglan back: cast_on_start, repeat_rounds, place_marker, add_round with bo4 and rm."""
    repo = _InMemoryRepo()
    service = ChartService(chart_repository=repo)
    rb = service.create_chart(name="raglan_back", start_side="RS", sts=23, rows=21)
    rb.cast_on_start(122)
    rb.repeat_rounds(["repeat(k1, p1)"], 15)
    rb.repeat_rounds(["repeat(k1)"], 30)
    rb.place_marker("WS", 4)
    rb.add_round("bo4, repeat(k1), rm").place_on_hold()
    rb.add_round("repeat(k1)")
    assert 4 not in rb.get_markers("WS"), "rm should remove marker"
    service.save_charts([rb])


class _InMemoryRepo(IChartRepository):
    def __init__(self):
        self._charts = {}

    def save_chart(self, chart_data: ChartData):
        self._charts[chart_data.name] = chart_data

    def load_chart(self, name: str) -> ChartData:
        return self._charts[name]

    def load_all_charts(self):
        return list(self._charts.values())

    def save_charts(self, charts: list):
        for c in charts:
            self.save_chart(c)


def run_all():
    test_marker_removal_rm_in_pattern()
    test_marker_removal_round()
    test_bind_off_reduces_stitch_count()
    test_bind_off_boN_syntax()
    test_bind_off_appears_in_rows()
    test_cast_on_additional_after_row()
    test_cast_on_additional_after_round()
    test_regression_lobster_back_flow()
    test_regression_sleeve_flow()
    test_regression_raglan_back_flow()
    print("All Milestone F stitch semantics tests passed.")


if __name__ == "__main__":
    run_all()
