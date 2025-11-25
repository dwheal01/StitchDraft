"""Test ViewModels and ViewModelMapper."""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from engine.data.models.chart_data import ChartData
from engine.data.models.node import Node
from engine.data.models.link import Link
from engine.presentation.mappers.view_model_mapper import ViewModelMapper

def test_view_model_mapper():
    """Test ViewModelMapper conversion."""
    print("Testing ViewModelMapper...")
    
    # Create sample data
    nodes = [
        Node(id="n1", type="k", row=0, fx=10.0, fy=20.0),
        Node(id="n2", type="p", row=0, fx=30.0, fy=20.0),
    ]
    links = [
        Link(source="n1", target="n2"),
    ]
    chart_data = ChartData(name="test_chart", nodes=nodes, links=links)
    
    # Convert to view model
    mapper = ViewModelMapper()
    view_model = mapper.to_view_model(chart_data)
    
    # Verify conversion
    assert view_model.name == "test_chart"
    assert len(view_model.nodes) == 2
    assert len(view_model.links) == 1
    assert view_model.nodes[0].id == "n1"
    assert view_model.nodes[0].x == 10.0
    assert view_model.nodes[0].y == 20.0
    assert view_model.links[0].source_id == "n1"
    assert view_model.links[0].target_id == "n2"
    
    print("✓ ViewModelMapper test passed!")
    return view_model

if __name__ == "__main__":
    try:
        test_view_model_mapper()
        print("\n✓ All ViewModel tests passed!")
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()