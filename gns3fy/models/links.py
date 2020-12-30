"""Model for python GNS3 Link entity and useful link related services
"""
from .connector import Connector
from .base import verify_attributes
from .ports import Port
from typing import Any, List, Optional
from pydantic import BaseModel, PrivateAttr, Field, validator


LINK_TYPES = ["ethernet", "serial"]


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
    link_type: Optional[str] = None
    suspend: Optional[bool] = None
    filters: Optional[Any] = None
    capturing: Optional[bool] = None
    capture_file_path: Optional[str] = None
    capture_file_name: Optional[str] = None
    capture_compute_id: Optional[str] = None
    nodes: List[Port] = Field(default_factory=list)

    @validator("link_type")
    def valid_link_type(cls, v):
        if not any(x for x in LINK_TYPES if x == v):
            raise ValueError("Not a valid GNS3 Link type")
        return v

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

        # data = {
        #     k: v
        #     for k, v in self.dict().items()
        #     if k not in ("_connector", "__initialised__")
        #     if v is not None
        # }
        data = self.dict(
            exclude_unset=True,
            exclude={"_connector"},
        )

        _response = self._connector.http_call("post", _url, json_data=data)

        # Now update it
        self._update(_response.json())
