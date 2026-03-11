"""Tests for WS start chart expansion and layout (reverse pattern, treat like RS)."""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from engine.domain.services.chart_service import ChartService
from engine.data.repositories.chart_repository import ChartRepository
from engine.presentation.services.chart_visualization_service import ChartVisualizationService


def test_ws_k1_inc_repeat_k1_expands_correctly():
    """
    For WS, 'k1, inc, repeat(k1)' should expand to 9k, inc, k1 (inc second from right).
    reverse_row_if_needed does this; chart_generator must not reverse the row again.
    """
    repo = ChartRepository(data_path="engine")
    service = ChartService(chart_repository=repo)
    chart = service.create_chart(name="ws_expand_test", start_side="WS", sts=22, rows=28)
    chart.cast_on_start(10)
    chart.repeat_rounds(["k1, inc, repeat(k1)"], 2)

    # Row 2: expect 11 stitches (9 k, inc, 1 k) -> displayed as p,...,inc,p
    row2_nodes = [n for n in chart.nodes if n.row == 2 and n.type != "strand"]
    types = [n.type for n in row2_nodes]
    assert len(types) == 11, f"Expected 11 stitches in row 2, got {len(types)}: {types}"
    inc_idx = next(i for i, t in enumerate(types) if t == "inc")
    assert inc_idx == 9, f"Expected inc at index 9 (second from right), got {inc_idx}"


if __name__ == "__main__":
    from engine.test_view_models import test_view_model_mapper

    try:
        test_view_model_mapper()
        test_ws_k1_inc_repeat_k1_expands_correctly()
        print("\n✓ WS layout tests passed!")
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()

