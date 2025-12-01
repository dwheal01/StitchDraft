import sys
import os
from pathlib import Path

# Add project root to path so we can import from engine
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from engine.domain.services.chart_service import ChartService
from engine.data.repositories.chart_repository import ChartRepository
# Keep old import temporarily for comparison
from chart_section import ChartSection
import json
from typing import Optional, TYPE_CHECKING
from engine.presentation.services.chart_visualization_service import ChartVisualizationService

if TYPE_CHECKING:
    from engine.chart_section import ChartSection


if __name__ == "__main__":
      # Initialize service layer
      repository = ChartRepository(data_path="engine")
      chart_service = ChartService(chart_repository=repository)
      visualization_service = ChartVisualizationService(chart_service)
      chart_sections = []
    
       # Replace ONLY the creation line - keep everything else the same
      raglan = chart_service.create_chart(name="raglan", start_side="RS", sts=23, rows=21)
      # Attach observer right after creation
      chart_service.attach_visualization_observer(raglan)
      raglan.cast_on_start(122)
      raglan.repeat_rounds(["repeat(k1, p1)"], 15)
      raglan.repeat_rounds(["repeat(k1)"], 30)
      raglan.place_marker("WS", 4)
      raglan.add_round("bo4, repeat(k1), rm").place_on_hold()
      raglan.add_round("repeat(k1)")
      raglan.repeat_rounds(
         ["k1, dec, repeat(k1), dec, k1",
         "repeat(k1)"]
      , 23)
      num_stitches = raglan.get_current_num_of_stitches()
      raglan.place_marker("RS", int(num_stitches/2) - 6)
      raglan.place_marker("RS", int(num_stitches/2) + 7)
      raglan.add_round("k1, dec, repeat(k1), sm, bo13, sm, repeat(k1), dec, k1")
      raglan.add_row("p26").place_on_hold()
      raglan.add_row("k1, dec, repeat(k1), dec, k1")
      raglan.add_row("repeat(p1)")
      raglan.add_row("k1, dec, repeat(k1), dec, k1")
      raglan.add_row("repeat(p1)")
      raglan.add_row("k1, dec, repeat(k1), dec, k1")
      raglan.add_row("repeat(p1)")
      raglan.add_row("k1, dec, repeat(k1), dec, k1")
      raglan.add_row("repeat(p1)")
      raglan.add_row("k1, dec, repeat(k1), dec, k1")
      raglan.add_row("repeat(p1)")
      raglan.add_row("k1, dec, repeat(k1), dec, k1")
      raglan.add_row("repeat(p1)")
      raglan.add_row("k1, dec, repeat(k1), dec, k1")
      raglan.add_row("repeat(p1)")
      stitches_on_hold = raglan.add_row("").place_on_hold()
      raglan.place_on_needle(stitches_on_hold, "WS")
      raglan.add_row("repeat(p1)")
      raglan.add_row("k1, dec, repeat(k1), dec, k1")
      raglan.add_row("repeat(p1)")
      raglan.add_row("k1, dec, repeat(k1), dec, k1")
      raglan.add_row("repeat(p1)")
      raglan.add_row("k1, dec, repeat(k1), dec, k1")
      raglan.add_row("repeat(p1)")
      raglan.add_row("k1, dec, repeat(k1), dec, k1")
      raglan.add_row("repeat(p1)")
      raglan.add_row("k1, dec, repeat(k1), dec, k1")
      raglan.add_row("repeat(p1)")
      raglan.add_row("k1, dec, repeat(k1), dec, k1")
      raglan.add_row("repeat(p1)")
      raglan.add_row("k1, dec, repeat(k1), dec, k1")
      raglan.add_row("repeat(p1)")
    
      raglan_back = chart_service.create_chart(name="raglan_back", start_side="RS", sts=23, rows=21)
      # Attach observer
      chart_service.attach_visualization_observer(raglan_back)
      raglan_back.cast_on_start(122)
      raglan_back.repeat_rounds(["repeat(k1, p1)"], 15)
      raglan_back.repeat_rounds(["repeat(k1)"], 30)
      raglan_back.place_marker("WS", 2)
      raglan_back.add_round("bo4, repeat(k1), rm").place_on_hold()
      raglan_back.add_round("repeat(k1)")
      raglan_back.repeat_rounds(
         ["k1, dec, repeat(k1), dec, k1",
         "repeat(k1)"]
      , 31)
      
      sleeve = chart_service.create_chart(name="sleeve", start_side="RS", sts=23, rows=21)
      # Attach observer
      chart_service.attach_visualization_observer(sleeve)
      sleeve.cast_on_start(60)
      sleeve.repeat_rounds(["repeat(k1, p1)"], 15)
      sleeve.add_round(["repeat(k2, inc)"]).cast_on(1)
      sleeve.repeat_rounds(["repeat(k1)"], 96)
      sleeve.add_round("bo7, repeat(k1)")
      sleeve.repeat_rounds(["repeat(k1)"], 11)
      sleeve.repeat_rounds(["k1, dec, repeat(k1), dec, k1",
                           "repeat(k1)"], 26)
      
      chart_sections.append(raglan_back)
      chart_sections.append(raglan)
      chart_sections.append(sleeve)
      
      # Attach observers to all charts before saving (using visualization service)
      for chart in chart_sections:
          visualization_service.attach_visualization_observer(chart)
      
      chart_service.save_charts(chart_sections)
      
      print(f"Data written to charts.json with {len(chart_sections)} chart(s):")
      for chart in chart_sections:
         print(f"  - {chart.name}.json")
      
      print("Data written to left_back.json")