"""
Functions used as helpers for drawing objects in a GNS3 Project.
"""


def generate_rectangle_svg(
    height: int = 100,
    width: int = 200,
    fill: str = "#ffffff",
    fill_opacity: float = 1.0,
    stroke: str = "#000000",
    stroke_width: int = 2,
) -> str:
    return (
        f'<svg height="{height}" width="{width}"><rect fill="{fill}" fill-opacity="'
        f'{fill_opacity}" height="{height}" stroke="{stroke}" stroke-width="'
        f'{stroke_width}" width="{width}" /></svg>'
    )


def generate_ellipse_svg(
    height: float = 200.0,
    width: float = 200.0,
    cx: int = 100,
    cy: int = 100,
    fill: str = "#ffffff",
    fill_opacity: float = 1.0,
    rx: int = 100,
    ry: int = 100,
    stroke: str = "#000000",
    stroke_width: int = 2,
) -> str:
    return (
        f'<svg height="{height}" width="{width}"><ellipse cx="{cx}" cy="{cy}" fill="'
        f'{fill}" fill-opacity="{fill_opacity}" rx="{rx}" ry="{ry}" stroke="{stroke}" '
        f'stroke-width="{stroke_width}" /></svg>'
    )


def generate_line_svg(
    height: int = 0,
    width: int = 200,
    x1: int = 0,
    x2: int = 200,
    y1: int = 0,
    y2: int = 0,
    stroke: str = "#000000",
    stroke_width: int = 2,
) -> str:
    return (
        f'<svg height="{height}" width="{width}"><line stroke="{stroke}" stroke-width="'
        f'{stroke_width}" x1="{x1}" x2="{x2}" y1="{y1}" y2="{y2}" /></svg>'
    )


def parsed_x(x: int, obj_width: int = 100) -> int:
    return x * obj_width


def parsed_y(y: int, obj_height: int = 100) -> int:
    return (y * obj_height) * -1
