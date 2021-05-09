"""Model for python GNS3 Project entity and useful project related services
"""
import time
from .connector import Connector
from .links import Link, get_links, create_link
from .ports import Port
from .nodes import Node, get_nodes, create_node
from .drawings import Drawing, get_drawings, create_drawing
from .snapshots import Snapshot, get_snapshots, create_snapshot
from .templates import get_templates
from .base import verify_attributes, BaseResourceModel
from typing import Optional, Any, List, Dict, Set, Tuple
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

    project_id: str
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
    nodes: Dict[str, Node] = Field(default_factory=dict)
    # links: Set[Link] = Field(default_factory=set)
    links: Dict[str, Link] = Field(default_factory=dict)

    @validator("status")
    def valid_status(cls, v):
        if not any(x for x in PROJECT_STATUS if x == v):
            raise ValueError("Not a valid GNS3 Project status")
        return v

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
        if not isinstance(other, Project):
            return False
        if self.project_id is None:
            raise ValueError("No project_id present. Need to initialize first")
        return other.project_id == self.project_id

    def __hash__(self) -> int:
        if self.project_id is None:
            raise ValueError("No project_id present. Need to initialize first")
        return hash(self.project_id)

    def _set_nodes(self) -> Dict[str, Node]:
        return {n.name: n for n in get_nodes(self._connector, self.project_id)}

    def _set_links(self) -> Dict[str, Link]:
        _links = {}
        for _link in get_links(self._connector, self.project_id, resolve_node=False):
            for _p in _link.nodes:
                _p.name = _p.label.get("text")
                try:
                    _p.node_name = next(
                        _n.name
                        for _n in self.nodes.values()
                        if _n.node_id == _p.node_id
                    )
                except StopIteration:
                    raise ValueError(f"Node not found {_p.node_id}")
            _link.name = _link._gen_name()
            _links.update({_link.name: _link})
        return _links

    def _resolve_ports_nodes(self) -> None:
        for _n in self.nodes.values():
            for _p in _n.ports:
                _p.node_name = _n.name
                _p.node_id = _n.node_id

    def _resolve_ports_links(self) -> None:
        for _l in self.links.values():
            for _p in _l.nodes:
                _p.name = _p.label.get("text")
                _p.node_name = next(
                    _n.name for _n in self.nodes.values() if _n.node_id == _p.node_id
                )
            _l.name = _l._gen_name()

    @verify_attributes(attrs=["_connector", "project_id"])
    def get(self) -> bool:
        """
        Retrieves the projects information.

        **Required Attributes:**

        - `connector`
        - `project_id`
        """
        # Get project
        _url = f"{self._connector.base_url}/projects/{self.project_id}"
        _response = self._connector.http_call("get", _url)

        if _response.status_code == 200:
            self.snapshots = set(get_snapshots(self._connector, self.project_id))
            self.drawings = set(get_drawings(self._connector, self.project_id))
            self.nodes = self._set_nodes()
            # self.links = set(get_links(self._connector, self.project_id))
            self.links = self._set_links()

            # Update object
            # self._resolve_ports_links()
            self._resolve_ports_nodes()
            self._update(_response.json())
            return True
        else:
            return False

    @verify_attributes(attrs=["project_id", "_connector"])
    def update(self, **kwargs) -> bool:
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

        data = {
            k: v
            for k, v in kwargs.items()
            if k not in ("stats", "snapshots", "drawings", "nodes", "links")
        }

        # TODO: Verify that the passed kwargs are supported ones
        _response = self._connector.http_call("put", _url, json_data=data)

        # Update object
        if _response.status_code == 200:
            self._update(_response.json())
            return True
        else:
            return False

    @verify_attributes(attrs=["project_id", "_connector"])
    def delete(self) -> bool:
        """
        Deletes the project from the server. It sets to `None` the attributes
        `project_id` and `name` when executed successfully

        **Required Attributes:**

        - `project_id`
        - `connector`
        """
        _url = f"{self._connector.base_url}/projects/{self.project_id}"

        _response = self._connector.http_call("delete", _url)

        if _response.status_code == 204:
            return True
        else:
            return False

    @verify_attributes(attrs=["project_id", "_connector"])
    def close(self) -> bool:
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
            self.status = "closed"
            return True
        else:
            return False

    @verify_attributes(attrs=["project_id", "_connector"])
    def open(self) -> bool:
        """
        Opens the project on the server.

        **Required Attributes:**

        - `project_id`
        - `connector`
        """
        _url = f"{self._connector.base_url}/projects/{self.project_id}/open"

        _response = self._connector.http_call("post", _url)

        # Update object
        if _response.status_code == 201:
            # TODO: Bug on pylance - remove ignore
            self.status = "opened"
            return True
        else:
            return False

    @verify_attributes(attrs=["project_id", "_connector"])
    def nodes_action(self, action: str, poll_wait_time: int = 5) -> bool:
        """Action to execute on all Nodes from the project

        Args:

        - `action (str)`: Action to run -> `start`, `stop`, `suspend` and `reload`
        - `poll_wait_time (int, optional)`: Delay to apply when polling. Defaults to 5.
        """
        if action not in ("start", "stop", "suspend", "reload"):
            raise ValueError(f"Action {action} not supported")

        _url = f"{self._connector.base_url}/projects/{self.project_id}/nodes/{action}"

        _response = self._connector.http_call("post", _url)

        if _response.status_code == 201:
            time.sleep(poll_wait_time)
            self.nodes = self._set_nodes()
            return True
        else:
            return False

    @verify_attributes(attrs=["project_id", "_connector"])
    def create_node(
        self, name: str, template: str, x: int = 0, y: int = 0, **kwargs: Dict[str, Any]
    ) -> Node:
        """Creates a GNS3 Node on a project based on given template.

        Args:

        - `project (Project)`: Project object
        - `name (str)`: Name of the node
        - `template_name (str)`: Name of the template of the node
        - `x (int)`: X coordinate to place the node
        - `y (int)`: Y coordinate to place the node
        - `kwargs (Dict[str, Any])`: Keyword attributes of the node to create

        Raises:

        - `ValueError`: If node is already created or if template does not exist

        Returns:

        - `Node`: Node object
        """
        self.get()
        _node = self.nodes.get(name)
        if _node:
            raise ValueError(f"Node {_node.name} already created")

        try:
            _template = next(
                tplt for tplt in get_templates(self._connector) if tplt.name == template
            )
        except StopIteration:
            raise ValueError(f"Template {template} not found")

        _node = create_node(
            connector=self._connector,
            project_id=self.project_id,
            template_id=_template.template_id,
            name=name,
            x=x,
            y=y,
            **kwargs,
        )

        self.nodes.update({_node.name: _node})
        self._resolve_ports_nodes()
        return _node

    @verify_attributes(attrs=["project_id", "_connector"])
    def delete_node(self, name: str) -> bool:
        """Deletes a GNS3 Node in a given project

        Args:

        - `project (Project)`: Project object
        - `name (Optional[str], optional)`: Project name. Defaults to None.
        - `node_id (Optional[str], optional)`: Node ID. Defaults to None.

        Raises:

        - `ValueError`: When neither name nor ID was submitted
        - `ValueError`: When node was not found
        """
        _snode = self.nodes.get(name)

        if _snode is None:
            raise ValueError(f"Node {name} not found")

        if _snode.delete():
            self.nodes.pop(_snode.name)
            return True
        else:
            return False

    @verify_attributes(attrs=["project_id", "_connector"])
    def search_node(self, name: str) -> Optional[Node]:
        """Searches for a GNS3 Link of a given project and set of endpoints of nodes and
        ports.

        Args:

        - `project (Project)`: Project object
        - `node_a (str)`: Endpoint A node name
        - `port_a (str)`: Endpoint A port name
        - `node_b (str)`: Endpoint B node name
        - `port_b (str)`: Endpoint B port name

        Raises:

        - `ValueError`: If port or node is not found

        Returns:

        - `Optional[Link]`: `Link` if found, else `None`
        """
        # Refresh project
        self.get()
        _node = self.nodes.get(name)
        if _node:
            _node.get()
        return _node

    def _link_nodes_and_ports(
        self, node_a: str, port_a: str, node_b: str, port_b: str
    ) -> Tuple[Node, Port, Node, Port]:
        """Generates Nodes and Ports objects if they exist in the project

        Args:

        - `project (Project)`: Project object
        - `node_a (str)`: Endpoint A node name
        - `port_a (str)`: Endpoint A port name
        - `node_b (str)`: Endpoint B node name
        - `port_b (str)`: Endpoint B port name

        Raises:

        - `ValueError`: If port or node is not found

        Returns:

        - `Tuple[Node, Dict[str, Any], Node, Dict[str, Any]]`: Tuple of the endpoints
        in the form of Node and port attributes
        """

        _node_a = self.nodes.get(node_a)
        if not _node_a:
            raise ValueError(f"node_a: {node_a} not found")

        _port_a = _node_a.get_port(port_a)
        if not _port_a:
            raise ValueError(f"port_a: {port_a} not found")

        _node_b = self.nodes.get(node_b)
        if not _node_b:
            raise ValueError(f"node_b: {node_b} not found")

        _port_b = _node_b.get_port(port_b)
        if not _port_b:
            raise ValueError(f"port_b: {port_b} not found")

        return (_node_a, _port_a, _node_b, _port_b)

    def _search_link(
        self,
        node_a: Node,
        port_a: Port,
        node_b: Node,
        port_b: Port,
    ) -> Optional[Link]:
        """Returns a Link if found given a pair of Node and port attributes. For example
        of how port attribute data looks like see in the API documentation.

        Args:

        - `project (Project)`: Project object
        - `node_a (Node)`: Node object
        - `port_a (Port)`: GNS3 port data
        - `node_b (Node)`: [description]
        - `port_b (Port)`: [description]

        Example of port data:

        ```python
        >>> port_a
        {
            "adapter_number": 0,
            "data_link_types": {
                "Ethernet": "DLT_EN10MB"
            },
            "link_type": "ethernet",
            "name": "Ethernet0",
            "port_number": 0,
            "short_name": "e0"
        }
        ```

        Returns:

        - `Optional[Link]`: `Link` if found, else `None`
        """
        _matches = []
        for _l in self.links.values():
            if not _l.nodes:
                continue
            if (
                _l.nodes[0].node_id == node_a.node_id
                and _l.nodes[0].adapter_number == port_a.adapter_number
                and _l.nodes[0].port_number == port_a.port_number
                and _l.nodes[1].node_id == node_b.node_id
                and _l.nodes[1].adapter_number == port_b.adapter_number
                and _l.nodes[1].port_number == port_b.port_number
            ):
                _matches.append(_l)
            elif (
                _l.nodes[1].node_id == node_a.node_id
                and _l.nodes[1].adapter_number == port_a.adapter_number
                and _l.nodes[1].port_number == port_a.port_number
                and _l.nodes[0].node_id == node_b.node_id
                and _l.nodes[0].adapter_number == port_b.adapter_number
                and _l.nodes[0].port_number == port_b.port_number
            ):
                _matches.append(_l)
        try:
            return _matches[0]
        except IndexError:
            return None

    @verify_attributes(attrs=["project_id", "_connector"])
    def create_link(
        self,
        node_a: str,
        port_a: str,
        node_b: str,
        port_b: str,
        **kwargs: Dict[str, Any],
    ) -> Link:
        """Creates a GNS3 Link between 2 nodes in a given project

        Args:

        - `project (Project)`: Project object
        - `node_a (str)`: Endpoint A node name
        - `port_a (str)`: Endpoint A port name
        - `node_b (str)`: Endpoint B node name
        - `port_b (str)`: Endpoint B port name

        Raises:

        - `ValueError`: If port or node is not found

        Returns:

        - `Link`: Link object
        """
        # Refresh project
        self.get()

        _node_a, _port_a, _node_b, _port_b = self._link_nodes_and_ports(
            node_a, port_a, node_b, port_b
        )

        _slink = self._search_link(_node_a, _port_a, _node_b, _port_b)

        if _slink:
            raise ValueError(f"At least one port is used, ID: {_slink.link_id}")

        # Now create the link!
        _link = create_link(
            connector=self._connector,
            project_id=self.project_id,
            node_a_id=_node_a.node_id,
            port_a_adapter_number=_port_a.adapter_number,  # type: ignore
            port_a_port_number=_port_a.port_number,  # type: ignore
            port_a_name=_port_a.name,  # type: ignore
            node_b_id=_node_b.node_id,
            port_b_adapter_number=_port_b.adapter_number,  # type: ignore
            port_b_port_number=_port_b.port_number,  # type: ignore
            port_b_name=_port_b.name,  # type: ignore
            **kwargs,
        )

        # self.links.add(_link)
        self.links.update({_link.name: _link})  # type: ignore
        self._resolve_ports_links()
        return _link

    @verify_attributes(attrs=["project_id", "_connector"])
    def delete_link(self, node_a: str, port_a: str, node_b: str, port_b: str) -> bool:
        """Deletes a GNS3 Link between 2 nodes in a given project

        Args:

        - `project (Project)`: Project object
        - `node_a (str)`: Endpoint A node name
        - `port_a (str)`: Endpoint A port name
        - `node_b (str)`: Endpoint B node name
        - `port_b (str)`: Endpoint B port name

        Raises:

        - `ValueError`: If port is not found
        """
        _link = self.search_link(node_a, port_a, node_b, port_b)

        if _link is None:
            raise ValueError(f"Link not found {node_a, port_a, node_b, port_b}")

        if _link.delete():
            self.links.pop(_link.name)  # type: ignore
            return True
        else:
            return False

    @verify_attributes(attrs=["project_id", "_connector"])
    def search_link(
        self, node_a: str, port_a: str, node_b: str, port_b: str
    ) -> Optional[Link]:
        """Searches for a GNS3 Link of a given project and set of endpoints of nodes and
        ports.

        Args:

        - `project (Project)`: Project object
        - `node_a (str)`: Endpoint A node name
        - `port_a (str)`: Endpoint A port name
        - `node_b (str)`: Endpoint B node name
        - `port_b (str)`: Endpoint B port name

        Raises:

        - `ValueError`: If port or node is not found

        Returns:

        - `Optional[Link]`: `Link` if found, else `None`
        """
        # Refresh project
        self.get()

        _node_a, _port_a, _node_b, _port_b = self._link_nodes_and_ports(
            node_a, port_a, node_b, port_b
        )

        _link = self._search_link(_node_a, _port_a, _node_b, _port_b)
        if _link:
            _link.name = _link._gen_name()
        return _link

    @verify_attributes(attrs=["project_id", "_connector"])
    def search_snapshot(self, name: str) -> Optional[Snapshot]:
        """Searches for GNS3 Snapshot from a given snapshot name or ID

        Args:

        - `project (Project)`: Project object
        - `name (Optional[str], optional)`: Snapshot name. Defaults to None.
        - `snapshot_id (Optional[str], optional)`: Snapshot ID. Defaults to None.

        Returns:

        - `Optional[Snapshot]`: `Snapshot` if found, else `None`
        """
        try:
            return next(
                snap
                for snap in get_snapshots(self._connector, self.project_id)
                if snap.name == name
            )
        except StopIteration:
            return None

    @verify_attributes(attrs=["project_id", "_connector"])
    def create_snapshot(self, name: str) -> Snapshot:
        """Creates a GNS3 Project Snapshot

        Args:

        - `project (Project)`: Project object
        - `name (str)`: Snapshot name

        Raises:

        - `ValueError`: If snapshot is already created

        Returns:

        - `Snapshot`: Snapshot object
        """

        _ssnapshot = self.search_snapshot(name)

        if _ssnapshot:
            raise ValueError(f"Snapshot with same name already exists: {_ssnapshot}")

        _snapshot = create_snapshot(
            connector=self._connector, project_id=self.project_id, name=name
        )

        self.snapshots.add(_snapshot)
        return _snapshot

    @verify_attributes(attrs=["project_id", "_connector"])
    def delete_snapshot(self, name: str) -> bool:
        """Deletes GNS3 Project Snapshot

        Args:

        - `project (Project)`: Project object
        - `name (Optional[str], optional)`: Snapshot name. Defaults to None.
        - `snapshot_id (Optional[str], optional)`: Snapshot ID. Defaults to None.

        Raises:

        - `ValueError`: When neither name nor ID was submitted
        - `ValueError`: When snapshot was not found
        """
        _ssnapshot = self.search_snapshot(name)

        if _ssnapshot is None:
            raise ValueError("Snapshot not found")

        if _ssnapshot.delete():
            self.snapshots.remove(_ssnapshot)
            return True
        else:
            return False

    @verify_attributes(attrs=["project_id", "_connector"])
    def search_drawing(self, drawing_id: str) -> Optional[Drawing]:
        """Searches for GNS3 Drawing from a given drawing svg or ID

        Args:

        - `project (Project)`: Project object
        - `svg (Optional[str], optional)`: Drawing svg string. Defaults to None.
        - `drawing_id (Optional[str], optional)`: Drawing ID. Defaults to None.

        Returns:

        - `Optional[Drawing]`: `Drawing` if found, else `None`
        """
        try:
            _drawings = get_drawings(self._connector, self.project_id)
            return next(draw for draw in _drawings if draw.drawing_id == drawing_id)
        except StopIteration:
            return None

    @verify_attributes(attrs=["project_id", "_connector"])
    def create_drawing(
        self, svg: str, x: int = 0, y: int = 0, **kwargs: Dict[str, Any]
    ) -> Drawing:
        """Creates a GNS3 Project Drawing

        Args:

        - `project (Project)`: Project object
        - `svg (str)`: Drawing svg
        - `kwargs (Dict[str, Any])`: Keyword attributes of the project to create

        Raises:

        - `ValueError`: If drawing is already created

        Returns:

        - `Drawing`: Drawing object
        """

        _drawing = create_drawing(
            connector=self._connector,
            project_id=self.project_id,
            svg=svg,
            x=x,
            y=y,
            **kwargs,
        )

        self.drawings.add(_drawing)
        return _drawing

    @verify_attributes(attrs=["project_id", "_connector"])
    def delete_drawing(self, drawing_id: str) -> bool:
        """Deletes GNS3 Project Drawing based on svg string or drawing ID

        Args:

        - `project (Project)`: Project object
        - `svg (Optional[str], optional)`: Drawing svg string. Defaults to None.
        - `drawing_id (Optional[str], optional)`: Drawing ID. Defaults to None.

        Raises:

        - `ValueError`: When neither name nor ID was submitted
        - `ValueError`: When drawing was not found
        """

        _sdrawing = self.search_drawing(drawing_id)

        if _sdrawing is None:
            raise ValueError("Drawing not found")

        if _sdrawing.delete():
            self.drawings.remove(_sdrawing)
            return True
        else:
            return False

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


def get_projects(connector: Connector) -> List[Project]:
    """Retrieves all GNS3 Projects

    Args:

    - `connector (Connector)`: GNS3 connector object

    Returns:`

    - `List[Project]`: List of Project objects
    """
    _raw_projects = connector.http_call(
        "get", url=f"{connector.base_url}/projects"
    ).json()

    return [Project(connector=connector, **proj) for proj in _raw_projects]


def create_project(connector: Connector, name: str, **kwargs) -> Project:
    """
    Creates the project.

    **Required Attributes:**

    - `name`
    - `connector`
    """
    _url = f"{connector.base_url}/projects"

    _response = connector.http_call("post", _url, json_data=dict(name=name, **kwargs))

    # Now update it
    project = Project(connector=connector, **_response.json())
    # project.get()
    project._update(_response.json())
    return project
