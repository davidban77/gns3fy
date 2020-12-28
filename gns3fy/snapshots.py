"""Module for python GNS3 Snapshots entity and useful snapshot related services
"""
from .connector import Connector
from .projects import Project
from typing import TypeVar, Callable, Any, List, Optional
from datetime import datetime
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

        data = {
            k: v
            for k, v in self.dict().items()
            if k not in ("_connector", "__initialised__")
            if v is not None
        }

        _response = self._connector.http_call("post", _url, json_data=data)

        # Now update it
        self._update(_response.json())


def get_snapshots(project: Project) -> List[Snapshot]:
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
        Snapshot(connector=project._connector, **_snapshot)
        for _snapshot in _raw_snapshots
    ]


def search_snapshot(
    project: Project, value: str, type: str = "name"
) -> Optional[Snapshot]:
    """Searches for GNS3 Snapshot from a given snapshot name or ID

    Args:

    - `project (Project)`: Project object
    - `value (str)`: Snapshot name of ID
    - `type (str)`: Type of attribute. `name` or `snapshot_id`

    Returns:

    - `Optional[Snapshot]`: `Snapshot` if found, else `None`
    """
    # Refresh project
    project.get(snapshots=True)

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


def create_snapshot(project: Project, name: str) -> Snapshot:
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

    _snapshot = Snapshot(
        connector=project._connector, project_id=project.project_id, name=name
    )

    _snapshot.create()
    project.snapshots.add(_snapshot)
    return _snapshot


def delete_snapshot(
    project: Project, name: Optional[str] = None, snapshot_id: Optional[str] = None
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
    project: Project, name: Optional[str] = None, snapshot_id: Optional[str] = None
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
