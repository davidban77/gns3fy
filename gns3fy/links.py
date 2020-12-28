"""Module for python GNS3 Link entity and useful link related services
"""
from pydantic.fields import Field
from .connector import Connector
from .nodes import Node, Port, search_node, search_port
from .projects import Project
from typing import TypeVar, Callable, Any, List, Optional, Tuple
from enum import Enum
from functools import wraps
from pydantic import BaseModel, PrivateAttr


_TFUNC = TypeVar("_TFUNC", bound=Callable[..., Any])


def verify_attributes(_func: Optional[Any] = None, attrs: List[str] = ["_connector"]):
    """
    Main checker for connector object and respective object's ID for their retrieval
    or actions methods.
    """

    def decorator_verify_attributes(func: _TFUNC) -> _TFUNC:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            for attr in attrs:
                if getattr(self, attr) is None:
                    raise ValueError(f"Parameter is not set: {attr}")
            return func(self, *args, **kwargs)

        return wrapper  # type: ignore

    if _func is None:
        return decorator_verify_attributes
    else:
        return decorator_verify_attributes(_func)


class LinkType(Enum):
    ethernet = "ethernet"
    serial = "serial"


class Link(BaseModel):
    """
    GNS3 Link API object. For more information visit: [Links Endpoint API information](
    https://gns3-server.readthedocs.io/en/2.2/api/v2/controller/link.html)

    **Attributes:**

    - `link_id` (str): Link UUID (**required** to be set when using `get` method)
    - `link_type` (enum): Possible values: ethernet, serial
    - `project_id` (str): Project UUID (**required**)
    - `connector` (object): `Connector` instance used for interaction (**required**)
    - `suspend` (bool): Suspend the link
    - `nodes` (list): List of the Nodes and ports (**required** when using `create`
    method, see Features/Link creation on the docs)
    - `filters` (dict): Packet filter. This allow to simulate latency and errors
    - `capturing` (bool): Read only property. True if a capture running on the link
    - `capture_file_path` (str): Read only property. The full path of the capture file
    if capture is running
    - `capture_file_name` (str): Read only property. The name of the capture file if
    capture is running

    **Returns:**

    `Link` instance

    **Example:**

    ```python
    >>> link = Link(project_id=<pr_id>, link_id=<link_id> connector=<Connector
    instance>)
    >>> link.get()
    >>> print(link.link_type)
    'ethernet'
    ```
    """

    project_id: str
    _connector: Connector = PrivateAttr()
    link_id: Optional[str] = None
    link_type: Optional[LinkType] = None
    suspend: Optional[bool] = None
    filters: Optional[Any] = None
    capturing: Optional[bool] = None
    capture_file_path: Optional[str] = None
    capture_file_name: Optional[str] = None
    capture_compute_id: Optional[str] = None
    nodes: List[Port] = Field(default_factory=list)

    class Config:
        validate_assignment = True
        extra = "ignore"

    def __init__(
        self,
        project_id: str,
        connector: Connector,
        link_id: Optional[str] = None,
        **data: Any,
    ) -> None:
        super().__init__(project_id=project_id, link_id=link_id, **data)
        self._connector = connector

    def _update(self, data_dict) -> None:
        # Attributes are validated on assignment
        for k, v in data_dict.items():
            setattr(self, k, v)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Link):
            return False
        if self.link_id is None:
            raise ValueError("No link_id present. Need to initialize first")
        return other.link_id == self.link_id

    def __hash__(self) -> int:
        if self.link_id is None:
            raise ValueError("No link_id present. Need to initialize first")
        return hash(self.link_id)

    @verify_attributes(attrs=["project_id", "_connector", "link_id"])
    def get(self) -> None:
        """
        Retrieves the information from the link endpoint.

        **Required Attributes:**

        - `project_id`
        - `connector`
        - `link_id`
        """
        _url = (
            f"{self._connector.base_url}/projects/"
            f"{self.project_id}/links/{self.link_id}"
        )
        _response = self._connector.http_call("get", _url)

        # Update object
        _data = _response.json()
        if _data["nodes"]:
            _data["nodes"] = [Port(**_port) for _port in _data["nodes"]]
        self._update(_response.json())

    @verify_attributes(attrs=["project_id", "_connector", "link_id"])
    def delete(self) -> None:
        """
        Deletes a link endpoint from the project. It sets to `None` the attributes
        `link_id` when executed sucessfully

        **Required Attributes:**

        - `project_id`
        - `connector`
        - `link_id`
        """
        _url = (
            f"{self._connector.base_url}/projects/"
            f"{self.project_id}/links/{self.link_id}"
        )

        self._connector.http_call("delete", _url)

    @verify_attributes(attrs=["project_id", "_connector", "nodes"])
    def create(self) -> None:
        """
        Creates a link endpoint

        **Required Attributes:**

        - `project_id`
        - `connector`
        - `nodes`
        """
        _url = f"{self._connector.base_url}/projects/{self.project_id}/links"

        data = {
            k: v
            for k, v in self.dict().items()
            if k not in ("_connector", "__initialised__")
            if v is not None
        }

        _response = self._connector.http_call("post", _url, json_data=data)

        # Now update it
        self._update(_response.json())


def get_links(project: Project) -> List[Link]:
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
            _link["nodes"] = [Port(**_port) for _port in _link["nodes"]]

    return [Link(connector=project._connector, **_link) for _link in _raw_links]


def _link_nodes_and_ports(
    project: Project, node_a: str, port_a: str, node_b: str, port_b: str
) -> Tuple[Node, Port, Node, Port]:
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
    project: Project,
    node_a: Node,
    port_a: Port,
    node_b: Node,
    port_b: Port,
) -> Optional[Link]:
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
    project: Project, node_a: str, port_a: str, node_b: str, port_b: str
) -> Optional[Link]:
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
    project.get(links=True)

    _node_a, _port_a, _node_b, _port_b = _link_nodes_and_ports(
        project, node_a, port_a, node_b, port_b
    )

    return _search_link(project, _node_a, _port_a, _node_b, _port_b)


def create_link(
    project: Project, node_a: str, port_a: str, node_b: str, port_b: str
) -> Link:
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
    project.get()

    _node_a, _port_a, _node_b, _port_b = _link_nodes_and_ports(
        project, node_a, port_a, node_b, port_b
    )

    _slink = _search_link(project, _node_a, _port_a, _node_b, _port_b)

    if _slink:
        raise ValueError(f"At least one port is used, ID: {_slink.link_id}")

    # Now create the link!
    _link = Link(
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
    project: Project, node_a: str, port_a: str, node_b: str, port_b: str
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


def links_summary(project: Project) -> List[Any]:
    """Returns a summary of the links inside the Project.

    Args:

    - `project (Project)`: Project object

    Returns:

    - `List[Any]`: List of tuples nodes and enpoints of each link. For example:

    `[(node_a, port_a, node_b, port_b) ...]`
    """
    project.get(links=True, nodes=True)

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
