"""Model for python GNS3 Link entity and useful link related services
"""
from .connector import Connector
from .base import verify_attributes, BaseResourceModel
from .ports import Port, gen_port_from_links
from typing import Any, List, Optional, Dict
from pydantic import PrivateAttr, Field, validator


LINK_TYPES = ["ethernet", "serial"]


class Link(BaseResourceModel):
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
    link_id: str
    _connector: Connector = PrivateAttr()
    link_type: Optional[str] = None
    suspend: Optional[bool] = None
    filters: Optional[Any] = None
    capturing: Optional[bool] = None
    capture_file_path: Optional[str] = None
    capture_file_name: Optional[str] = None
    capture_compute_id: Optional[str] = None
    nodes: List[Port] = Field(default_factory=list)

    name: Optional[str] = None

    @validator("link_type")
    def valid_link_type(cls, v):
        if not any(x for x in LINK_TYPES if x == v):
            raise ValueError("Not a valid GNS3 Link type")
        return v

    def __init__(
        self,
        project_id: str,
        connector: Connector,
        link_id: Optional[str] = None,
        **data: Any,
    ) -> None:
        super().__init__(project_id=project_id, link_id=link_id, **data)
        self._connector = connector

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

    def _gen_name(self) -> str:
        return (
            f"{self.nodes[0].node_name}: {self.nodes[0].name} == "
            f"{self.nodes[-1].node_name}: {self.nodes[-1].name}"
        )

    def _update(self, data_dict: Dict[str, Any], resolve_node: bool) -> None:
        # Create and resolve Ports for the links
        if data_dict["nodes"]:
            data_dict["nodes"] = gen_port_from_links(
                connector=self._connector,
                project_id=self.project_id,
                port_data=data_dict["nodes"],
                resolve_node=resolve_node,
            )

        # Apply retrieved values to the respective attributes
        for k, v in data_dict.items():
            setattr(self, k, v)

        # Generate name
        self.name = self._gen_name()

    @verify_attributes(attrs=["project_id", "_connector", "link_id"])
    def get(self, resolve_node: bool = True) -> bool:
        """
        Retrieves the information from the link endpoint.

        **Required Attributes:**

        - `project_id`
        - `connector`
        - `link_id`

        Args:

        - `resolve_node (bool)`: If it needs to perform queries to get nodes names.
        Default to True.
        """
        _url = (
            f"{self._connector.base_url}/projects/"
            f"{self.project_id}/links/{self.link_id}"
        )
        _response = self._connector.http_call("get", _url)

        # Update object
        if _response.status_code == 200:
            self._update(_response.json(), resolve_node)
            return True
        else:
            return False

    @verify_attributes(attrs=["project_id", "_connector", "link_id"])
    def delete(self) -> bool:
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

        _response = self._connector.http_call("delete", _url)

        if _response.status_code == 204:
            return True
        else:
            return False

    @verify_attributes(attrs=["project_id", "_connector", "link_id"])
    def update(self, resolve_node: bool = True, **kwargs) -> bool:
        """
        Updates the link instance by passing the keyword arguments of the attributes
        you want updated

        Required Attributes:

        - `project_id`
        - `connector`
        - `link_id`
        """
        _url = (
            f"{self._connector.base_url}/projects/"
            f"{self.project_id}/links/{self.link_id}"
        )

        data = {k: v for k, v in kwargs.items() if k not in ("name", "project_id")}

        # TODO: Verify that the passed kwargs are supported ones
        _response = self._connector.http_call("put", _url, json_data=data)

        # Update object
        if _response.status_code == 201:
            self._update(_response.json(), resolve_node)
            return True
        else:
            return False

    @verify_attributes(attrs=["project_id", "_connector", "link_id"])
    def available_filters(self) -> List[Dict[str, Any]]:
        """
        Updates the link instance by passing the keyword arguments of the attributes
        you want updated

        Required Attributes:

        - `project_id`
        - `connector`
        - `link_id`
        """
        _url = (
            f"{self._connector.base_url}/projects/"
            f"{self.project_id}/links/{self.link_id}/available_filters"
        )

        # TODO: Verify that the passed kwargs are supported ones
        _response = self._connector.http_call("get", _url)

        return _response.json()

    def apply_filters(
        self,
        frequency_drop: Optional[int] = None,
        packet_loss: Optional[int] = None,
        latency: Optional[int] = None,
        jitter: Optional[int] = None,
        corrupt: Optional[int] = None,
        bpf_expression: Optional[str] = None,
    ) -> bool:
        """Applies filters to the link.

        Args:

        - `link (Link)`: Link object
        - `frequency_drop (int, optional)`: It will drop everything with a -1 frequency,
        drop every Nth packet with a positive frequency. Defaults to None.
        - `packet_loss (int, optional)`: Percentage of chance for a packet to be lost.
        Defaults to None.
        - `latency (int, optional)`: Delay packets in milliseconds. Defaults to None.
        - `jitter (int, optional)`: Jitter in milliseconds (+/-) of the delay.
        Defaults to None.
        - `corrupt (int, optional)`: Percentage of chance for a packet to be corrupted.
        Defaults to None.
        - `bpf_expression (str, optional)`: This filter will drop any packet matching a
        BPF expression. Defaults to None.
        """
        filters = {}
        if frequency_drop is not None:
            filters.update({"frequency_drop": [frequency_drop]})
        if packet_loss is not None:
            filters.update({"packet_loss": [packet_loss]})
        if bpf_expression is not None:
            filters.update({"bpf": [bpf_expression]})
        if corrupt is not None:
            filters.update({"corrupt": [corrupt]})
        if latency is not None:
            if jitter is not None:
                filters.update({"delay": [latency, jitter]})
            else:
                filters.update({"delay": [latency]})

        return self.update(filters=filters)


def get_links(
    connector: Connector, project_id: str, resolve_node: bool = True
) -> List[Link]:
    """Retrieves all GNS3 Project Links

    Args:

    - `project (Project)`: Project object

    Raises:

    - `ValueError`: If project_id attribute is not found

    Returns:

    - `List[Link]`: List of Link objects
    """
    _raw_links = connector.http_call(
        "get",
        url=f"{connector.base_url}/projects/{project_id}/links",
    ).json()

    _links = []
    for _raw_link in _raw_links:
        if _raw_link["nodes"]:
            _raw_link["nodes"] = gen_port_from_links(
                connector=connector,
                project_id=project_id,
                port_data=_raw_link["nodes"],
                resolve_node=resolve_node,
            )

        # Inject project ID (Cases where project is closed)
        if _raw_link.get("project_id") is None:
            _raw_link["project_id"] = project_id

        _link = Link(connector=connector, **_raw_link)
        _link.name = _link._gen_name()
        _links.append(_link)

    return _links


def create_link(
    connector: Connector,
    project_id: str,
    node_a_id: str,
    port_a_adapter_number: int,
    port_a_port_number: int,
    port_a_name: str,
    node_b_id: str,
    port_b_adapter_number: int,
    port_b_port_number: int,
    port_b_name: str,
    **kwargs,
) -> Link:
    """
    Creates a link endpoint

    **Required Attributes:**

    - `project_id`
    - `connector`
    - `nodes`
    """
    _url = f"{connector.base_url}/projects/{project_id}/links"

    data = dict(
        nodes=[
            dict(
                adapter_number=port_a_adapter_number,
                port_number=port_a_port_number,
                node_id=node_a_id,
                label=dict(text=port_a_name),
            ),
            dict(
                adapter_number=port_b_adapter_number,
                port_number=port_b_port_number,
                node_id=node_b_id,
                label=dict(text=port_b_name),
            ),
        ],
        **kwargs,
    )

    _response = connector.http_call("post", _url, json_data=data)

    _result_data = _response.json()

    if _result_data["nodes"]:
        _result_data["nodes"] = gen_port_from_links(
            connector=connector,
            project_id=project_id,
            port_data=_result_data["nodes"],
            resolve_node=True,
        )

    link = Link(connector=connector, **_result_data)
    # link.get()
    return link
