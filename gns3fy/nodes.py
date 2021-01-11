"""Model for python GNS3 Node entity and useful node related services
"""
from .connector import Connector
from .links import Link
from .ports import Port, gen_port_from_links
from .base import verify_attributes, BaseResourceModel
from typing import Optional, Any, List, Dict
from pydantic import PrivateAttr, Field, validator


NODE_TYPES = [
    "cloud",
    "nat",
    "ethernet_hub",
    "ethernet_switch",
    "frame_relay_switch",
    "atm_switch",
    "docker",
    "dynamips",
    "vpcs",
    "traceng",
    "virtualbox",
    "vmware",
    "iou",
    "qemu",
]


CONSOLE_TYPES = [
    "vnc",
    "telnet",
    "http",
    "https",
    "spice",
    "spice+agent",
    "none",
    "null",
]


NODE_STATUS = ["stopped", "started", "suspended"]


class Node(BaseResourceModel):
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

    # name: Optional[str] = None
    name: str
    node_id: str
    compute_id: Optional[str] = "local"
    node_type: Optional[str] = None
    node_directory: Optional[str] = None
    status: Optional[str] = None
    port_name_format: Optional[str] = None
    port_segment_size: Optional[int] = None
    first_port_name: Optional[str] = None
    locked: Optional[bool] = None
    label: Optional[Any] = None
    console: Optional[int] = None
    console_host: Optional[str] = None
    console_type: Optional[str] = None
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
    ports: List[Port] = Field(default_factory=list)

    template: Optional[str] = None
    # links: Set[Link] = Field(default_factory=set)
    links: Dict[str, Link] = Field(default_factory=dict)

    @validator("node_type")
    def valid_node_type(cls, v):
        if not any(x for x in NODE_TYPES if x == v):
            raise ValueError("Not a valid GNS3 Node type")
        return v

    @validator("status")
    def valid_status(cls, v):
        if not any(x for x in NODE_STATUS if x == v):
            raise ValueError("Not a valid GNS3 Node status")
        return v

    @validator("console_type")
    def valid_console_type(cls, v):
        if not any(x for x in CONSOLE_TYPES if x == v):
            if v is not None:
                raise ValueError("Not a valid GNS3 Console type")
        return v

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

    def _resolve_ports_nodes(self) -> None:
        for _p in self.ports:
            _p.node_name = self.name
            _p.node_id = self.node_id

    def _resolve_template(self):
        _url = f"{self._connector.base_url}/templates/{self.template_id}"
        _response = self._connector.http_call("get", _url)
        self.template = _response.json()["name"]

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
            _data["ports"] = [
                Port(node_name=self.name, node_id=self.node_id, **_port)
                for _port in _data["ports"]
            ]

        self._update(_data)

        if get_links:
            self.get_links()

        if self.template is None:
            self._resolve_template()
        if self.ports:
            self._resolve_ports_nodes()

    @verify_attributes(attrs=["project_id", "_connector", "node_id"])
    def get_port(self, name: str) -> Optional[Port]:
        """Searches a Port and its attributes

        Args:

        - `node (Node)`: Node object
        - `name (str)`: Name of the port on the node

        Returns:

        - `Optional[Port]`: Port object if found else `None`
        """
        # Refresh node
        self.get()

        try:
            return next(_p for _p in self.ports if _p.name == name)
        except StopIteration:
            return None

    @verify_attributes(attrs=["project_id", "_connector", "node_id"])
    def get_links(self, resolve_node: bool = True) -> None:
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
                _link["nodes"] = gen_port_from_links(
                    connector=self._connector,
                    project_id=self.project_id,
                    port_data=_link["nodes"],
                    resolve_node=resolve_node,
                )
            link = Link(connector=self._connector, **_link)
            link.name = link._gen_name()
            self.links.update({link.name: link})

    @verify_attributes(attrs=["project_id", "_connector", "node_id"])
    def start(self) -> bool:
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
        if _response.status_code == 200:
            self._update(_response.json())
            self._resolve_ports_nodes()
            return True
        else:
            return False

    @verify_attributes(attrs=["project_id", "_connector", "node_id"])
    def stop(self) -> bool:
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
        if _response.status_code == 200:
            self._update(_response.json())
            self._resolve_ports_nodes()
            return True
        else:
            return False

    @verify_attributes(attrs=["project_id", "_connector", "node_id"])
    def reload(self) -> bool:
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
        if _response.status_code == 200:
            self._update(_response.json())
            self._resolve_ports_nodes()
            return True
        else:
            return False

    @verify_attributes(attrs=["project_id", "_connector", "node_id"])
    def suspend(self) -> bool:
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
        if _response.status_code == 200:
            self._update(_response.json())
            self._resolve_ports_nodes()
            return True
        else:
            return False

    @verify_attributes(attrs=["project_id", "_connector", "node_id"])
    def update(self, **kwargs) -> bool:
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

        data = {k: v for k, v in kwargs.items() if k not in ("template", "links")}

        _response = self._connector.http_call("put", _url, json_data=data)

        # Update object
        if _response.status_code == 200:
            self._update(_response.json())
            self._resolve_ports_nodes()
            return True
        else:
            return False

    @verify_attributes(attrs=["project_id", "_connector", "node_id"])
    def delete(self) -> bool:
        """Deletes the node from the project. It sets to `None` theattributes`node_id`
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

        _response = self._connector.http_call("delete", _url)

        if _response.status_code == 204:
            return True
        else:
            return False

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


def get_nodes(connector: Connector, project_id: str) -> List[Node]:
    """Retrieves all GNS3 Project Nodes

    Args:

    - `project (Project)`: Project object

    Raises:

    - `ValueError`: If project_id attribute is not set

    Returns:

    - `List[Node]`: List of Node objects
    """
    _raw_nodes = connector.http_call(
        "get",
        url=f"{connector.base_url}/projects/{project_id}/nodes",
    ).json()

    for _node in _raw_nodes:
        # Inject project ID (Cases where project is closed)
        if _node.get("project_id") is None:
            _node["project_id"] = project_id

    return [Node(connector=connector, **_node) for _node in _raw_nodes]


def create_node(
    connector: Connector,
    project_id: str,
    template_id: str,
    name: str,
    x: int = 0,
    y: int = 0,
    compute_id: str = "local",
    **kwargs,
) -> Node:
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
    _url = f"{connector.base_url}/projects/{project_id}/templates/{template_id}"

    _response = connector.http_call(
        "post", _url, json_data=dict(x=x, y=y, compute_id=compute_id)
    )

    node = Node(connector=connector, **_response.json())

    # Update the node attributes based on cached data
    node.update(name=name, **kwargs)
    if node.ports:
        node._resolve_ports_nodes()

    return node
