# SPDX-License-Identifier: GPL-3.0-or-later
#
# gns3fy-next - GNS3 REST API python library with API v3 support
#
# Copyright (C) 2025 Guobin Yue
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""
Drawing utilities for gns3fy-next

This module is part of gns3fy-next, a fork of the gns3fy project.

Functions used as helpers for drawing objects in a GNS3 Project.

Project Home: https://github.com/yueguobin/gns3fy-next
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
