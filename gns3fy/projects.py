"""Module for python GNS3 Project entity and useful project related services
"""
from enum import Enum
from typing import Optional, Any, TypeVar, Callable, List, Dict, Set
from functools import wraps
from pydantic import BaseModel, PrivateAttr, Field
from .connector import Connector
from .links import Link, get_links
from .nodes import Node, get_nodes
from .drawings import Drawing, get_drawings
from .snapshots import Snapshot, get_snapshots


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


class ProjectStatus(Enum):
    opened = "opened"
    closed = "closed"


class Project(BaseModel):
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
    status: Optional[ProjectStatus] = None
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
        links: bool = True,
        nodes: bool = True,
        stats: bool = True,
        snapshots: bool = True,
        drawings: bool = True,
    ) -> None:
        """
        Retrieves the projects information.

        - `links`: When true it also queries for the links inside the project
        - `nodes`: When true it also queries for the nodes inside the project
        - `stats`: When true it also queries for the stats inside the project
        - `snapshots`: When true it also queries for the snapshots inside the project
        - `drawings`: When true it also queries for the drawings inside the project

        **Required Attributes:**

        - `connector`
        - `project_id` or `name`
        """
        # Get project
        _url = f"{self._connector.base_url}/projects/{self.project_id}"
        _response = self._connector.http_call("get", _url)

        # Update object
        self._update(_response.json())

        if stats:
            self.get_stats()
        if snapshots:
            self.get_snapshots()
        if drawings:
            self.get_drawings()
        if nodes:
            self.get_nodes()
        if links:
            self.get_links()

    @verify_attributes(attrs=["name", "_connector"])
    def create(self) -> None:
        """
        Creates the project.

        **Required Attributes:**

        - `name`
        - `connector`
        """
        _url = f"{self._connector.base_url}/projects"

        data = {
            k: v
            for k, v in self.dict().items()
            if k not in ("stats", "nodes", "links", "connector", "__initialised__")
            if v is not None
        }

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
        self._update(_response.json())

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

    @verify_attributes(attrs=["project_id", "_connector"])
    def get_nodes(self) -> None:
        """
        Retrieve the nodes of the project.

        **Required Attributes:**

        - `project_id`
        - `connector`
        """
        # Create the Nodes array but cleanup cache if there is one
        if self.nodes:
            self.nodes.clear()

        self.nodes = set(get_nodes(self))

    @verify_attributes(attrs=["project_id", "_connector"])
    def get_links(self) -> None:
        """
        Retrieve the links of the project.

        **Required Attributes:**

        - `project_id`
        - `connector`
        """
        # Create the Nodes array but cleanup cache if there is one
        if self.links:
            self.links.clear()

        self.links = set(get_links(self))

    # @verify_attributes(attrs=["project_id", "_connector"])
    # def start_nodes(self, poll_wait_time: int = 5) -> None:
    #     """
    #     Starts all the nodes inside the project.

    #     - `poll_wait_time` is used as a delay when performing the next query of the
    #     nodes status.

    #     **Required Attributes:**

    #     - `project_id`
    #     - `connector`
    #     """
    #     _url = f"{self._connector.base_url}/projects/{self.project_id}/nodes/start"

    #     self._connector.http_call("post", _url)

    #     # Update object
    #     time.sleep(poll_wait_time)
    #     self.get_nodes()

    # @verify_attributes(attrs=["project_id", "_connector"])
    # def stop_nodes(self, poll_wait_time: int = 5) -> None:
    #     """
    #     Stops all the nodes inside the project.

    #     - `poll_wait_time` is used as a delay when performing the next query of the
    #     nodes status.

    #     **Required Attributes:**

    #     - `project_id`
    #     - `connector`
    #     """
    #     _url = f"{self._connector.base_url}/projects/{self.project_id}/nodes/stop"

    #     self._connector.http_call("post", _url)

    #     # Update object
    #     time.sleep(poll_wait_time)
    #     self.get_nodes()

    # @verify_attributes(attrs=["project_id", "_connector"])
    # def reload_nodes(self, poll_wait_time: int = 5) -> None:
    #     """
    #     Reloads all the nodes inside the project.

    #     - `poll_wait_time` is used as a delay when performing the next query of the
    #     nodes status.

    #     **Required Attributes:**

    #     - `project_id`
    #     - `connector`
    #     """
    #     _url = f"{self._connector.base_url}/projects/{self.project_id}/nodes/reload"

    #     self._connector.http_call("post", _url)

    #     # Update object
    #     time.sleep(poll_wait_time)
    #     self.get_nodes()

    # @verify_attributes(attrs=["project_id", "_connector"])
    # def suspend_nodes(self, poll_wait_time: int = 5) -> None:
    #     """
    #     Suspends all the nodes inside the project.

    #     - `poll_wait_time` is used as a delay when performing the next query of the
    #     nodes status.

    #     **Required Attributes:**

    #     - `project_id`
    #     - `connector`
    #     """
    #     _url = f"{self._connector.base_url}/projects/{self.project_id}/nodes/suspend"

    #     self._connector.http_call("post", _url)

    #     # Update object
    #     time.sleep(poll_wait_time)
    #     self.get_nodes()

    # def _search_node(self, key: str, value: Any) -> Optional[Node]:
    #     "Performs a search based on a key and value"
    #     # Retrive nodes if neccesary
    #     if not self.nodes:
    #         self.get_nodes()

    #     try:
    #         return next(_p for _p in self.nodes if getattr(_p, key) == value)
    #     except StopIteration:
    #         return None

    # @verify_attributes(attrs=["project_id", "_connector"])
    # def get_node(
    #     self, name: Optional[str] = None, node_id: Optional[str] = None
    # ) -> Optional[Node]:
    #     """
    #     Returns the Node object by searching for the `name` or the `node_id`.

    #     **Required Attributes:**

    #     - `project_id`
    #     - `connector`

    #     **Required keyword arguments:**
    #     - `name` or `node_id`
    #     """
    #     self.get_nodes()
    #     if node_id:
    #         return self._search_node(key="node_id", value=node_id)
    #     elif name:
    #         return self._search_node(key="name", value=name)
    #     else:
    #         raise ValueError("name or node_ide must be provided")

    # @verify_attributes(attrs=["project_id", "_connector"])
    # def create_node(
    #     self,
    #     template: Optional[str] = None,
    #     template_id: Optional[str] = None,
    #     **kwargs,
    # ) -> None:
    #     """
    #     Creates a node. To know available parameters see `Node` object, specifically
    #     the `create` method. The most basic example would be:

    #     ```python
    #     project.create_node(name='test-switch01', template='Ethernet switch')
    #     ```

    #     **Required Project instance attributes:**

    #     - `project_id`
    #     - `connector`

    #     **Required keyword aguments:**

    #     - `template` or `template_id`
    #     """
    #     if template is None and template_id is None:
    #         raise ValueError("Parameter 'template' or 'template_id' needs toe passed")
    #     if not self.nodes:
    #         self.get_nodes()

    #     _node = Node(
    #         project_id=self.project_id,  # type: ignore (Already checked)
    #         connector=self._connector,
    #         template=template,
    #         template_id=template_id,
    #         **kwargs,
    #     )

    #     _node.create()
    #     self.nodes.add(_node)

    @verify_attributes(attrs=["project_id", "_connector"])
    def get_snapshots(self) -> None:
        """
        Retrieves list of snapshots of the project

        **Required Project instance attributes:**

        - `project_id`
        - `connector`
        """
        # Create the snapshots array but cleanup cache if there is one
        if self.snapshots:
            self.snapshots.clear()

        self.snapshots = set(get_snapshots(self))

    # def _search_snapshot(self, key: str, value: Any) -> Optional[Dict[str, Any]]:
    #     "Performs a search based on a key and value"
    #     if not self.snapshots:
    #         self.get_snapshots()

    #     try:
    #         return next(_p for _p in self.snapshots if _p[key] == value)
    #     except StopIteration:
    #         return None

    # @verify_attributes(attrs=["project_id", "_connector"])
    # def get_snapshot(
    #     self, name: Optional[str] = None, snapshot_id: Optional[str] = None
    # ) -> Optional[Dict[str, Any]]:
    #     """
    #     Returns the Snapshot by searching for the `name` or the `snapshot_id`.

    #     **Required Attributes:**

    #     - `project_id`
    #     - `connector`

    #     **Required keyword arguments:**
    #     - `name` or `snapshot_id`
    #     """
    #     if snapshot_id:
    #         return self._search_snapshot(key="snapshot_id", value=snapshot_id)
    #     elif name:
    #         return self._search_snapshot(key="name", value=name)
    #     else:
    #         raise ValueError("name or snapshot_id must be provided")

    # @verify_attributes(attrs=["project_id", "_connector"])
    # def create_snapshot(self, name: str) -> None:
    #     """
    #     Creates a snapshot of the project

    #     **Required Project instance attributes:**

    #     - `project_id`
    #     - `connector`

    #     **Required keyword aguments:**

    #     - `name`
    #     """
    #     self.get_snapshots()

    #     _snapshot = self.get_snapshot(name=name)
    #     if _snapshot:
    #         raise ValueError("Snapshot already created")

    #     _url = f"{self._connector.base_url}/projects/{self.project_id}/snapshots"

    #     response = self._connector.http_call("post", _url, json_data=dict(name=name))

    #     _snapshot = response.json()

    #     self.snapshots.append(_snapshot)

    # @verify_attributes(attrs=["project_id", "_connector"])
    # def delete_snapshot(
    #     self, name: Optional[str] = None, snapshot_id: Optional[str] = None
    # ) -> None:
    #     """
    #     Deletes a snapshot of the project

    #     **Required Project instance attributes:**

    #     - `project_id`
    #     - `connector`

    #     **Required keyword aguments:**

    #     - `name` or `snapshot_id`
    #     """
    #     self.get_snapshots()

    #     _snapshot = self.get_snapshot(name=name, snapshot_id=snapshot_id)
    #     if not _snapshot:
    #         raise ValueError("Snapshot not found")

    #     _url = (
    #         f"{self._connector.base_url}/projects/{self.project_id}/snapshots/"
    #         f"{_snapshot['snapshot_id']}"
    #     )

    #     self._connector.http_call("delete", _url)

    #     self.get_snapshots()

    # @verify_attributes(attrs=["project_id", "_connector"])
    # def restore_snapshot(
    #     self, name: Optional[str] = None, snapshot_id: Optional[str] = None
    # ) -> None:
    #     """
    #     Restore a snapshot from disk

    #     **Required Project instance attributes:**

    #     - `project_id`
    #     - `connector`

    #     **Required keyword aguments:**

    #     - `name` or `snapshot_id`
    #     """
    #     self.get_snapshots()

    #     _snapshot = self.get_snapshot(name=name, snapshot_id=snapshot_id)
    #     if not _snapshot:
    #         raise ValueError("Snapshot not found")

    #     _url = (
    #         f"{self._connector.base_url}/projects/{self.project_id}/snapshots/"
    #         f"{_snapshot['snapshot_id']}/restore"
    #     )

    #     self._connector.http_call("post", _url)

    #     # Update the whole project
    #     self.get()

    # @verify_attributes(attrs=["project_id", "_connector"])
    # def get_drawing(self, drawing_id: Optional[str] = None) -> Optional[Any]:
    #     """
    #     Returns the drawing by searching for the `drawing_id`.

    #     **Required Attributes:**

    #     - `project_id`
    #     - `connector`

    #     **Required keyword arguments:**
    #     - `drawing_id`
    #     """
    #     if not self.drawings:
    #         self.get_drawings()

    #     try:
    #         return next(
    #             _drawing
    #             for _drawing in self.drawings
    #             if _drawing["drawing_id"] == drawing_id
    #         )
    #     except StopIteration:
    #         return None

    @verify_attributes(attrs=["project_id", "_connector"])
    def get_drawings(self) -> None:
        """
        Retrieves list of drawings  of the project

        **Required Project instance attributes:**

        - `project_id`
        - `connector`
        """
        if self.drawings:
            self.drawings.clear()

        self.drawings = set(get_drawings(self))

    # @verify_attributes(attrs=["project_id", "_connector"])
    # def create_drawing(
    #     self, svg: str, locked: bool = False, x: int = 10, y: int = 10, z: int = 1
    # ) -> None:
    #     """
    #     Creates a drawing on the project

    #     **Required Project instance attributes:**

    #     - `project_id`
    #     - `connector`
    #     """
    #     _url = f"{self._connector.base_url}/projects/{self.project_id}/drawings"

    #     response = self._connector.http_call(
    #         "post", _url, json_data=dict(svg=svg, locked=locked, x=x, y=y, z=z)
    #     )

    #     _drawing = response.json()

    #     self.drawings.append(_drawing)

    # @verify_attributes(attrs=["project_id", "_connector"])
    # def update_drawing(
    #     self,
    #     drawing_id: str,
    #     svg: Optional[str] = None,
    #     locked: Optional[bool] = None,
    #     x: Optional[int] = None,
    #     y: Optional[int] = None,
    #     z: Optional[int] = None,
    # ) -> None:
    #     """
    #     Updates a drawing on the project

    #     **Required Project instance attributes:**

    #     - `project_id`
    #     - `connector`
    #     """
    #     _url = (
    #         f"{self._connector.base_url}/projects/{self.project_id}/drawings/"
    #         f"{drawing_id}"
    #     )

    #     if svg is None:
    #         svg = [
    #             draw["svg"]
    #             for draw in self.drawings
    #             if draw["drawing_id"] == drawing_id
    #         ][0]

    #     if locked is None:
    #         locked = [
    #             draw["locked"]
    #             for draw in self.drawings
    #             if draw["drawing_id"] == drawing_id
    #         ][0]

    #     if x is None:
    #         x = [
    #             draw["x"] for draw in self.drawings if draw["drawing_"] == drawing_id
    #         ][0]

    #     if y is None:
    #         y = [
    #             draw["y"] for draw in self.drawings if draw["drawing_"] == drawing_id
    #         ][0]

    #     if z is None:
    #         z = [
    #             draw["z"] for draw in self.drawings if draw["drawing_"] == drawing_id
    #         ][0]

    #     self._connector.http_call(
    #         "put", _url, json_data=dict(svg=svg, locked=locked, x=x, y=y, z=z)
    #     )

    #     self.get_drawings()

    # @verify_attributes(attrs=["project_id", "_connector"])
    # def delete_drawing(self, drawing_id: Optional[str] = None) -> None:
    #     """
    #     Deletes a drawing of the project

    #     **Required Project instance attributes:**

    #     - `project_id`
    #     - `connector`

    #     **Required keyword aguments:**

    #     - `drawing_id`
    #     """
    #     self.get_drawings()

    #     _drawing = self.get_drawing(drawing_id=drawing_id)
    #     if not _drawing:
    #         raise ValueError("drawing not found")

    #     _url = (
    #         f"{self._connector.base_url}/projects/{self.project_id}/drawings/"
    #         f"{_drawing['drawing_id']}"
    #     )

    #     self._connector.http_call("delete", _url)

    #     self.get_drawings()


def get_projects(connector: Connector) -> List[Project]:
    """Retrieves all GNS3 Projects

    Args:

    - `connector (Connector)`: GNS3 connector object

    Returns:

    - `List[Project]`: List of Project objects
    """
    _raw_projects = connector.http_call(
        "get", url=f"{connector.base_url}/projects"
    ).json()

    return [Project(connector=connector, **proj) for proj in _raw_projects]


def search_project(
    connector: Connector, value: str, type: str = "name"
) -> Optional[Project]:
    """Searches for GNS3 Project from a given project name or ID

    Args:

    - `connector (Connector)`: GNS3 connector object
    - `value (str)`: Project name or ID
    - `type (str)`: Type of attribute. `name` or `project_id`

    Returns:

    - `Optional[Project]`: `Project` if found, else `None`
    """
    try:
        if type == "name":
            return next(prj for prj in get_projects(connector) if prj.name == value)
        elif type == "project_id":
            return next(
                prj for prj in get_projects(connector) if prj.project_id == value
            )
        return None
    except StopIteration:
        return None


def create_project(connector: Connector, name: str) -> Project:
    """Creates a GNS3 Project

    Args:

    - `connector (Connector)`: GNS3 connector object
    - `name (str)`: Name of the project

    Raises:

    - `ValueError`: If project already exists

    Returns:

    - `Project`: Project object
    """
    _sproject = search_project(connector, name)

    if _sproject:
        raise ValueError(f"Project with same name already exists: {name}")

    _project = Project(connector=connector, name=name)

    _project.create()
    return _project


def delete_project(
    connector: Connector, name: Optional[str] = None, project_id: Optional[str] = None
) -> None:
    """Deletes a GNS3 Project

    Args:

    - `connector (Connector)`: GNS3 connector object
    - `name (Optional[str], optional)`: Project name. Defaults to None.
    - `project_id (Optional[str], optional)`: Project ID. Defaults to None.

    Raises:

    - `ValueError`: If name of project ID is not submitted
    - `ValueError`: If project is not found
    """
    if name is not None:
        _sproject = search_project(connector, name)
    elif project_id is not None:
        _sproject = search_project(connector, project_id, type="project_id")
    else:
        raise ValueError("Need to submit either name or project_id")

    if _sproject is None:
        raise ValueError("Project not found")

    _sproject.delete()
