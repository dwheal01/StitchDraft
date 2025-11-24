from dataclasses import dataclass

@dataclass
class ChartConfig:
    """Configuration for creating a chart section."""
    name: str
    start_side: str  # 'RS' or 'WS'
    sts: int  # stitches per 4 inches
    rows: int  # rows per 4 inches