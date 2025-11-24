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

if __name__ == "__main__":
    # Initialize service layer
    repository = ChartRepository(data_path="engine")
    chart_service = ChartService(chart_repository=repository)
    
    chart_sections = []
    
    # Replace ONLY the creation line - keep everything else the same
    raglan = chart_service.create_chart(name="raglan", start_side="RS", sts=23, rows=21)
    # ... rest of raglan code stays the same ...
    
    raglan_back = chart_service.create_chart(name="raglan_back", start_side="RS", sts=23, rows=21)
    # ... rest of raglan_back code stays the same ...
    
    sleeve = chart_service.create_chart(name="sleeve", start_side="RS", sts=23, rows=21)
    # ... rest of sleeve code stays the same ...
    
    chart_sections.append(raglan_back)
    chart_sections.append(raglan)
    chart_sections.append(sleeve)
    chart_service.save_charts(chart_sections)
    
    print(f"Data written to charts.json with {len(chart_sections)} chart(s):")
    for chart in chart_sections:
        print(f"  - {chart.name}.json")
    
    print("Data written to left_back.json")