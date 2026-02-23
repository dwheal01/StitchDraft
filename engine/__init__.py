"""
Knitting Pattern Visualization Library

A library for generating visual representations of knitting patterns
by parsing pattern instructions and creating interactive charts.
"""

# Main public API
from engine.domain.services.chart_service import ChartService
from engine.data.repositories.chart_repository import ChartRepository
from engine.chart_section import ChartSection

# Optional: Expose visualization services if users need them
from engine.presentation.services.chart_visualization_service import ChartVisualizationService

__version__ = "0.1.0"
__all__ = [
    'ChartService',
    'ChartRepository', 
    'ChartSection',
    'ChartVisualizationService',
]


