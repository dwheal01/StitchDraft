"""Test ChartService and ChartRepository integration."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.domain.services.chart_service import ChartService
from engine.data.repositories.chart_repository import ChartRepository
from engine.domain.factories.chart_section_factory import ChartSectionFactory

def test_service_creates_and_saves():
    """Test that ChartService can create and save a chart."""
    print("Testing ChartService integration...")
    
    # Create repository and service
    repository = ChartRepository(data_path="engine")
    service = ChartService(chart_repository=repository)
    
    # Create a simple chart
    chart = service.create_chart(name="test_integration", start_side="RS", sts=23, rows=21)
    chart.cast_on_start(10)
    chart.add_row("k1")
    
    # Save using service
    service.save_chart(chart)
    print("✓ Chart created and saved via service")
    
    # Load using service
    chart_data = service.load_chart("test_integration")
    print(f"✓ Chart loaded: {chart_data.name} with {len(chart_data.nodes)} nodes")
    
    return service

if __name__ == "__main__":
    try:
        service = test_service_creates_and_saves()
        print("\n✓ Service integration test passed!")
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()