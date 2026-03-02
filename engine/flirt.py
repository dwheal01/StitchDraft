import json
import sys
from pathlib import Path

# Ensure project root is in path (needed when running as script, not as installed package)
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

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
    back = chart_service.create_chart(name="lobster_back", start_side="RS", sts=22, rows=44)
    # Attach observer right after creation
    # visualization_service.attach_visualization_observer(raglan)
    back.cast_on_start(41)
    back.repeat_rows(["k2, inc, repeat(k1), inc, k2",
                        "repeat(k1)"], 17)
    back.add_row("repeat(k1,p1)")
    back.repeat_rows(["work est"], 3)
   
    # # get the number of rows
    # num_rows = back.get_current_row_num()
    # print(f"Number of rows: {num_rows} after back inc")

    # back.repeat_rows(["repeat(k1)"], 36)
    # back.repeat_rows(["k2, inc, repeat(k1), inc, k2",
    #                   "repeat(k1)"], 14)
    # back.repeat_rows(["repeat(k1)"], 98)
    #  # get the number of stitches
    # num_stitches = back.get_current_num_of_stitches()


    # front = chart_service.create_chart(name="lobster_front", start_side="RS", sts=22, rows=44)
    # front.cast_on_start(26)
    # front.repeat_rows(["k2, dec, repeat(k1)", "repeat(k1)"], 9)
    # front.repeat_rows(["repeat(k1)"], 14)
    # front.repeat_rows(["repeat(k1), inc, k2", "repeat(k1)"], 12)
    # front.add_row("repeat(k1)").cast_on(9)
    # front.repeat_rows(["repeat(k1)"], 41)

    # front.repeat_rows(["k2, inc, repeat(k1)", "repeat(k1)"], 14)
    # get the number of rows
    # num_rows = front.get_current_row_num()
    # print(f"Number of rows: {num_rows} after front inc")
    # front.repeat_rows(["repeat(k1)"], 98)
    chart_sections.append(back)
    # chart_sections.append(front)
          
    chart_service.save_charts(chart_sections)
    
    print(f"Data written to charts.json with {len(chart_sections)} chart(s):")
    for chart in chart_sections:
        print(f"  - {chart.name}.json")
    


if __name__ == "__main__":
    main()