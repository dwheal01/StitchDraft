import json
from typing import Optional, TYPE_CHECKING

# Use clean imports from the package
from engine import ChartService, ChartRepository
from engine.chart_section import ChartSection
from engine.presentation.services.chart_visualization_service import ChartVisualizationService

if TYPE_CHECKING:
    from engine.chart_section import ChartSection


def main():
    """Main entry point for the knitting pattern engine."""
    # Initialize service layer
    repository = ChartRepository(data_path="engine")
    chart_service = ChartService(chart_repository=repository)
    # visualization_service = ChartVisualizationService(chart_service)
    chart_sections = []
  
    # Replace ONLY the creation line - keep everything else the same
    sleeve = chart_service.create_chart(name="raglan", start_side="RS", sts=23, rows=21)
    # Attach observer right after creation
    # visualization_service.attach_visualization_observer(raglan)
    sleeve.cast_on_start(120)
    sleeve.add_round("k2, inc, repeat(p4, k4), inc, k2")
    sleeve.repeat_rounds(["k3, repeat(p4, k4), k3"], 3)
    sleeve.add_round("k2, inc, k1, repeat(p4, k4), inc, k2")
    sleeve.repeat_rounds(["k4, repeat(p4, k4), k4"], 3)
    sleeve.add_round("k2, inc, k2, repeat(p4, k4), inc, k2")
    sleeve.repeat_rounds(["k5, repeat(p4, k4), k5"], 3)
    sleeve.add_round("k2, inc, k3, repeat(p4, k4), inc, k2")
    sleeve.repeat_rounds(["k6, repeat(p4, k4), k6"], 3)
    
    sleeve.add_round("k2, inc, repeat(k4, p4), inc, k2")
    sleeve.repeat_rounds(["k2, p1, repeat(k4, p4), k2"], 3)
    sleeve.add_round("k2, inc, p1, repeat(k4, p4), inc, k2")
    sleeve.repeat_rounds(["k2, p2, repeat(k4, p4), k2"], 3)
    sleeve.add_round("k2, inc, p2, repeat(k4, p4), inc, k2")
    sleeve.repeat_rounds(["k2, p3, repeat(k4, p4), k2"], 3)
    sleeve.add_round("k2, inc, p3, repeat(k4, p4), inc, k2")
    sleeve.repeat_rounds(["k2, p4, repeat(k4, p4), k2"], 3)
    
    sleeve.add_round("k2, inc, repeat(p4, k4), inc, k2")
    sleeve.repeat_rounds(["k3, repeat(p4, k4), k3"], 3)
    sleeve.add_round("k2, inc, k1, repeat(p4, k4), inc, k2")
    sleeve.repeat_rounds(["k4, repeat(p4, k4), k4"], 3)
    sleeve.add_round("k2, inc, k2, repeat(p4, k4), inc, k2")
    sleeve.repeat_rounds(["k5, repeat(p4, k4), k5"], 3)
    sleeve.add_round("k2, inc, k3, repeat(p4, k4), inc, k2")
    sleeve.repeat_rounds(["k6, repeat(p4, k4), k6"], 3)
    
    sleeve.add_round("k2, inc, repeat(k4, p4), inc, k2")
    sleeve.repeat_rounds(["k2, p1, repeat(k4, p4), k2"], 5)
    sleeve.add_round("k2, inc, p1, repeat(k4, p4), inc, k2")
    sleeve.repeat_rounds(["k2, p2, repeat(k4, p4), k2"], 5)
    
    num_stitches = sleeve.get_current_num_of_stitches()
    print(f"After 4x sleeve increases, there are {num_stitches} stitches")

    sleeve.add_round("k2, inc, p2, repeat(k4, p4), inc, k2")
    sleeve.repeat_rounds(["k2, p3, repeat(k4, p4), k2"], 5)
    sleeve.add_round("k2, inc, p3, repeat(k4, p4), inc, k2")
    sleeve.repeat_rounds(["k2, p4, repeat(k4, p4), k2"], 5)
    
    num_stitches = sleeve.get_current_num_of_stitches()
    print(f"After first 6x sleeve increases, there are {num_stitches} stitches")


    # raglan.repeat_rounds(["repeat(k1, p1)"], 15)
    # raglan.repeat_rounds(["repeat(k1)"], 30)
    # raglan.place_marker("WS", 4)
    # raglan.add_round("bo4, repeat(k1), rm").place_on_hold()
    # raglan.add_round("repeat(k1)")
    # raglan.repeat_rounds(
    #     ["k1, dec, repeat(k1), dec, k1",
    #     "repeat(k1)"]
    # , 23)
    # num_stitches = raglan.get_current_num_of_stitches()
    # raglan.place_marker("RS", int(num_stitches/2) - 6)
    # raglan.place_marker("RS", int(num_stitches/2) + 7)
    # raglan.add_round("k1, dec, repeat(k1), sm, bo13, sm, repeat(k1), dec, k1")
    # raglan.add_row("p26").place_on_hold()
    # raglan.add_row("k1, dec, repeat(k1), dec, k1")
    # raglan.add_row("repeat(p1)")
    # raglan.add_row("k1, dec, repeat(k1), dec, k1")
    # raglan.add_row("repeat(p1)")
    # raglan.add_row("k1, dec, repeat(k1), dec, k1")
    # raglan.add_row("repeat(p1)")
    # raglan.add_row("k1, dec, repeat(k1), dec, k1")
    # raglan.add_row("repeat(p1)")
    # raglan.add_row("k1, dec, repeat(k1), dec, k1")
    # raglan.add_row("repeat(p1)")
    # raglan.add_row("k1, dec, repeat(k1), dec, k1")
    # raglan.add_row("repeat(p1)")
    # raglan.add_row("k1, dec, repeat(k1), dec, k1")
    # raglan.add_row("repeat(p1)")
    # stitches_on_hold = raglan.add_row("").place_on_hold()
    # raglan.place_on_needle(stitches_on_hold, "WS")
    # raglan.add_row("repeat(p1)")
    # raglan.add_row("k1, dec, repeat(k1), dec, k1")
    # raglan.add_row("repeat(p1)")
    # raglan.add_row("k1, dec, repeat(k1), dec, k1")
    # raglan.add_row("repeat(p1)")
    # raglan.add_row("k1, dec, repeat(k1), dec, k1")
    # raglan.add_row("repeat(p1)")
    # raglan.add_row("k1, dec, repeat(k1), dec, k1")
    # raglan.add_row("repeat(p1)")
    # raglan.add_row("k1, dec, repeat(k1), dec, k1")
    # raglan.add_row("repeat(p1)")
    # raglan.add_row("k1, dec, repeat(k1), dec, k1")
    # raglan.add_row("repeat(p1)")
    # raglan.add_row("k1, dec, repeat(k1), dec, k1")
    # raglan.add_row("repeat(p1)")
  
    # raglan_back = chart_service.create_chart(name="raglan_back", start_side="RS", sts=23, rows=21)
    # # Attach observer
    # # visualization_service.attach_visualization_observer(raglan_back)
    # raglan_back.cast_on_start(122)
    # raglan_back.repeat_rounds(["repeat(k1, p1)"], 15)
    # raglan_back.repeat_rounds(["repeat(k1)"], 30)
    # raglan_back.place_marker("WS", 4)
    # raglan_back.add_round("bo4, repeat(k1), rm").place_on_hold()
    # raglan_back.add_round("repeat(k1)")
    # raglan_back.repeat_rounds(
    #     ["k1, dec, repeat(k1), dec, k1",
    #     "repeat(k1)"]
    # , 31)
    
    # sleeve = chart_service.create_chart(name="sleeve", start_side="RS", sts=23, rows=21)
    # # Attach observer
    # # visualization_service.attach_visualization_observer(sleeve)
    # sleeve.cast_on_start(60)
    # sleeve.repeat_rounds(["repeat(k1, p1)"], 15)
    # sleeve.add_round(["repeat(k2, inc)"]).cast_on(1)
    # sleeve.repeat_rounds(["repeat(k1)"], 96)
    # sleeve.add_round("bo7, repeat(k1)")
    # sleeve.repeat_rounds(["repeat(k1)"], 11)
    # sleeve.repeat_rounds(["k1, dec, repeat(k1), dec, k1",
    #                      "repeat(k1)"], 26)
    
    # join_demo1 = chart_service.create_chart(name="join_demo", start_side="RS", sts=23, rows=21)
    # join_demo1.cast_on_start(10)
    # join_demo1.repeat_rows(["k1, inc, repeat(k1), inc, k1", "repeat(k1)"], 3)
    # join_demo2 = chart_service.create_chart(name="join_demo2", start_side="RS", sts=23, rows=21)
    # join_demo2.cast_on_start(10)
    # join_demo2.repeat_rows(["k1, inc, repeat(k1), inc, k1", "repeat(k1)"], 3)
    # join_demo1.join(join_demo2)
    
    # chart_sections.append(raglan_back)
    # chart_sections.append(raglan)
    # chart_sections.append(sleeve)
    # chart_sections.append(join_demo1)
    chart_sections.append(sleeve)
          
    chart_service.save_charts(chart_sections)
    
    print(f"Data written to charts.json with {len(chart_sections)} chart(s):")
    for chart in chart_sections:
        print(f"  - {chart.name}.json")
    
    print("Data written to left_back.json")


if __name__ == "__main__":
    main()