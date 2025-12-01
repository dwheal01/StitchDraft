import json
import os
from typing import List, Optional
from pathlib import Path
from engine.domain.interfaces.ichart_repository import IChartRepository
from engine.data.models.chart_data import ChartData
from engine.data.repositories.chart_data_serializer import ChartDataSerializer
from engine.presentation.mappers.view_model_mapper import ViewModelMapper
# Note: ChartDataValidator will be added later
# from engine.data.repositories.chart_data_validator import ChartDataValidator


class ChartRepository(IChartRepository):
    """Repository for persisting and loading chart data."""
    
    def __init__(self, data_path: str = "engine", validator=None):
        """
        Initialize the repository.
        
        Args:
            data_path: Base path for storing chart files
            validator: Optional ChartDataValidator for validation
        """
        self.data_path = Path(data_path)
        self.validator = validator
        self.serializer = ChartDataSerializer()
        self.view_model_mapper = ViewModelMapper()
        
        # Ensure data directory exists
        self.data_path.mkdir(parents=True, exist_ok=True)
    
    def save_chart(self, chart_data: ChartData) -> None:
        """
        Save a single chart to a JSON file.
        
        Args:
            chart_data: ChartData to save
        """
        # Validate if validator is available
        if self.validator:
            validation_result = self.validator.validate(chart_data)
            validation_result.raise_if_invalid()
        
        # Serialize to JSON
        json_data = self.serializer.serialize_deterministic_from_chart_data(chart_data)
        
        # Save to file
        file_path = self.data_path / f"{chart_data.name}.json"
        with open(file_path, "w") as f:
            f.write(json_data)
    
    def load_chart(self, name: str) -> ChartData:
        """
        Load a single chart from a JSON file.
        
        Args:
            name: Name of the chart to load
            
        Returns:
            ChartData object
        """
        file_path = self.data_path / f"{name}.json"
        
        if not file_path.exists():
            raise FileNotFoundError(f"Chart file not found: {file_path}")
        
        with open(file_path, "r") as f:
            data = json.load(f)
        
        # Convert to ChartData
        chart_data = self._dict_to_chart_data(data)
        
        # Validate if validator is available
        if self.validator:
            validation_result = self.validator.validate(chart_data)
            validation_result.raise_if_invalid()
        
        return chart_data
    
    def load_all_charts(self) -> List[ChartData]:
        """
        Load all charts from the data directory.
        
        Returns:
            List of ChartData objects
        """
        charts = []
        
        # Find all JSON files in the data directory
        for file_path in self.data_path.glob("*.json"):
            # Skip the master charts.json file
            if file_path.name == "charts.json":
                continue
            
            try:
                chart_name = file_path.stem  # filename without extension
                chart_data = self.load_chart(chart_name)
                charts.append(chart_data)
            except Exception as e:
                # Log error but continue loading other charts
                print(f"Error loading chart from {file_path}: {e}")
                continue
        
        return charts
    
    def save_charts(self, charts: List[ChartData]) -> None:
        """
        Save multiple charts to individual files and a master file.
        Uses ViewModels for the master charts.json file.
        
        Args:
            charts: List of ChartData objects to save
        """
        # Save individual chart files (using raw ChartData)
        for chart_data in charts:
            self.save_chart(chart_data)
        
        # Convert to ViewModels for the master charts.json file
        view_models = [self.view_model_mapper.to_view_model(chart) for chart in charts]
        
        # Save master charts file with ViewModels
        master_data = {
            "charts": [
                self.view_model_mapper.view_model_to_dict(view_model)
                for view_model in view_models
            ]
        }
        
        master_file_path = self.data_path / "charts.json"
        with open(master_file_path, "w") as f:
            json.dump(master_data, f, indent=2)
    
    def _dict_to_chart_data(self, data: dict) -> ChartData:
        """Convert dictionary to ChartData object."""
        nodes = [self.serializer._convert_single_node(node_dict) for node_dict in data.get("nodes", [])]
        links = [self.serializer._convert_single_link(link_dict) for link_dict in data.get("links", [])]
        
        return ChartData(
            name=data.get("name", ""),
            nodes=nodes,
            links=links
        )