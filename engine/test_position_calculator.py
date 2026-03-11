"""Tests and debug helpers for PositionCalculator anchor calculations."""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from engine.domain.models.position_calculator import PositionCalculator
from engine.data.models.node import Node


class _DummyLinkManager:
    """Minimal stub for link manager used by PositionCalculator in tests."""

    def add_vertical_link(self, *args, **kwargs):
        pass

    def add_horizontal_link(self, *args, **kwargs):
        pass


def _make_previous_row(pc: PositionCalculator, count: int = 10) -> list[Node]:
    """Create a synthetic previous row of `count` stitches using centered_array spacing."""
    xs = pc.centered_array(count)
    return [
        Node(id=str(i), type="k", row=1, fx=x, fy=0.0)
        for i, x in enumerate(xs)
    ]


def test_rs_increase_symmetry_k1_inc_k8_inc_k1():
    """Debug: print and check symmetry for RS row 'k1, inc, k8, inc, k1' after CO 10."""
    print("\n=== RS symmetry test: k1, inc, k8, inc, k1 over CO 10 ===")

    pc = PositionCalculator()
    # Set a non-zero gauge so centered_array produces meaningful spacing.
    pc.set_guage(sts=20, rows=20)
    previous_stitches = _make_previous_row(pc, 10)
    row = ["k", "inc"] + ["k"] * 8 + ["inc", "k"]  # 12 stitches total

    anchors, _ = pc.calculate_anchors(
        row=row,
        side="RS",
        previous_stitches=previous_stitches,
        link_manager=_DummyLinkManager(),
        node_counter=0,
    )

    print("Previous row x positions:")
    print([round(n.fx, 4) for n in previous_stitches])
    print("Current row anchors:")
    print([round(a, 4) for a in anchors])

    # Basic symmetry checks: center near zero and mirrored positions
    center = sum(anchors) / len(anchors)
    assert abs(center) < 1e-6, f"Row should be centered, got center={center}"

    for left, right in zip(anchors, reversed(anchors)):
        diff = abs(left + right)
        assert diff < 1e-6, f"Anchors should be mirrored: {left} vs {right} (diff={diff})"

    print("✓ Anchors are numerically centered and mirrored.")


if __name__ == "__main__":
    # Allow quick manual debugging: run this file directly.
    test_rs_increase_symmetry_k1_inc_k8_inc_k1()

