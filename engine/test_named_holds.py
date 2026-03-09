"""Tests for named hold slots: place on hold with name, place on needle from hold by name."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.domain.factories.chart_section_factory import ChartSectionFactory


def test_named_hold_slots_separate():
    """Place on hold 'left' and 'right' store unconsumed in separate slots."""
    factory = ChartSectionFactory()
    chart = factory.create_with_defaults(name="named_holds", start_side="RS")
    chart.cast_on_start(10)
    chart.place_marker("RS", 3)
    # Row that works only first 3 stitches: unconsumed = remaining 7
    chart.add_row("repeat(k1), sm")
    chart.place_on_hold("left")
    assert len(chart.get_stitches_on_hold("left")) == 7
    assert chart.get_current_num_of_stitches() == 3
    # Row that works nothing (empty): unconsumed = all 3
    chart.add_row("")
    chart.place_on_hold("right")
    assert len(chart.get_stitches_on_hold("right")) == 3
    assert chart.get_current_num_of_stitches() == 0
    # "left" slot unchanged
    assert len(chart.get_stitches_on_hold("left")) == 7


def test_place_on_needle_from_hold_by_name():
    """Place on needle from hold 'left' places back only that slot and clears it."""
    factory = ChartSectionFactory()
    chart = factory.create_with_defaults(name="needle_by_name", start_side="RS")
    chart.cast_on_start(10)
    chart.place_marker("RS", 3)
    chart.add_row("repeat(k1), sm")
    chart.place_on_hold("left")
    chart.add_row("")
    chart.place_on_hold("right")
    assert chart.get_current_num_of_stitches() == 0
    chart.place_on_needle_from_hold("left", "WS")
    assert chart.get_current_num_of_stitches() == 7
    assert len(chart.get_stitches_on_hold("left")) == 0
    assert len(chart.get_stitches_on_hold("right")) == 3
    chart.place_on_needle_from_hold("right", "RS")
    assert chart.get_current_num_of_stitches() == 10
    assert len(chart.get_stitches_on_hold("right")) == 0


def test_bind_off_hold_work_right_hold_place_left_count_two():
    """Place left (2) on hold, work right (3) two rows, place right on hold (unconsumed empty -> whole needle), place left from hold -> needle is 2 (not 5)."""
    factory = ChartSectionFactory()
    chart = factory.create_with_defaults(name="bo_hold_reconnect", start_side="RS")
    chart.cast_on_start(5)
    chart.place_marker("RS", 3)  # segment lengths 3, 2
    chart.add_row("repeat(k1), sm")  # work 3, unconsumed = 2
    chart.place_on_hold("left")  # 2 sts on hold "left", needle has 3
    chart.add_row("repeat(k1)")  # work 3; unconsumed is empty
    chart.add_row("repeat(k1)")  # unconsumed still empty
    chart.place_on_hold("right")  # whole needle (3) goes on hold; needle now 0
    assert chart.get_current_num_of_stitches() == 0
    chart.place_on_needle_from_hold("left", "WS")
    assert chart.get_current_num_of_stitches() == 2, "needle should be 2 (left only), not 5"
    chart.add_row("repeat(k1)")
    assert chart.get_current_num_of_stitches() == 2
    rows = chart.row_manager.get_rows()
    assert len(rows[-1]) == 2


def test_place_on_needle_from_hold_cast_on_between():
    """Place left (2) from hold, then place right (3) from hold with cast_on_between=4 -> needle has 9 sts (2 + 4 co + 3)."""
    factory = ChartSectionFactory()
    chart = factory.create_with_defaults(name="cast_on_between", start_side="RS")
    chart.cast_on_start(5)
    chart.place_marker("RS", 3)  # segments: 3 left, 2 right -> work 3, unconsumed 2
    chart.add_row("repeat(k1), sm")  # work 3, unconsumed 2
    chart.place_on_hold("left")  # 2 on "left", needle has 3
    chart.add_row("repeat(k1)")
    chart.add_row("repeat(k1)")
    chart.place_on_hold("right")  # 3 on "right", needle 0
    chart.place_on_needle_from_hold("left", "WS")
    assert chart.get_current_num_of_stitches() == 2
    chart.place_on_needle_from_hold("right", "RS", cast_on_between=4)
    assert chart.get_current_num_of_stitches() == 9, "expected 2 + 4 + 3 = 9"
    last_row = chart.node_manager.get_last_row_stitches()
    types = [s.type for s in last_row]
    assert len(types) == 9
    assert types[2:6] == ["co", "co", "co", "co"], f"middle 4 should be co, got {types}"


def test_place_on_needle_from_hold_missing_raises():
    """Place on needle from a hold name with no stitches raises."""
    factory = ChartSectionFactory()
    chart = factory.create_with_defaults(name="missing_hold", start_side="RS")
    chart.cast_on_start(5)
    chart.add_row("repeat(k1)")
    try:
        chart.place_on_needle_from_hold("nonexistent", "RS")
        assert False, "Expected ValueError"
    except ValueError as e:
        assert "no stitches" in str(e).lower() or "nonexistent" in str(e).lower()


def test_default_name_last_backward_compat():
    """place_on_hold() and place_on_needle(stitches, side) work with default 'last' slot."""
    factory = ChartSectionFactory()
    chart = factory.create_with_defaults(name="default_last", start_side="RS")
    chart.cast_on_start(10)
    chart.add_row("repeat(k1)")
    chart.add_row("")
    chart.place_on_hold()  # default name "last"
    assert len(chart.get_stitches_on_hold()) == 10
    assert chart.get_current_num_of_stitches() == 0
    stitches = chart.get_stitches_on_hold()
    chart.place_on_needle(stitches, "WS")
    assert chart.get_current_num_of_stitches() == 10


def run_all():
    test_named_hold_slots_separate()
    test_place_on_needle_from_hold_by_name()
    test_bind_off_hold_work_right_hold_place_left_count_two()
    test_place_on_needle_from_hold_cast_on_between()
    test_place_on_needle_from_hold_missing_raises()
    test_default_name_last_backward_compat()
    print("All named holds tests passed.")


if __name__ == "__main__":
    run_all()
