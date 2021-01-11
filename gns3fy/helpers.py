from typing import List, Any, Dict
from urllib.parse import urlparse
from math import pi, sin, cos
from .projects import Project


def nodes_summary(project: Project) -> List[Any]:
    """Returns a summary of the nodes inside of a given project.

    Args:

    - `project_id`
    - `connector`

    Returns:

    - `List[Any]`: List of tuples node name, status, console and node_id

    `[(node_name, node_status, node_console, node_id) ...]`
    """
    if project.status != "opened":
        raise ValueError("Project must be opened before getting all node info")

    project.get()

    return [
        (name, _node.status, _node.console, _node.node_id)
        for name, _node in project.nodes.items()
    ]


def nodes_inventory(project: Project) -> Dict[str, Any]:
    """Returns an inventory-style dictionary of the nodes

    Example:

    ```python
    {
        "router01": {
            "server": "127.0.0.1",
            "name": "router01",
            "console_port": 5077,
            "type": "vEOS"
        }
    }
    ```

    Args

    - `project (Project)`: Project object
    """
    # Refresh project
    project.get()

    _nodes_inventory = {}
    _server = urlparse(project._connector.base_url).hostname

    for name, _node in project.nodes.items():

        _nodes_inventory.update(
            {
                name: {
                    "server": _server,
                    "name": name,
                    "console_port": _node.console,
                    "console_type": _node.console_type,
                    "type": _node.node_type,
                    "template": _node.template,
                }
            }
        )

    return _nodes_inventory


def arrange_nodes_circular(project: Project, radius: int = 120) -> None:
    """Re-arrgange the existing nodes in a circular fashion

    Args:

    - `project (Project)`: Project object
    - `radius (int)`: Radius length to apply

    **Example**

    ```python
    >>> proj = Project(name='project_name', connector=Connector)
    >>> proj.arrange_nodes()
    ```
    """
    # Refresh project
    project.get()

    if project.status != "opened":
        project.open()

    _angle = (2 * pi) / len(project.nodes)
    # The Y Axis is inverted in GNS3, so the -Y is UP
    for index, n in enumerate(project.nodes.values()):
        _x = int(radius * (sin(_angle * index)))
        _y = int(radius * (-cos(_angle * index)))
        n.update(x=_x, y=_y)


def links_summary(project: Project) -> List[Any]:
    """Returns a summary of the links inside the Project.

    Args:

    - `project (Project)`: Project object

    Returns:

    - `List[Any]`: List of tuples nodes and enpoints of each link. For example:

    `[(node_a, port_a, node_b, port_b) ...]`
    """
    # refresh_project(project, nodes=True, links=True)
    if project.status != "opened":
        raise ValueError("Project must be opened before getting all link info")

    project.get()

    _links_summary = []
    for _l in project.links.values():
        if not _l.nodes:
            continue
        _side_a = _l.nodes[0]
        _side_b = _l.nodes[1]
        _node_a = [x for x in project.nodes.values() if x.node_id == _side_a.node_id][0]
        _port_a = [
            x.name
            for x in _node_a.ports
            if x.port_number == _side_a.port_number
            and x.adapter_number == _side_a.adapter_number
        ][0]
        _node_b = [x for x in project.nodes.values() if x.node_id == _side_b.node_id][0]
        _port_b = [
            x.name
            for x in _node_b.ports
            if x.port_number == _side_b.port_number
            and x.adapter_number == _side_b.adapter_number
        ][0]

        _links_summary.append((_node_a.name, _port_a, _node_b.name, _port_b))

    return _links_summary
