"""Model for python GNS3 Snapshots entity and useful snapshot related services
"""
from .connector import Connector
from .base import verify_attributes
from typing import Any, Optional
from datetime import datetime
from pydantic import BaseModel, PrivateAttr


class Snapshot(BaseModel):
    """
    GNS3 Snapshot API object. For more information visit:
    [Links Endpoint API information](
    https://gns3-server.readthedocs.io/en/2.2/api/v2/controller/snapshot.html)

    **Attributes:**

    - `connector` (object): `Connector` instance used for interaction (**required**)
    - `name` (str): Snapshot name (**required** when using `create` method)
    - `project_id` (str): Project UUID (**required** when using `create` method)
    - `snapshot_id` (str): Snapshot UUID
    - `created_at` (str): Date of the snapshot (UTC timestamp)

    **Returns:**

    `Snapshot` instance

    **Example:**

    ```python
    >>> template = Snapshot(name=<snapshot name>, connector=<Connector instance>)
    >>> template.create()
    >>> print(template.template_type)
    'ethernet'
    ```
    """

    _connector: Connector = PrivateAttr()
    name: Optional[str] = None
    project_id: Optional[str] = None
    snapshot_id: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        validate_assignment = True
        extra = "ignore"

    def __init__(
        self,
        connector: Connector,
        name: Optional[str] = None,
        project_id: Optional[str] = None,
        **data: Any,
    ) -> None:
        super().__init__(name=name, project_id=project_id, **data)
        self._connector = connector

    def _update(self, data_dict) -> None:
        # Attributes are validated on assignment
        for k, v in data_dict.items():
            setattr(self, k, v)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Snapshot):
            return False
        if self.snapshot_id is None:
            raise ValueError("No snapshot_id present. Need to initialize first")
        return other.snapshot_id == self.snapshot_id

    def __hash__(self) -> int:
        if self.snapshot_id is None:
            raise ValueError("No snapshot_id present. Need to initialize first")
        return hash(self.snapshot_id)

    @verify_attributes(attrs=["_connector", "snapshot_id"])
    def get(self) -> None:
        """
        Retrieves the information from the snapshot endpoint.

        **Required Attributes:**

        - `connector`
        - `snapshot_id`
        """
        raise NotImplementedError

    @verify_attributes(attrs=["_connector", "snapshot_id"])
    def delete(self) -> None:
        """
        Deletes a snapshot endpoint from the server.

        **Required Attributes:**

        - `connector`
        - `snapshot_id`
        """
        _url = f"{self._connector.base_url}/snapshots/{self.snapshot_id}"

        self._connector.http_call("delete", _url)

    @verify_attributes(attrs=["_connector"])
    def create(self) -> None:
        """
        Creates a template. Is important to highlight that the default attributes are
        explicitly specified and that this Model *allows* extra attributes to be passed,
        making the model suitable for updating any kind of template in GNS3.

        For example:

        ```python
        >>> data = dict(template_type="qemu", adapters=...)
        # Note that `adapters` is an attribute related to the `qemu` hosts
        >>> template_eos = Template(name="Arista vEOS", **data)
        >>> template.create()
        ```

        **Required Attributes:**

        - `connector`
        """
        _url = f"{self._connector.base_url}/templates"

        data = self.dict(
            exclude_unset=True,
            exclude={"_connector", "snapshot_id"},
        )

        _response = self._connector.http_call("post", _url, json_data=data)

        # Now update it
        self._update(_response.json())
