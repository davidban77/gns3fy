"""Model for python GNS3 Node entity and useful node related services
"""
from .connector import Connector
from .links import Link
from .ports import Port
from .base import verify_attributes
from typing import Optional, Any, List, Set
from pydantic import BaseModel, PrivateAttr, Field, validator


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
    "qemu"
]


CONSOLE_TYPES = [
    "vnc",
    "telnet",
    "http",
    "https",
    "spice",
    "spice+agent",
    "none",
    "null"
]


NODE_STATUS = [
    "stopped",
    "started",
    "suspended"
]


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

    template: Optional[str] = None
    ports: List[Port] = Field(default_factory=list)
    links: Set[Link] = Field(default_factory=set)

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

        # Apply first values on object to validate types
        for k, v in kwargs.items():
            setattr(self, k, v)

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

        # data = {
        #     k: v
        #     for k, v in self.dict().items()
        #     if k
        #     not in (
        #         "project_id",
        #         "template",
        #         "template_id",
        #         "links",
        #         "connector",
        #         "__initialised__",
        #     )
        #     if v is not None
        # }
        data = self.dict(
            exclude_unset=True,
            exclude={"project_id", "template", "template_id", "links", "_connector"},
        )

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
        self.update(**data)

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
