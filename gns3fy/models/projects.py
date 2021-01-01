"""Model for python GNS3 Project entity and useful project related services
"""
from .connector import Connector
from .links import Link
from .nodes import Node
from .drawings import Drawing
from .snapshots import Snapshot
from .base import verify_attributes, BaseResourceModel
from typing import Optional, Any, List, Dict, Set
from pydantic import PrivateAttr, Field, validator


PROJECT_STATUS = ["opened", "closed"]


class Project(BaseResourceModel):
    """
    GNS3 Project API object. For more information visit:
    [Project Endpoint API information](
    https://gns3-server.readthedocs.io/en/2.2/api/v2/controller/project.html)

    **Attributes:**

    - `name`: Project name (**required** when using `create` method)
    - `project_id` (str): Project UUID (**required**)
    - `connector` (object): `Connector` instance used for interaction (**required**)
    - `status` (enum): Possible values: opened, closed
    - `path` (str): Path of the project on the server
    - `filename` (str): Project filename
    - `auto_start` (bool): Project start when opened
    - `auto_close` (bool): Project auto close when client cut off the notifications feed
    - `auto_open` (bool): Project open when GNS3 start
    - `drawing_grid_size` (int): Grid size for the drawing area for drawings
    - `grid_size` (int): Grid size for the drawing area for nodes
    - `scene_height` (int): Height of the drawing area
    - `scene_width` (int): Width of the drawing area
    - `show_grid` (bool): Show the grid on the drawing area
    - `show_interface_labels` (bool): Show interface labels on the drawing area
    - `show_layers` (bool): Show layers on the drawing area
    - `snap_to_grid` (bool): Snap to grid on the drawing area
    - `supplier` (dict): Supplier of the project
    - `variables` (list): Variables required to run the project
    - `zoom` (int): Zoom of the drawing area
    - `stats` (dict): Project stats
    -.`drawings` (list): List of drawings present on the project
    - `nodes` (list): List of `Node` instances present on the project
    - `links` (list): List of `Link` instances present on the project

    **Returns:**

    `Project` instance

    **Example:**

    ```python
    >>> lab = Project(name="lab", connector=<Connector instance>)
    >>> lab.create()
    >>> print(lab.status)
    'opened'
    ```
    """

    name: Optional[str] = None
    _connector: Connector = PrivateAttr()

    project_id: Optional[str] = None
    status: Optional[str] = None
    path: Optional[str] = None
    filename: Optional[str] = None
    auto_start: Optional[bool] = None
    auto_close: Optional[bool] = None
    auto_open: Optional[bool] = None
    drawing_grid_size: Optional[int] = None
    grid_size: Optional[int] = None
    scene_height: Optional[int] = None
    scene_width: Optional[int] = None
    show_grid: Optional[bool] = None
    show_interface_labels: Optional[bool] = None
    show_layers: Optional[bool] = None
    snap_to_grid: Optional[bool] = None
    supplier: Optional[Any] = None
    variables: Optional[List] = None
    zoom: Optional[int] = None

    stats: Optional[Dict[str, Any]] = None
    snapshots: Set[Snapshot] = Field(default_factory=set)
    drawings: Set[Drawing] = Field(default_factory=set)
    nodes: Set[Node] = Field(default_factory=set)
    links: Set[Link] = Field(default_factory=set)

    @validator("status")
    def valid_status(cls, v):
        if not any(x for x in PROJECT_STATUS if x == v):
            raise ValueError("Not a valid GNS3 Project status")
        return v

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
        if not isinstance(other, Project):
            return False
        if self.project_id is None:
            raise ValueError("No project_id present. Need to initialize first")
        return other.project_id == self.project_id

    def __hash__(self) -> int:
        if self.project_id is None:
            raise ValueError("No project_id present. Need to initialize first")
        return hash(self.project_id)

    @verify_attributes(attrs=["_connector", "project_id"])
    def get(
        self,
    ) -> None:
        """
        Retrieves the projects information.

        **Required Attributes:**

        - `connector`
        - `project_id`
        """
        # Get project
        _url = f"{self._connector.base_url}/projects/{self.project_id}"
        _response = self._connector.http_call("get", _url)

        # Update object
        self._update(_response.json())

        self.get_stats()

    @verify_attributes(attrs=["name", "_connector"])
    def create(self) -> None:
        """
        Creates the project.

        **Required Attributes:**

        - `name`
        - `connector`
        """
        _url = f"{self._connector.base_url}/projects"

        data = self.dict(
            exclude_unset=True,
            exclude={"stats", "nodes", "links", "snapshots", "_connector", "drawings"},
        )

        _response = self._connector.http_call("post", _url, json_data=data)

        # Now update it
        self._update(_response.json())

    @verify_attributes(attrs=["project_id", "_connector"])
    def update(self, **kwargs) -> None:
        """
        Updates the project instance by passing the keyword arguments of the attributes
        you want updated

        Example:

        ```python
        lab.update(auto_close=True)
        ```

        This will update the project `auto_close` attribute to `True`

        **Required Attributes:**

        - `project_id`
        - `connector`
        """
        _url = f"{self._connector.base_url}/projects/{self.project_id}"

        # Apply first values on object to validate types
        for k, v in kwargs.items():
            setattr(self, k, v)

        # TODO: Verify that the passed kwargs are supported ones
        _response = self._connector.http_call("put", _url, json_data=kwargs)

        # Update object
        self._update(_response.json())

    @verify_attributes(attrs=["project_id", "_connector"])
    def delete(self) -> None:
        """
        Deletes the project from the server. It sets to `None` the attributes
        `project_id` and `name` when executed successfully

        **Required Attributes:**

        - `project_id`
        - `connector`
        """
        _url = f"{self._connector.base_url}/projects/{self.project_id}"

        self._connector.http_call("delete", _url)

    @verify_attributes(attrs=["project_id", "_connector"])
    def close(self) -> None:
        """
        Closes the project on the server.

        **Required Attributes:**

        - `project_id`
        - `connector`
        """
        _url = f"{self._connector.base_url}/projects/{self.project_id}/close"

        _response = self._connector.http_call("post", _url)

        # Update object
        if _response.status_code == 204:
            # TODO: Bug on pylance - remove ignore
            self.status = "closed"  # type: ignore

    @verify_attributes(attrs=["project_id", "_connector"])
    def open(self) -> None:
        """
        Opens the project on the server.

        **Required Attributes:**

        - `project_id`
        - `connector`
        """
        _url = f"{self._connector.base_url}/projects/{self.project_id}/open"

        _response = self._connector.http_call("post", _url)

        # Update object
        if _response.status_code == 204:
            # TODO: Bug on pylance - remove ignore
            self.status = "opened"  # type: ignore

    @verify_attributes(attrs=["project_id", "_connector"])
    def get_stats(self) -> None:
        """
        Retrieve the stats of the project.

        **Required Attributes:**

        - `project_id`
        - `connector`
        """
        _url = f"{self._connector.base_url}/projects/{self.project_id}/stats"

        _response = self._connector.http_call("get", _url)

        # Update object
        self.stats = _response.json()

    @verify_attributes(attrs=["project_id", "_connector"])
    def get_file(self, path: str) -> str:
        """
        Retrieve a file in the project directory. Beware you have warranty to be able to
        access only to file global to the project.

        **Required Attributes:**

        - `project_id`
        - `connector`
        - `path`: Project's relative path of the file
        """
        _url = f"{self._connector.base_url}/projects/{self.project_id}/files/{path}"

        return self._connector.http_call("get", _url).text

    @verify_attributes(attrs=["project_id", "_connector"])
    def write_file(self, path: str, data: str) -> None:
        """
        Places a file content on a specified project file path. Beware you have warranty
        to be able to access only to file global to the project.

        Example to create a README.txt for the project:

        ```python
        >>> data = '''
            This is a README description!
            '''

        >>> project.write_file(path='README.txt', data=data)
        ```

        **Required Attributes:**

        - `project_id`
        - `connector`
        - `path`: Project's relative path of the file
        - `data`: Data to be included in the file
        """
        _url = f"{self._connector.base_url}/projects/{self.project_id}/files/{path}"

        self._connector.http_call("post", _url, data=data)
