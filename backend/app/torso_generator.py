from __future__ import annotations

from typing import Literal, Optional

# ---- Craft Yarn Council measurements (simplified, XS–5XL) ----
# Values are in inches. This is copied from /Users/dianawhealan/Documents/knitviz/engine/test.py
CYC_MEASUREMENTS: dict[str, dict[str, float]] = {
    "XS": {
        "shoulder_width": 14.25,
        "back_length": 16.5,
        "bust_circ": 29,
        "waist_circ": 23.5,
        "hip_circ": 33.5,
        "armhole_depth": 6.25,
        "upper_arm_circ": 9.75,
        "arm_length": 19.25,
    },
    "S": {
        "shoulder_width": 14.75,
        "back_length": 17,
        "bust_circ": 33,
        "waist_circ": 25.75,
        "hip_circ": 35.5,
        "armhole_depth": 6.75,
        "upper_arm_circ": 10.25,
        "arm_length": 19.75,
    },
    "M": {
        "shoulder_width": 15.75,
        "back_length": 17.25,
        "bust_circ": 37,
        "waist_circ": 29,
        "hip_circ": 39,
        "armhole_depth": 7.25,
        "upper_arm_circ": 11,
        "arm_length": 20.25,
    },
    "L": {
        "shoulder_width": 16.75,
        "back_length": 17.5,
        "bust_circ": 41,
        "waist_circ": 33,
        "hip_circ": 43,
        "armhole_depth": 7.75,
        "upper_arm_circ": 12,
        "arm_length": 20.75,
    },
    "XL": {
        "shoulder_width": 17.5,
        "back_length": 17.75,
        "bust_circ": 45,
        "waist_circ": 37,
        "hip_circ": 47,
        "armhole_depth": 8.25,
        "upper_arm_circ": 13.5,
        "arm_length": 20.25,
    },
    "2XL": {
        "shoulder_width": 18,
        "back_length": 18,
        "bust_circ": 49,
        "waist_circ": 41,
        "hip_circ": 52.5,
        "armhole_depth": 8.75,
        "upper_arm_circ": 15.5,
        "arm_length": 21.25,
    },
    "3XL": {
        "shoulder_width": 18,
        "back_length": 18,
        "bust_circ": 53,
        "waist_circ": 44.5,
        "hip_circ": 54.5,
        "armhole_depth": 9.25,
        "upper_arm_circ": 17,
        "arm_length": 18,
    },
    "4XL": {
        "shoulder_width": 18,
        "back_length": 18,
        "bust_circ": 57,
        "waist_circ": 46.5,
        "hip_circ": 56.5,
        "armhole_depth": 9.75,
        "upper_arm_circ": 18.5,
        "arm_length": 18.5,
    },
    "5XL": {
        "shoulder_width": 22,
        "back_length": 18,
        "bust_circ": 61,
        "waist_circ": 49.5,
        "hip_circ": 61.5,
        "armhole_depth": 10.25,
        "upper_arm_circ": 18.5,
        "arm_length": 18.5,
    },
}

TorsoUnits = Literal["in"]


def _build_svg(
    shoulder_width: float,
    back_length: float,
    bust_circ: float,
    waist_circ: float,
    hip_circ: float,
    armhole_depth: float,
    upper_arm_circ: float,
    arm_length: float,
    *,
    apex_depth: Optional[float] = None,
    waist_to_hip: float = 8,
    top_padding: float = 2,
    units: TorsoUnits = "in",
    ease: float = 0.0,
) -> tuple[str, str, float, float]:
    """Core SVG builder used by both CYC and custom input.

    Returns: (svg_string, viewBox_string, width, height)
    - Coordinates are in inches (matching test.py).
    """
    # Widths (apply ease to circumferences)
    bust_width = (bust_circ + ease) / 2
    waist_width = (waist_circ + ease) / 2
    hip_width = (hip_circ + ease) / 2
    arm_width = upper_arm_circ / 2

    # Vertical levels
    y_top = top_padding
    y_underarm = y_top + armhole_depth
    y_waist = y_top + back_length
    y_hip = y_waist + waist_to_hip

    # Apex line
    if apex_depth is not None:
        y_apex = y_top + apex_depth
    else:
        y_apex = y_top + back_length * 0.55

    # Half widths
    x_shoulder = shoulder_width / 2
    x_underarm = (x_shoulder + bust_width / 2) / 2
    x_bust = bust_width / 2
    x_waist = waist_width / 2
    x_hip = hip_width / 2

    # Torso outline (half)
    torso_half_path = (
        f"M0,{y_top} "
        f"L{x_shoulder},{y_top} "
        f"L{x_underarm},{y_underarm} "
        f"L{x_bust},{y_apex} "
        f"L{x_waist},{y_waist} "
        f"L{x_hip},{y_hip} "
        f"L0,{y_hip} Z"
    )

    # Arms (rectangles)
    arm_height = arm_width
    arm_half_path = (
        f"M{x_shoulder},{y_top} "
        f"L{x_shoulder + arm_length},{y_top} "
        f"L{x_shoulder + arm_length},{y_top + arm_height} "
        f"L{x_shoulder},{y_top + arm_height} Z"
    )

    total_height = top_padding + back_length + waist_to_hip

    # Shoulder notches
    tick_len = 1.0
    shoulder_notches = (
        f'<line x1="{x_shoulder}" y1="{y_top}" '
        f'      x2="{x_shoulder}" y2="{y_top + tick_len}" '
        f'      stroke="red" stroke-width="0.2" stroke-dasharray="0.3,0.2"/>'
        f'<line x1="{-x_shoulder}" y1="{y_top}" '
        f'      x2="{-x_shoulder}" y2="{y_top + tick_len}" '
        f'      stroke="red" stroke-width="0.2" stroke-dasharray="0.3,0.2"/>'
    )

    # Underarm line (red dashed guideline across torso)
    underarm_line = (
        f'<line x1="{-x_underarm}" y1="{y_underarm}" '
        f'      x2="{x_underarm}" y2="{y_underarm}" '
        f'      stroke="red" stroke-width="0.15" stroke-dasharray="0.5,0.5"/>'
    )

    # Nipple line
    nipple_line = (
        f'<line x1="{-x_bust}" y1="{y_apex}" '
        f'      x2="{x_bust}" y2="{y_apex}" '
        f'      stroke="blue" stroke-width="0.15" stroke-dasharray="0.5,0.5"/>'
    )

    width = shoulder_width + 2 * arm_length
    height = total_height
    view_box = f"{-(shoulder_width / 2 + arm_length)} 0 {width} {height}"

    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     width="{width}{units}"
     height="{height}{units}"
     viewBox="{view_box}">
  <rect width="100%" height="100%" fill="white"/>
  <!-- Left torso -->
  <path d="{torso_half_path}" fill="black" transform="scale(-1,1)" />
  <!-- Right torso -->
  <path d="{torso_half_path}" fill="black" />
  <!-- Left arm -->
  <path d="{arm_half_path}" fill="black" transform="scale(-1,1)" />
  <!-- Right arm -->
  <path d="{arm_half_path}" fill="black" />
  {shoulder_notches}
  {underarm_line}
  {nipple_line}
</svg>
"""

    return svg, view_box, width, height


def generate_torso_svg_from_size(
    size: str,
    *,
    apex_depth: Optional[float] = None,
    waist_to_hip: float = 8,
    top_padding: float = 2,
    units: TorsoUnits = "in",
    ease: float = 0.0,
) -> tuple[str, str, float, float]:
    """Use CYC measurements by size label (XS–5XL)."""
    if size not in CYC_MEASUREMENTS:
        raise ValueError(f"Unknown size '{size}'. Valid: {list(CYC_MEASUREMENTS.keys())}")
    return _build_svg(**CYC_MEASUREMENTS[size], apex_depth=apex_depth, waist_to_hip=waist_to_hip, top_padding=top_padding, units=units, ease=ease)


def generate_torso_svg_custom(
    *,
    shoulder_width: float,
    back_length: float,
    bust_circ: float,
    waist_circ: float,
    hip_circ: float,
    armhole_depth: float,
    upper_arm_circ: float,
    arm_length: float,
    apex_depth: Optional[float] = None,
    waist_to_hip: float = 8,
    top_padding: float = 2,
    units: TorsoUnits = "in",
    ease: float = 0.0,
) -> tuple[str, str, float, float]:
    """Use custom measurements directly."""
    return _build_svg(
        shoulder_width=shoulder_width,
        back_length=back_length,
        bust_circ=bust_circ,
        waist_circ=waist_circ,
        hip_circ=hip_circ,
        armhole_depth=armhole_depth,
        upper_arm_circ=upper_arm_circ,
        arm_length=arm_length,
        apex_depth=apex_depth,
        waist_to_hip=waist_to_hip,
        top_padding=top_padding,
        units=units,
        ease=ease,
    )

