"""Model for python GNS3 Snapshots entity and useful snapshot related services
"""
from .connector import Connector
from .base import verify_attributes, BaseResourceModel
from typing import Any, Optional, List
from datetime import datetime
from pydantic import PrivateAttr


class Snapshot(BaseResourceModel):
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

    def __init__(
        self,
        connector: Connector,
        name: Optional[str] = None,
        project_id: Optional[str] = None,
        **data: Any,
    ) -> None:
        super().__init__(name=name, project_id=project_id, **data)
        self._connector = connector

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
    def delete(self) -> bool:
        """
        Deletes a snapshot endpoint from the server.

        **Required Attributes:**

        - `connector`
        - `snapshot_id`
        """
        _url = (
            f"{self._connector.base_url}/projects/{self.project_id}"
            f"/snapshots/{self.snapshot_id}"
        )

        _response = self._connector.http_call("delete", _url)

        if _response.status_code == 204:
            return True
        else:
            return False

    @verify_attributes(attrs=["_connector", "snapshot_id", "project_id"])
    def restore_snapshot(self) -> bool:
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
        _url = (
            f"{self._connector.base_url}/projects/{self.project_id}/"
            f"snapshots/{self.snapshot_id}/restore"
        )
        _response = self._connector.http_call("post", _url)

        if _response.status_code == 201:
            return True
        else:
            return False


def get_snapshots(connector: Connector, project_id: str) -> List[Snapshot]:
    """Retrieves all GNS3 Project Snapshots

    Args:

    - `project (Project)`: Project object

    Returns:

    - `List[Snapshot]`: List of Snapshot objects
    """

    _raw_snapshots = connector.http_call(
        "get",
        url=f"{connector.base_url}/projects/{project_id}/snapshots",
    ).json()

    return [Snapshot(connector=connector, **_snapshot) for _snapshot in _raw_snapshots]


def create_snapshot(connector: Connector, project_id: str, name: str) -> Snapshot:
    """Creates a GNS3 Project Snapshot

    Args:

    - `project (Project)`: Project object
    - `name (str)`: Snapshot name

    Raises:

    - `ValueError`: If snapshot is already created

    Returns:

    - `Snapshot`: Snapshot object
    """

    _url = f"{connector.base_url}/projects/{project_id}/snapshots"

    _response = connector.http_call("post", _url, json_data=dict(name=name))

    return Snapshot(connector=connector, **_response.json())
