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
gns3fy-next package

This package is a fork of the gns3fy project, providing enhanced features and
GNS3 Server API v3 support.

Key features:
- GNS3 Server API v2 and v3 support
- JWT-based authentication for v3 API (automatic token management)
- Direct JWT token authentication support
- Tags support for templates and projects
- Project, node, link, and drawing management
- Template management with tags
- Snapshot management

Project Home: https://github.com/yueguobin/gns3fy-next
"""

from .gns3fy import Gns3Connector, Project, Node, Link

__all__ = ["Gns3Connector", "Project", "Node", "Link"]
