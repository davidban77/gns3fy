import time

from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urlparse
from math import pi, sin, cos
from .models import (
    connector,
    drawings,
    projects,
    ports,
    nodes,
    templates,
    links,
    snapshots,
)


# ############## Connector ###############
def create_connector(
    url: str,
    user: Optional[str] = None,
    cred: Optional[str] = None,
    verify: bool = False,
    api_version: int = 2,
    retries: int = 3,
    timeout: int = 5,
    proxies: Optional[Dict[str, Any]] = None,
) -> connector.Connector:
    """Creates a GNS3 Connector object

    Args:

    - `url (str)`: URL of the GNS3 server (**required**)
    - `user (Optional[str], optional)`: User used for authentication
    - `cred (Optional[str], optional)`: Password used for authentication
    - `verify (bool, optional)`: Whether or not to verify SSL
    - `api_version (int, optional)`: GNS3 server REST API version
    - `retries (int, optional)`: Retry values to connect. Defaults to 3.
    - `timeout (int, optional)`: Timeout value in secs. Defaults to 5.
    - `proxies (Optional[Dict[str, Any]], optional)`: Proxies dictionary. Optional

    Returns:

    - `connector.Connector`: GNS3 Connector object
    """
    return connector.Connector(
        url=url,
        user=user,
        cred=cred,
        verify=verify,
        api_version=api_version,
        retries=retries,
        timeout=timeout,
        proxies=proxies,
    )


# ############## Projects ###############
def get_projects(connector: connector.Connector) -> List[projects.Project]:
    """Retrieves all GNS3 Projects

    Args:

    - `connector (Connector)`: GNS3 connector object

    Returns:

    - `List[Project]`: List of Project objects
    """
    _raw_projects = connector.http_call(
        "get", url=f"{connector.base_url}/projects"
    ).json()

    return [projects.Project(connector=connector, **proj) for proj in _raw_projects]


def refresh_project(
    project: projects.Project,
    links: bool = True,
    nodes: bool = True,
    snapshots: bool = True,
    drawings: bool = True,
) -> None:
    if snapshots:
        project.snapshots = set(get_snapshots(project))
    if drawings:
        project.drawings = set(get_drawings(project))
    if nodes:
        project.nodes = set(get_nodes(project))
    if links:
        project.links = set(get_links(project))


def search_project(
    connector: connector.Connector,
    name: Optional[str] = None,
    project_id: Optional[str] = None,
) -> Optional[projects.Project]:
    """Searches for GNS3 Project from a given project name or ID

    Args:

    - `connector (Connector)`: GNS3 connector object
    - `name (Optional[str], optional)`: Project name. Defaults to None.
    - `project_id (Optional[str], optional)`: Project ID. Defaults to None.

    Raises:

    - `ValueError`: If name or project ID is not submitted

    Returns:

    - `Optional[Project]`: `Project` if found, else `None`
    """
    try:
        if name is not None:
            return next(prj for prj in get_projects(connector) if prj.name == name)

        elif project_id is not None:
            return next(
                prj for prj in get_projects(connector) if prj.project_id == project_id
            )

        else:
            raise ValueError("Need to submit either name or project_id")
    except StopIteration:
        return None


def create_project(
    connector: connector.Connector, name: str, **kwargs: Dict[str, Any]
) -> projects.Project:
    """Creates a GNS3 Project

    Args:

    - `connector (Connector)`: GNS3 connector object
    - `name (str)`: Name of the project
    - `kwargs (Dict[str, Any])`: Keyword attributes of the project to create

    Raises:

    - `ValueError`: If project already exists

    Returns:

    - `Project`: Project object
    """
    _sproject = search_project(connector, name=name)

    if _sproject:
        raise ValueError(f"Project with same name already exists: {name}")

    _project = projects.Project(connector=connector, name=name, **kwargs)

    _project.create()
    return _project


def delete_project(
    connector: connector.Connector,
    name: Optional[str] = None,
    project_id: Optional[str] = None,
) -> None:
    """Deletes a GNS3 Project

    Args:

    - `connector (Connector)`: GNS3 connector object
    - `name (Optional[str], optional)`: Project name. Defaults to None.
    - `project_id (Optional[str], optional)`: Project ID. Defaults to None.

    Raises:

    - `ValueError`: If name of project ID is not submitted
    - `ValueError`: If project is not found
    """
    _sproject = search_project(connector=connector, name=name, project_id=project_id)

    if _sproject is None:
        raise ValueError("Project not found")

    _sproject.delete()


# ############## Drawing ###############
def get_drawings(project: projects.Project) -> List[drawings.Drawing]:
    """Retrieves all GNS3 Project Snapshots

    Args:

    - `project (Project)`: Project object

    Returns:

    - `List[Drawing]`: List of Drawing objects
    """

    _raw_drawings = project._connector.http_call(
        "get",
        url=f"{project._connector.base_url}/projects/{project.project_id}/drawings",
    ).json()

    return [
        drawings.Drawing(connector=project._connector, **_drawing)
        for _drawing in _raw_drawings
    ]


def search_drawing(
    project: projects.Project, value: str, type: str = "svg"
) -> Optional[drawings.Drawing]:
    """Searches for GNS3 Drawing from a given drawing svg or ID

    Args:

    - `project (Project)`: Project object
    - `value (str)`: Drawing name of ID
    - `type (str)`: Type of attribute. `name` or `drawing_id`

    Returns:

    - `Optional[Drawing]`: `Drawing` if found, else `None`
    """
    # Refresh project
    refresh_project(project, drawings=True)

    try:
        if type == "svg":
            return next(draw for draw in get_drawings(project) if draw.svg == value)
        elif type == "drawing_id":
            return next(
                draw for draw in get_drawings(project) if draw.drawing_id == value
            )
        return None
    except StopIteration:
        return None


def create_drawing(project: projects.Project, svg: str) -> drawings.Drawing:
    """Creates a GNS3 Project Drawing

    Args:

    - `project (Project)`: Project object
    - `svg (str)`: Drawing svg

    Raises:

    - `ValueError`: If drawing is already created

    Returns:

    - `Drawing`: Drawing object
    """

    _sdrawing = search_drawing(project, svg)

    if _sdrawing:
        raise ValueError(f"Drawing with same svg already exists: {_sdrawing}")

    _drawing = drawings.Drawing(
        connector=project._connector, project_id=project.project_id, svg=svg
    )

    _drawing.create()
    project.drawings.add(_drawing)
    return _drawing


def delete_drawing(
    project: projects.Project,
    name: Optional[str] = None,
    drawing_id: Optional[str] = None,
) -> None:
    """Deletes GNS3 Project Drawing

    Args:

    - `project (Project)`: Project object
    - `name (Optional[str], optional)`: Drawing name. Defaults to None.
    - `drawing_id (Optional[str], optional)`: Drawing ID. Defaults to None.

    Raises:

    - `ValueError`: When neither name nor ID was submitted
    - `ValueError`: When drawing was not found
    """

    if name is not None:
        _sdrawing = search_drawing(project, name)
    elif drawing_id is not None:
        _sdrawing = search_drawing(project, drawing_id, type="drawing_id")
    else:
        raise ValueError("Need to submit either name or drawing_id")

    if _sdrawing is None:
        raise ValueError("Snapshot not found")

    _sdrawing.delete()
    project.drawings.remove(_sdrawing)


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


# ############## Ports ###############
def search_port(node: nodes.Node, name: str) -> Optional[ports.Port]:
    """Searches a Port and its attributes

    Args:

    - `node (Node)`: Node object
    - `name (str)`: Name of the port on the node

    Returns:

    - `Optional[Port]`: Port object if found else `None`
    """
    # Refresh node
    node.get()

    try:
        return next(_p for _p in node.ports if _p.name == name)
    except StopIteration:
        return None


# ############## Nodes ###############
def get_nodes(project: projects.Project) -> List[nodes.Node]:
    """Retrieves all GNS3 Project Nodes

    Args:

    - `project (Project)`: Project object

    Returns:

    - `List[Node]`: List of Node objects
    """

    _raw_nodes = project._connector.http_call(
        "get",
        url=f"{project._connector.base_url}/projects/{project.project_id}/nodes",
    ).json()

    return [nodes.Node(connector=project._connector, **_node) for _node in _raw_nodes]


def search_node(
    project: projects.Project,
    name: Optional[str] = None,
    node_id: Optional[str] = None,
) -> Optional[nodes.Node]:
    """Searches for a GNS3 Node if found based a node name.

    Args:

    - `project (Project)`: Project object
    - `name (Optional[str], optional)`: Node name. Defaults to None.
    - `node_id (Optional[str], optional)`: Node ID. Defaults to None.

    Raises:

    - `ValueError`: If name or node ID is not submitted

    Returns:

    - `Optional[Node]`: `Node` if found, else `None`
    """
    # Refresh project
    refresh_project(project, nodes=True)

    try:
        if name is not None:
            return next(_node for _node in project.nodes if _node.name == name)

        elif node_id is not None:
            return next(
                _node for _node in get_nodes(project) if _node.node_id == node_id
            )

        else:
            raise ValueError("Need to submit either name or node_id")
    except StopIteration:
        return None


def create_node(
    project: projects.Project,
    name: str,
    template_name: str,
    x: int = 0,
    y: int = 0,
    **kwargs: Dict[str, Any],
) -> nodes.Node:
    """Creates a GNS3 Node on a project based on given template.

    Args:

    - `project (Project)`: Project object
    - `name (str)`: Name of the node
    - `template_name (str)`: Name of the template of the node
    - `x (int)`: X coordinate to place the node
    - `y (int)`: Y coordinate to place the node
    - `kwargs (Dict[str, Any])`: Keyword attributes of the node to create

    Raises:

    - `ValueError`: If node is already created or if template does not exist

    Returns:

    - `Node`: Node object
    """
    _snode = search_node(project, name=name)

    if _snode:
        raise ValueError(f"Node with same name already exists: {name}")

    _template = search_template(connector=project._connector, name=template_name)
    if not _template:
        raise ValueError(f"Template not found: {template_name}")

    _node = nodes.Node(
        project_id=project.project_id,  # type: ignore
        connector=project._connector,
        name=name,
        template=_template.name,
        template_id=_template.template_id,
        x=x,
        y=y,
        **kwargs,
    )

    _node.create()
    project.nodes.add(_node)
    return _node


def delete_node(
    project: projects.Project, name: Optional[str] = None, node_id: Optional[str] = None
) -> None:
    """Deletes a GNS3 Node in a given project

    Args:

    - `project (Project)`: Project object
    - `name (Optional[str], optional)`: Project name. Defaults to None.
    - `node_id (Optional[str], optional)`: Node ID. Defaults to None.

    Raises:

    - `ValueError`: When neither name nor ID was submitted
    - `ValueError`: When node was not found
    """
    _snode = search_node(project=project, name=name, node_id=node_id)

    if _snode is None:
        raise ValueError("Node not found")

    _snode.delete()
    project.nodes.remove(_snode)


def start_nodes(project: projects.Project, poll_wait_time: int = 5) -> None:
    """Starts all the Nodes from a given project

    Args:

    - `project (Project)`: Projec object
    - `poll_wait_time (int, optional)`: Delay to apply when polling. Defaults to 5.
    """
    _url = f"{project._connector.base_url}/projects/{project.project_id}/nodes/start"

    project._connector.http_call("post", _url)

    time.sleep(poll_wait_time)
    get_nodes(project)


def stop_nodes(project: projects.Project, poll_wait_time: int = 5) -> None:
    """Stops all the Nodes from a given project

    Args:

    - `project (Project)`: Projec object
    - `poll_wait_time (int, optional)`: Delay to apply when polling. Defaults to 5.
    """
    _url = f"{project._connector.base_url}/projects/{project.project_id}/nodes/stop"

    project._connector.http_call("post", _url)

    time.sleep(poll_wait_time)
    get_nodes(project)


def reload_nodes(project: projects.Project, poll_wait_time: int = 5) -> None:
    """Reloads all the Nodes from a given project

    Args:

    - `project (Project)`: Projec object
    - `poll_wait_time (int, optional)`: Delay to apply when polling. Defaults to 5.
    """
    _url = f"{project._connector.base_url}/projects/{project.project_id}/nodes/reload"

    project._connector.http_call("post", _url)

    time.sleep(poll_wait_time)
    get_nodes(project)


def suspend_nodes(project: projects.Project, poll_wait_time: int = 5) -> None:
    """Suspends all the Nodes from a given project

    Args:

    - `project (Project)`: Projec object
    - `poll_wait_time (int, optional)`: Delay to apply when polling. Defaults to 5.
    """
    _url = f"{project._connector.base_url}/projects/{project.project_id}/nodes/suspend"

    project._connector.http_call("post", _url)

    time.sleep(poll_wait_time)
    get_nodes(project)


def nodes_summary(project: projects.Project) -> List[Any]:
    """Returns a summary of the nodes inside of a given project.

    Args:

    - `project_id`
    - `connector`

    Returns:

    - `List[Any]`: List of tuples node name, status, console and node_id

    `[(node_name, node_status, node_console, node_id) ...]`
    """
    # Refresh project
    refresh_project(project, nodes=True)

    return [(_n.name, _n.status, _n.console, _n.node_id) for _n in project.nodes]


def get_nodes_inventory(project: projects.Project) -> Dict[str, Any]:
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
    refresh_project(project, nodes=True)

    _nodes_inventory = {}
    _server = urlparse(project._connector.base_url).hostname

    for _n in project.nodes:

        _nodes_inventory.update(
            {
                _n.name: {
                    "server": _server,
                    "name": _n.name,
                    "console_port": _n.console,
                    "console_type": _n.console_type,
                    "type": _n.node_type,
                    "template": _n.template,
                }
            }
        )

    return _nodes_inventory


def arrange_nodes_circular(project: projects.Project, radius: int = 120) -> None:
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
    refresh_project(project, nodes=True)

    if project.status != "opened":
        project.open()

    _angle = (2 * pi) / len(project.nodes)
    # The Y Axis is inverted in GNS3, so the -Y is UP
    for index, n in enumerate(project.nodes):
        _x = int(radius * (sin(_angle * index)))
        _y = int(radius * (-cos(_angle * index)))
        n.update(x=_x, y=_y)


# ############## Templates ###############
def get_templates(connector: connector.Connector) -> List[templates.Template]:
    """Retrieves all GNS3 Node Templates

    Args:

    - `connector (Connector)`: GNS3 connector object

    Returns:

    - `List[Template]`: List of Template objects
    """
    _raw_templates = connector.http_call(
        "get", url=f"{connector.base_url}/templates"
    ).json()

    return [
        templates.Template(connector=connector, **_template)
        for _template in _raw_templates
    ]


def search_template(
    connector: connector.Connector,
    name: Optional[str] = None,
    template_id: Optional[str] = None,
) -> Optional[templates.Template]:
    """Searches for GNS3 Template from a given template name or ID

    Args:

    - `connector (Connector)`: GNS3 connector object
    - `name (Optional[str], optional)`: Template name. Defaults to None.
    - `template_id (Optional[str], optional)`: Template ID. Defaults to None.

    Raises:

    - `ValueError`: If name or template ID is not submitted

    Returns:

    - `Optional[Template]`: `Template` if found, else `None`
    """
    try:
        if name is not None:
            return next(tplt for tplt in get_templates(connector) if tplt.name == name)

        elif template_id is not None:
            return next(
                tp for tp in get_templates(connector) if tp.template_id == template_id
            )

        else:
            raise ValueError("Need to submit either name or template_id")
    except StopIteration:
        return None


def create_template(
    connector: connector.Connector, name: str, **kwargs: Dict[str, Any]
) -> templates.Template:
    """Creates a GNS3 Template

    Args:

    - `connector (Connector)`: GNS3 connector object
    - `name (str)`: Name of the template
    - `kwargs (Dict[str, Any])`: Keyword attributes of the template to create

    Raises:

    - `ValueError`: If template already exists

    Returns:

    - `Template`: Template object
    """
    _stemplate = search_template(connector, name=name)

    if _stemplate:
        raise ValueError(f"Template with same name already exists: {name}")

    _template = templates.Template(connector=connector, name=name, **kwargs)

    _template.create()
    return _template


def delete_template(
    connector: connector.Connector,
    name: Optional[str] = None,
    template_id: Optional[str] = None,
) -> None:
    """Deletes a GNS3 Template

    Args:

    - `connector (Connector)`: GNS3 connector object
    - `name (Optional[str], optional)`: Template name. Defaults to None.
    - `template_id (Optional[str], optional)`: Template ID. Defaults to None.

    Raises:

    - `ValueError`: If name or template ID is not submitted
    - `ValueError`: If template is not found
    """
    _stemplate = search_template(
        connector=connector, name=name, template_id=template_id
    )

    if _stemplate is None:
        raise ValueError("Template not found")

    _stemplate.delete()


# ############## Links ###############
def get_links(project: projects.Project) -> List[links.Link]:
    """Retrieves all GNS3 Project Links

    Args:

    - `project (Project)`: Project object

    Returns:

    - `List[Link]`: List of Link objects
    """

    _raw_links = project._connector.http_call(
        "get",
        url=f"{project._connector.base_url}/projects/{project.project_id}/links",
    ).json()

    for _link in _raw_links:
        if _link["nodes"]:
            _link["nodes"] = [ports.Port(**_port) for _port in _link["nodes"]]

    return [links.Link(connector=project._connector, **_link) for _link in _raw_links]


def _link_nodes_and_ports(
    project: projects.Project, node_a: str, port_a: str, node_b: str, port_b: str
) -> Tuple[nodes.Node, ports.Port, nodes.Node, ports.Port]:
    """Generates Nodes and Ports objects if they exist in the project

    Args:

    - `project (Project)`: Project object
    - `node_a (str)`: Endpoint A node name
    - `port_a (str)`: Endpoint A port name
    - `node_b (str)`: Endpoint B node name
    - `port_b (str)`: Endpoint B port name

    Raises:

    - `ValueError`: If port or node is not found

    Returns:

    - `Tuple[Node, Dict[str, Any], Node, Dict[str, Any]]`: Tuple of the endpoints in the
    form of Node and port attributes
    """

    _node_a = search_node(project, node_a)
    if not _node_a:
        raise ValueError(f"node_a: {node_a} not found")

    _port_a = search_port(_node_a, port_a)
    if not _port_a:
        raise ValueError(f"port_a: {port_a} not found")

    _node_b = search_node(project, node_b)
    if not _node_b:
        raise ValueError(f"node_b: {node_b} not found")

    _port_b = search_port(_node_b, port_b)
    if not _port_b:
        raise ValueError(f"port_b: {port_b} not found")

    return (_node_a, _port_a, _node_b, _port_b)


def _search_link(
    project: projects.Project,
    node_a: nodes.Node,
    port_a: ports.Port,
    node_b: nodes.Node,
    port_b: ports.Port,
) -> Optional[links.Link]:
    """Returns a Link if found given a pair of Node and port attributes. For example
    of how port attribute data looks like see in the API documentation.

    Args:

    - `project (Project)`: Project object
    - `node_a (Node)`: Node object
    - `port_a (Port)`: GNS3 port data
    - `node_b (Node)`: [description]
    - `port_b (Port)`: [description]

    Example of port data:

    ```python
    >>> port_a
    {
        "adapter_number": 0,
        "data_link_types": {
            "Ethernet": "DLT_EN10MB"
        },
        "link_type": "ethernet",
        "name": "Ethernet0",
        "port_number": 0,
        "short_name": "e0"
    }
    ```

    Returns:

    - `Optional[Link]`: `Link` if found, else `None`
    """
    _matches = []
    for _l in project.links:
        if not _l.nodes:
            continue
        if (
            _l.nodes[0].node_id == node_a.node_id
            and _l.nodes[0].adapter_number == port_a.adapter_number
            and _l.nodes[0].port_number == port_a.port_number
            and _l.nodes[1].node_id == node_b.node_id
            and _l.nodes[1].adapter_number == port_b.adapter_number
            and _l.nodes[1].port_number == port_b.port_number
        ):
            _matches.append(_l)
        elif (
            _l.nodes[1].node_id == node_a.node_id
            and _l.nodes[1].adapter_number == port_a.adapter_number
            and _l.nodes[1].port_number == port_a.port_number
            and _l.nodes[0].node_id == node_b.node_id
            and _l.nodes[0].adapter_number == port_b.adapter_number
            and _l.nodes[0].port_number == port_b.port_number
        ):
            _matches.append(_l)
    try:
        return _matches[0]
    except IndexError:
        return None


def search_link(
    project: projects.Project, node_a: str, port_a: str, node_b: str, port_b: str
) -> Optional[links.Link]:
    """Searches for a GNS3 Link of a given project and set of endpoints of nodes and
    ports.

    Args:

    - `project (Project)`: Project object
    - `node_a (str)`: Endpoint A node name
    - `port_a (str)`: Endpoint A port name
    - `node_b (str)`: Endpoint B node name
    - `port_b (str)`: Endpoint B port name

    Raises:

    - `ValueError`: If port or node is not found

    Returns:

    - `Optional[Link]`: `Link` if found, else `None`
    """
    # Refresh project
    refresh_project(project, links=True)

    _node_a, _port_a, _node_b, _port_b = _link_nodes_and_ports(
        project, node_a, port_a, node_b, port_b
    )

    return _search_link(project, _node_a, _port_a, _node_b, _port_b)


def create_link(
    project: projects.Project, node_a: str, port_a: str, node_b: str, port_b: str
) -> links.Link:
    """Creates a GNS3 Link between 2 nodes in a given project

    Args:

    - `project (Project)`: Project object
    - `node_a (str)`: Endpoint A node name
    - `port_a (str)`: Endpoint A port name
    - `node_b (str)`: Endpoint B node name
    - `port_b (str)`: Endpoint B port name

    Raises:

    - `ValueError`: If port or node is not found

    Returns:

    - `Link`: Link object
    """
    # Refresh project
    refresh_project(project)

    _node_a, _port_a, _node_b, _port_b = _link_nodes_and_ports(
        project, node_a, port_a, node_b, port_b
    )

    _slink = _search_link(project, _node_a, _port_a, _node_b, _port_b)

    if _slink:
        raise ValueError(f"At least one port is used, ID: {_slink.link_id}")

    # Now create the link!
    _link = links.Link(
        project_id=project.project_id,  # type: ignore
        connector=project._connector,
        nodes=[
            dict(
                node_id=_node_a.node_id,
                adapter_number=_port_a.adapter_number,
                port_number=_port_a.port_number,
                label=dict(
                    text=_port_a.name,
                ),
            ),
            dict(
                node_id=_node_b.node_id,
                adapter_number=_port_b.adapter_number,
                port_number=_port_b.port_number,
                label=dict(
                    text=_port_b.name,
                ),
            ),
        ],
    )

    _link.create()
    project.links.add(_link)
    return _link


def delete_link(
    project: projects.Project, node_a: str, port_a: str, node_b: str, port_b: str
) -> None:
    """Deletes a GNS3 Link between 2 nodes in a given project

    Args:

    - `project (Project)`: Project object
    - `node_a (str)`: Endpoint A node name
    - `port_a (str)`: Endpoint A port name
    - `node_b (str)`: Endpoint B node name
    - `port_b (str)`: Endpoint B port name

    Raises:

    - `ValueError`: If port is not found
    """
    _link = search_link(project, node_a, port_a, node_b, port_b)

    if _link is None:
        return None

    _link.delete()
    project.links.remove(_link)


def links_summary(project: projects.Project) -> List[Any]:
    """Returns a summary of the links inside the Project.

    Args:

    - `project (Project)`: Project object

    Returns:

    - `List[Any]`: List of tuples nodes and enpoints of each link. For example:

    `[(node_a, port_a, node_b, port_b) ...]`
    """
    refresh_project(project, nodes=True, links=True)

    _links_summary = []
    for _l in project.links:
        if not _l.nodes:
            continue
        _side_a = _l.nodes[0]
        _side_b = _l.nodes[1]
        _node_a = [x for x in project.nodes if x.node_id == _side_a.node_id][0]
        _port_a = [
            x.name
            for x in _node_a.ports
            if x.port_number == _side_a.port_number
            and x.adapter_number == _side_a.adapter_number
        ][0]
        _node_b = [x for x in project.nodes if x.node_id == _side_b.node_id][0]
        _port_b = [
            x.name
            for x in _node_b.ports
            if x.port_number == _side_b.port_number
            and x.adapter_number == _side_b.adapter_number
        ][0]

        _links_summary.append((_node_a.name, _port_a, _node_b.name, _port_b))

    return _links_summary


# ############## Snapshots ###############
def get_snapshots(project: projects.Project) -> List[snapshots.Snapshot]:
    """Retrieves all GNS3 Project Snapshots

    Args:

    - `project (Project)`: Project object

    Returns:

    - `List[Snapshot]`: List of Snapshot objects
    """

    _raw_snapshots = project._connector.http_call(
        "get",
        url=f"{project._connector.base_url}/projects/{project.project_id}/snapshots",
    ).json()

    return [
        snapshots.Snapshot(connector=project._connector, **_snapshot)
        for _snapshot in _raw_snapshots
    ]


def search_snapshot(
    project: projects.Project, value: str, type: str = "name"
) -> Optional[snapshots.Snapshot]:
    """Searches for GNS3 Snapshot from a given snapshot name or ID

    Args:

    - `project (Project)`: Project object
    - `value (str)`: Snapshot name of ID
    - `type (str)`: Type of attribute. `name` or `snapshot_id`

    Returns:

    - `Optional[Snapshot]`: `Snapshot` if found, else `None`
    """
    # Refresh project
    refresh_project(project, snapshots=True)

    try:
        if type == "name":
            return next(snap for snap in get_snapshots(project) if snap.name == value)
        elif type == "snapshot_id":
            return next(
                snap for snap in get_snapshots(project) if snap.snapshot_id == value
            )
        return None
    except StopIteration:
        return None


def create_snapshot(project: projects.Project, name: str) -> snapshots.Snapshot:
    """Creates a GNS3 Project Snapshot

    Args:

    - `project (Project)`: Project object
    - `name (str)`: Snapshot name

    Raises:

    - `ValueError`: If snapshot is already created

    Returns:

    - `Snapshot`: Snapshot object
    """

    _ssnapshot = search_snapshot(project, name)

    if _ssnapshot:
        raise ValueError(f"Snapshot with same name already exists: {_ssnapshot}")

    _snapshot = snapshots.Snapshot(
        connector=project._connector, project_id=project.project_id, name=name
    )

    _snapshot.create()
    project.snapshots.add(_snapshot)
    return _snapshot


def delete_snapshot(
    project: projects.Project,
    name: Optional[str] = None,
    snapshot_id: Optional[str] = None,
) -> None:
    """Deletes GNS3 Project Snapshot

    Args:

    - `project (Project)`: Project object
    - `name (Optional[str], optional)`: Snapshot name. Defaults to None.
    - `snapshot_id (Optional[str], optional)`: Snapshot ID. Defaults to None.

    Raises:

    - `ValueError`: When neither name nor ID was submitted
    - `ValueError`: When snapshot was not found
    """

    if name is not None:
        _ssnapshot = search_snapshot(project, name)
    elif snapshot_id is not None:
        _ssnapshot = search_snapshot(project, snapshot_id, type="snapshot_id")
    else:
        raise ValueError("Need to submit either name or snapshot_id")

    if _ssnapshot is None:
        raise ValueError("Snapshot not found")

    _ssnapshot.delete()
    project.snapshots.remove(_ssnapshot)


def restore_snapshot(
    project: projects.Project,
    name: Optional[str] = None,
    snapshot_id: Optional[str] = None,
) -> bool:
    """Restores a GNS3 Project Snapshot given a snapshot name or ID.

    Args:

    - `project (Project)`: Project object
    - `name (Optional[str])`: Snapshot name
    - `snapshot_id (Optional[str], optional)`: Snapshot ID. Defaults to None.

    Returns:

    - `bool`: True when snapshot has been restored

    Raises:

    - `ValueError`: When neither name nor ID was submitted
    """

    if name is not None:
        _snapshot = search_snapshot(project, name)
    elif snapshot_id is not None:
        _snapshot = search_snapshot(project, snapshot_id, type="snapshot_id")
    else:
        raise ValueError("Need to submit either name or snapshot_id")

    _url = (
        f"{project._connector.base_url}/projects/{project.project_id}/"
        f"snapshots/{_snapshot.snapshot_id}/restore"
    )
    _response = project._connector.http_call("post", _url)

    if _response.status_code == 201:
        return True
    else:
        return False
