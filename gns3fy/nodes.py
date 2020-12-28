"""Module for python GNS3 Node entity and useful node related services
"""
import time
from .connector import Connector
from .links import Link
from .templates import search_template
from .projects import Project
from enum import Enum
from typing import Optional, Any, TypeVar, Callable, List, Dict, Set
from functools import wraps
from pydantic import BaseModel, PrivateAttr, Field
from urllib.parse import urlparse
from math import pi, sin, cos


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


class Port(BaseModel):
    name: Optional[str] = None
    node_id: Optional[str] = None
    short_name: Optional[str] = None
    adapter_number: Optional[int] = None
    label: Optional[Dict[str, str]] = None
    port_number: Optional[int] = None
    link_type: Optional[str] = None
    data_link_types: Optional[Dict[str, Any]] = None


class NodeType(Enum):
    cloud = "cloud"
    nat = "nat"
    ethernet_hub = "ethernet_hub"
    ethernet_switch = "ethernet_switch"
    frame_relay_switch = "frame_relay_switch"
    atm_switch = "atm_switch"
    docker = "docker"
    dynamips = "dynamips"
    vpcs = "vpcs"
    traceng = "traceng"
    virtualbox = "virtualbox"
    vmware = "vmware"
    iou = "iou"
    qemu = "qemu"


class ConsoleType(Enum):
    vnc = "vnc"
    telnet = "telnet"
    http = "http"
    https = "https"
    spice = "spice"
    none = "none"
    null = "null"


class NodeStatus(Enum):
    stopped = "stopped"
    started = "started"
    suspended = "suspended"


class Node(BaseModel):
    """
    GNS3 Node API object. For more information visit: [Node Endpoint API information](
    https://gns3-server.readthedocs.io/en/2.2/api/v2/controller/node.html)

    **Attributes:**

    - `name` (str): Node name (**required** when using `create` method)
    - `project_id` (str): Project UUID (**required**)
    - `node_id` (str): Node UUID (**required** when using `get` method)
    - `compute_id` (str): Compute identifier (**required**, default=local)
    - `node_type` (enum): frame_relay_switch, atm_switch, docker, dynamips, vpcs,
    traceng, virtualbox, vmware, iou, qemu (**required** when using `create` method)
    - `connector` (object): `Connector` instance used for interaction (**required**)
    - `template_id`: Template UUID from the which the node is from.
    - `template`: Template name from the which the node is from.
    - `node_directory` (str): Working directory of the node. Read only
    - `status` (enum): Possible values: stopped, started, suspended
    - `ports` (list): List of node ports, READ only
    - `port_name_format` (str): Formating for port name {0} will be replace by port
    number
    - `port_segment_size` (int): Size of the port segment
    - `first_port_name` (str): Name of the first port
    - `properties` (dict): Properties specific to an emulator
    - `locked` (bool): Whether the element locked or not
    - `label` (dict): TBC
    - `console` (int): Console TCP port
    - `console_host` (str): Console host
    - `console_auto_start` (bool): Automatically start the console when the node has
    started
    - `command_line` (str): Command line use to start the node
    - `custom_adapters` (list): TBC
    - `height` (int): Height of the node, READ only
    - `width` (int): Width of the node, READ only
    - `symbol` (str): Symbol of the node
    - `x` (int): X position of the node
    - `y` (int): Y position of the node
    - `z (int): Z position of the node

    **Returns:**

    `Node` instance

    **Example:**

    ```python
    >>> alpine = Node(name="alpine1", node_type="docker", template="alpine",
    project_id=<pr_id>, connector=<Connector instance>)
    >>> alpine.create()
    >>> print(alpine.node_id)
    'SOME-UUID-GENERATED'
    ```
    """

    project_id: str
    _connector: Connector = PrivateAttr()

    name: Optional[str] = None
    node_id: Optional[str] = None
    compute_id: str = "local"
    node_type: Optional[NodeType] = None
    node_directory: Optional[str] = None
    status: Optional[NodeStatus] = None
    port_name_format: Optional[str] = None
    port_segment_size: Optional[int] = None
    first_port_name: Optional[str] = None
    locked: Optional[bool] = None
    label: Optional[Any] = None
    console: Optional[int] = None
    console_host: Optional[str] = None
    console_type: Optional[ConsoleType] = None
    console_auto_start: Optional[bool] = None
    command_line: Optional[str] = None
    custom_adapters: Optional[List[Any]] = None
    height: Optional[int] = None
    width: Optional[int] = None
    symbol: Optional[str] = None
    x: int = 0
    y: int = 0
    z: int = 0
    template_id: Optional[str] = None
    properties: Optional[Any] = None

    template: Optional[str] = None
    ports: List[Port] = Field(default_factory=list)
    links: Set[Link] = Field(default_factory=set)

    class Config:
        validate_assignment = True
        extra = "ignore"

    def __init__(
        self,
        project_id: str,
        connector: Connector,
        name: Optional[str] = None,
        node_id: Optional[str] = None,
        **data: Any,
    ) -> None:
        super().__init__(project_id=project_id, name=name, node_id=node_id, **data)
        self._connector = connector

    def _update(self, data_dict) -> None:
        # Attributes are validated on assignment
        for k, v in data_dict.items():
            setattr(self, k, v)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Node):
            return False
        if self.node_id is None:
            raise ValueError("No node_id present. Need to initialize first")
        return other.node_id == self.node_id

    def __hash__(self) -> int:
        if self.node_id is None:
            raise ValueError("No node_id present. Need to initialize first")
        return hash(self.node_id)

    @verify_attributes(attrs=["project_id", "_connector", "node_id"])
    def get(self, get_links: bool = True) -> None:
        """
        Retrieves the node information. When `get_links` is `True` it also retrieves the
        links respective to the node.

        **Required Attributes:**

        - `project_id`
        - `connector`
        - `node_id` or `name`
        """
        _url = (
            f"{self._connector.base_url}/projects/"
            f"{self.project_id}/nodes/{self.node_id}"
        )
        _response = self._connector.http_call("get", _url)

        # Update object
        _data = _response.json()
        if _data["ports"]:
            _data["ports"] = [Port(**_port) for _port in _data["ports"]]

        self._update(_data)

        if get_links:
            self.get_links()

    @verify_attributes(attrs=["project_id", "_connector", "node_id"])
    def get_links(self) -> None:
        """
        Retrieves the links of the respective node. They will be saved at the `links`
        attribute

        **Required Attributes:**

        - `project_id`
        - `connector`
        - `node_id`
        """

        _url = (
            f"{self._connector.base_url}/projects/{self.project_id}/nodes"
            f"/{self.node_id}/links"
        )
        _response = self._connector.http_call("get", _url)

        # Create the Link array but cleanup cache if there is one
        if self.links:
            self.links.clear()
        for _link in _response.json():
            if _link["nodes"]:
                _link["nodes"] = [Port(**_port) for _port in _link["nodes"]]
            self.links.add(Link(connector=self._connector, **_link))

    @verify_attributes(attrs=["project_id", "_connector", "node_id"])
    def start(self) -> None:
        """
        Starts the node.

        **Required Attributes:**

        - `project_id`
        - `connector`
        - `node_id`
        """
        _url = (
            f"{self._connector.base_url}/projects/{self.project_id}/nodes"
            f"/{self.node_id}/start"
        )
        _response = self._connector.http_call("post", _url)

        # Update object or perform get() if change was not reflected
        if _response.json().get("status") == "started":
            self._update(_response.json())
        else:
            self.get()

    @verify_attributes(attrs=["project_id", "_connector", "node_id"])
    def stop(self) -> None:
        """
        Stops the node.

        **Required Attributes:**

        - `project_id`
        - `connector`
        - `node_id`
        """
        _url = (
            f"{self._connector.base_url}/projects/{self.project_id}/nodes"
            f"/{self.node_id}/stop"
        )
        _response = self._connector.http_call("post", _url)

        # Update object or perform get() if change was not reflected
        if _response.json().get("status") == "stopped":
            self._update(_response.json())
        else:
            self.get()

    @verify_attributes(attrs=["project_id", "_connector", "node_id"])
    def reload(self) -> None:
        """
        Reloads the node.

        **Required Attributes:**

        - `project_id`
        - `connector`
        - `node_id`
        """
        _url = (
            f"{self._connector.base_url}/projects/{self.project_id}/nodes"
            f"/{self.node_id}/reload"
        )
        _response = self._connector.http_call("post", _url)

        # Update object or perform get() if change was not reflected
        if _response.json().get("status") == "started":
            self._update(_response.json())
        else:
            self.get()

    @verify_attributes(attrs=["project_id", "_connector", "node_id"])
    def suspend(self) -> None:
        """
        Suspends the node.

        **Required Attributes:**

        - `project_id`
        - `connector`
        - `node_id`
        """
        _url = (
            f"{self._connector.base_url}/projects/{self.project_id}/nodes"
            f"/{self.node_id}/suspend"
        )
        _response = self._connector.http_call("post", _url)

        # Update object or perform get() if change was not reflected
        if _response.json().get("status") == "suspended":
            self._update(_response.json())
        else:
            self.get()

    @verify_attributes(attrs=["project_id", "_connector", "node_id"])
    def update(self, **kwargs) -> None:
        """
        Updates the node instance by passing the keyword arguments of the attributes
        you want updated

        Example:

        ```python
        router01.update(name="router01-CSX")
        ```

        This will update the node `name` attribute to `"router01-CSX"`

        **Required Attributes:**

        - `project_id`
        - `connector`
        """
        _url = (
            f"{self._connector.base_url}/projects/"
            f"{self.project_id}/nodes/{self.node_id}"
        )

        # TODO: Verify that the passed kwargs are supported ones
        _response = self._connector.http_call("put", _url, json_data=kwargs)

        # Update object
        self._update(_response.json())

    @verify_attributes(attrs=["project_id", "_connector", "template_id", "compute_id"])
    def create(self) -> None:
        """
        Creates a node.

        By default it will fetch the nodes properties for creation based on the
        `template_id` attribute supplied. This can be overriden/updated
        by sending a dictionary of the properties under `extra_properties`.

        Args:

        - `project_id`
        - `connector`
        - `compute_id`: Defaults to "local"
        - `template_id`
        """
        if self.node_id:
            raise ValueError("Node already created")

        cached_data = {
            k: v
            for k, v in self.dict().items()
            if k
            not in (
                "project_id",
                "template",
                "template_id",
                "links",
                "connector",
                "__initialised__",
            )
            if v is not None
        }

        _url = (
            f"{self._connector.base_url}/projects/{self.project_id}/"
            f"templates/{self.template_id}"
        )

        # TODO: To set x, y more dynamic
        _response = self._connector.http_call(
            "post", _url, json_data=dict(x=self.x, y=self.y, compute_id=self.compute_id)
        )

        self._update(_response.json())

        # Update the node attributes based on cached data
        self.update(**cached_data)

    @verify_attributes(attrs=["project_id", "_connector", "node_id"])
    def delete(self) -> None:
        """Deletes the node from the project. It sets to `None` the attributes `node_id`
        and `name` when executed successfully

        Args:

        - `project_id`
        - `connector`
        - `node_id`
        """
        _url = (
            f"{self._connector.base_url}/projects/"
            f"{self.project_id}/nodes/{self.node_id}"
        )

        self._connector.http_call("delete", _url)

    @verify_attributes(attrs=["project_id", "_connector", "node_id"])
    def get_file(self, path: str) -> str:
        """
        Retrieve a file in the node directory.

        **Required Attributes:**

        - `project_id`
        - `connector`
        - `path`: Node's relative path of the file
        """
        _url = (
            f"{self._connector.base_url}/projects/"
            f"{self.project_id}/nodes/{self.node_id}/files/{path}"
        )

        return self._connector.http_call("get", _url).text

    @verify_attributes(attrs=["project_id", "_connector", "node_id"])
    def write_file(self, path: str, data: str) -> None:
        """
        Places a file content on a specified node file path. Used mainly for docker
        images.

        Example to update an alpine docker network interfaces:

        ```python
        >>> data = '''
            auto eth0
            iface eth0 inet dhcp
            '''

        >>> alpine_node.write_file(path='/etc/network/interfaces', data=data)
        ```

        **Required Attributes:**

        - `project_id`
        - `connector`
        - `path`: Node's relative path of the file
        - `data`: Data to be included in the file
        """
        _url = (
            f"{self._connector.base_url}/projects/{self.project_id}/nodes/"
            f"{self.node_id}/files/{path}"
        )

        self._connector.http_call("post", _url, data=data)


def search_port(node: Node, name: str) -> Optional[Port]:
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


def get_nodes(project: Project) -> List[Node]:
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

    return [Node(connector=project._connector, **_node) for _node in _raw_nodes]


def search_node(project: Project, value: str, type: str = "name") -> Optional[Node]:
    """Searches for a GNS3 Node if found based a node name.

    Args:

    - `project (Project)`: Project object
    - `value (str)`: Node name of ID
    - `type (str)`: Type of attribute. `name` or `node_id`

    Returns:

    - `Optional[Node]`: `Node` if found, else `None`
    """
    # Refresh project
    project.get(nodes=True)

    try:
        if type == "name":
            return next(_node for _node in project.nodes if _node.name == value)
        elif type == "node_id":
            return next(_node for _node in get_nodes(project) if _node.node_id == value)
        return None
    except StopIteration:
        return None


def create_node(
    project: Project, name: str, template_name: str, x: int = 0, y: int = 0
) -> Node:
    """Creates a GNS3 Node on a project based on given template.

    Args:

    - `project (Project)`: Project object
    - `name (str)`: Name of the node
    - `template_name (str)`: Name of the template of the node
    - `x (int)`: X coordinate to place the node
    - `y (int)`: Y coordinate to place the node

    Raises:

    - `ValueError`: If node is already created or if template does not exist

    Returns:

    - `Node`: Node object
    """

    _snode = search_node(project, name)

    if _snode:
        raise ValueError(f"Node with same name already exists: {name}")

    _template = search_template(connector=project._connector, value=template_name)
    if not _template:
        raise ValueError(f"Template not found: {template_name}")

    _node = Node(
        project_id=project.project_id,  # type: ignore
        connector=project._connector,
        name=name,
        template=_template.name,
        template_id=_template.template_id,
        x=x,
        y=y,
    )

    _node.create()
    project.nodes.add(_node)
    return _node


def delete_node(
    project: Project, name: Optional[str] = None, node_id: Optional[str] = None
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

    if name is not None:
        _snode = search_node(project, name)
    elif node_id is not None:
        _snode = search_node(project, node_id, type="node_id")
    else:
        raise ValueError("Need to submit either name or node_id")

    if _snode is None:
        raise ValueError("Node not found")

    _snode.delete()
    project.nodes.remove(_snode)


def start_nodes(project: Project, poll_wait_time: int = 5) -> None:
    """Starts all the Nodes from a given project

    Args:

    - `project (Project)`: Projec object
    - `poll_wait_time (int, optional)`: Delay to apply when polling. Defaults to 5.
    """
    _url = f"{project._connector.base_url}/projects/{project.project_id}/nodes/start"

    project._connector.http_call("post", _url)

    time.sleep(poll_wait_time)
    get_nodes(project)


def stop_nodes(project: Project, poll_wait_time: int = 5) -> None:
    """Stops all the Nodes from a given project

    Args:

    - `project (Project)`: Projec object
    - `poll_wait_time (int, optional)`: Delay to apply when polling. Defaults to 5.
    """
    _url = f"{project._connector.base_url}/projects/{project.project_id}/nodes/stop"

    project._connector.http_call("post", _url)

    time.sleep(poll_wait_time)
    get_nodes(project)


def reload_nodes(project: Project, poll_wait_time: int = 5) -> None:
    """Reloads all the Nodes from a given project

    Args:

    - `project (Project)`: Projec object
    - `poll_wait_time (int, optional)`: Delay to apply when polling. Defaults to 5.
    """
    _url = f"{project._connector.base_url}/projects/{project.project_id}/nodes/reload"

    project._connector.http_call("post", _url)

    time.sleep(poll_wait_time)
    get_nodes(project)


def suspend_nodes(project: Project, poll_wait_time: int = 5) -> None:
    """Suspends all the Nodes from a given project

    Args:

    - `project (Project)`: Projec object
    - `poll_wait_time (int, optional)`: Delay to apply when polling. Defaults to 5.
    """
    _url = f"{project._connector.base_url}/projects/{project.project_id}/nodes/suspend"

    project._connector.http_call("post", _url)

    time.sleep(poll_wait_time)
    get_nodes(project)


def nodes_summary(project: Project) -> List[Any]:
    """Returns a summary of the nodes inside of a given project.

    Args:

    - `project_id`
    - `connector`

    Returns:

    - `List[Any]`: List of tuples node name, status, console and node_id

    `[(node_name, node_status, node_console, node_id) ...]`
    """
    # Refresh project
    project.get(nodes=True)

    return [(_n.name, _n.status, _n.console, _n.node_id) for _n in project.nodes]


def get_nodes_inventory(project: Project) -> Dict[str, Any]:
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
    project.get(nodes=True)

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
    project.get(nodes=True)

    if project.status != "opened":
        project.open()

    _angle = (2 * pi) / len(project.nodes)
    # The Y Axis is inverted in GNS3, so the -Y is UP
    for index, n in enumerate(project.nodes):
        _x = int(radius * (sin(_angle * index)))
        _y = int(radius * (-cos(_angle * index)))
        n.update(x=_x, y=_y)
