import os
import time
import requests
from functools import wraps
from urllib.parse import urlparse
from requests import HTTPError
from dataclasses import field
from typing import Optional, Any, Dict, List
from pydantic import validator
from pydantic.dataclasses import dataclass
from math import pi, sin, cos


class Config:
    validate_assignment = True
    # TODO: Not really working.. Need to investigate more and possibly open an issue
    extra = "ignore"


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

LINK_TYPES = ["ethernet", "serial"]


class Gns3Connector:
    """
    Connector to be use for interaction against GNS3 server controller API.

    **Attributes:**

    - `url` (str): URL of the GNS3 server (**required**)
    - `user` (str): User used for authentication
    - `cred` (str): Password used for authentication
    - `verify` (bool): Whether or not to verify SSL
    - `api_version` (int): GNS3 server REST API version
    - `api_calls`: Counter of amount of `http_calls` has been performed
    - `base_url`: url passed + api_version
    - `session`: Requests Session object

    **Returns:**

    `Gns3Connector` instance

    **Example:**

    ```python
    >>> server = Gns3Connector(url="http://<address>:3080")
    >>> print(server.get_version())
    {'local': False, 'version': '2.2.0b4'}
    ```
    """

    def __init__(self, url=None, user=None, cred=None, verify=False, api_version=2):
        requests.packages.urllib3.disable_warnings()
        self.base_url = f"{url.strip('/')}/v{api_version}"
        self.user = user
        self.cred = cred
        self.headers = {"Content-Type": "application/json"}
        self.verify = verify
        self.api_calls = 0

        # Create session object
        self._create_session()

    def _create_session(self):
        """
        Creates the requests.Session object and applies the necessary parameters
        """
        self.session = requests.Session()  # pragma: no cover
        self.session.headers["Accept"] = "application/json"  # pragma: no cover
        if self.user:  # pragma: no cover
            self.session.auth = (self.user, self.cred)  # pragma: no cover

    def http_call(
        self,
        method,
        url,
        data=None,
        json_data=None,
        headers=None,
        verify=False,
        params=None,
    ):
        """
        Performs the HTTP operation actioned

        **Required Attributes:**

        - `method` (enum): HTTP method to perform: get, post, put, delete, head,
        patch (**required**)
        - `url` (str): URL target (**required**)
        - `data`: Dictionary or byte of request body data to attach to the Request
        - `json_data`: Dictionary or List of dicts to be passed as JSON object/array
        - `headers`: ictionary of HTTP Headers to attach to the Request
        - `verify`: SSL Verification
        - `params`: Dictionary or bytes to be sent in the query string for the Request
        """
        if data:
            _response = getattr(self.session, method.lower())(
                url, data=data, headers=headers, params=params, verify=verify
            )

        elif json_data:
            _response = getattr(self.session, method.lower())(
                url, json=json_data, headers=headers, params=params, verify=verify
            )

        else:
            _response = getattr(self.session, method.lower())(
                url, headers=headers, params=params, verify=verify
            )
        self.api_calls += 1

        try:
            _response.raise_for_status()
        except HTTPError:
            raise HTTPError(
                f"{_response.json()['status']}: {_response.json()['message']}"
            )

        return _response

    def get_version(self):
        """
        Returns the version information of GNS3 server
        """
        return self.http_call("get", url=f"{self.base_url}/version").json()

    def projects_summary(self, is_print=True):
        """
        Returns a summary of the projects in the server. If `is_print` is `False`, it
        will return a list of tuples like:

        `[(name, project_id, total_nodes, total_links, status) ...]`
        """
        _projects_summary = []
        for _p in self.get_projects():
            # Retrieve the project stats
            _stats = self.http_call(
                "get", f"{self.base_url}/projects/{_p['project_id']}/stats"
            ).json()
            if is_print:
                print(
                    f"{_p['name']}: {_p['project_id']} -- Nodes: {_stats['nodes']} -- "
                    f"Links: {_stats['links']} -- Status: {_p['status']}"
                )
            _projects_summary.append(
                (
                    _p["name"],
                    _p["project_id"],
                    _stats["nodes"],
                    _stats["links"],
                    _p["status"],
                )
            )

        return _projects_summary if not is_print else None

    def get_projects(self):
        """
        Returns the list of the projects on the server
        """
        return self.http_call("get", url=f"{self.base_url}/projects").json()

    def get_project(self, name=None, project_id=None):
        """
        Retrieves a project from either a name or ID

        **Required Attributes:**

        - `name` or `project_id`
        """
        if project_id:
            return self.http_call(
                "get", url=f"{self.base_url}/projects/{project_id}"
            ).json()
        elif name:
            try:
                return next(p for p in self.get_projects() if p["name"] == name)
            except StopIteration:
                # Project not found
                return None
        else:
            raise ValueError("Must provide either a name or project_id")

    def templates_summary(self, is_print=True):
        """
        Returns a summary of the templates in the server. If `is_print` is `False`, it
        will return a list of tuples like:

        `[(name, template_id, template_type, builtin, console_type, category) ...]`
        """
        _templates_summary = []
        for _t in self.get_templates():
            if "console_type" not in _t:
                _t["console_type"] = "N/A"
            if is_print:
                print(
                    f"{_t['name']}: {_t['template_id']} -- Type: {_t['template_type']}"
                    f" -- Builtin: {_t['builtin']} -- Console: {_t['console_type']} -- "
                    f"Category: {_t['category']}"
                )
            _templates_summary.append(
                (
                    _t["name"],
                    _t["template_id"],
                    _t["template_type"],
                    _t["builtin"],
                    _t["console_type"],
                    _t["category"],
                )
            )

        return _templates_summary if not is_print else None

    def get_templates(self):
        """
        Returns the templates defined on the server.
        """
        return self.http_call("get", url=f"{self.base_url}/templates").json()

    def get_template(self, name=None, template_id=None):
        """
        Retrieves a template from either a name or ID

        **Required Attributes:**

        - `name` or `template_id`
        """
        if template_id:
            return self.http_call(
                "get", url=f"{self.base_url}/templates/{template_id}"
            ).json()
        elif name:
            try:
                return next(t for t in self.get_templates() if t["name"] == name)
            except StopIteration:
                # Template name not found
                return None
        else:
            raise ValueError("Must provide either a name or template_id")

    def update_template(self, name=None, template_id=None, **kwargs):
        """
        Updates a template by giving its name or UUID. For more information [API INFO]
        (http://api.gns3.net/en/2.2/api/v2/controller/template/
        templatestemplateid.html#put-v2-templates-template-id)

        **Required Attributes:**

        - `name` or `template_id`
        """
        _template = self.get_template(name=name, template_id=template_id)
        _template.update(**kwargs)

        response = self.http_call(
            "put",
            url=f"{self.base_url}/templates/{_template['template_id']}",
            json_data=_template,
        )

        return response.json()

    def create_template(self, **kwargs):
        """
        Creates a template by giving its attributes. For more information [API INFO]
        (http://api.gns3.net/en/2.2/api/v2/controller/template/
        templates.html#post-v2-templates)

        **Required Attributes:**

        - `name`
        - `compute_id` by default is 'local'
        - `template_type`
        """
        _template = self.get_template(name=kwargs["name"])
        if _template:
            raise ValueError(f"Template already used: {kwargs['name']}")

        if "compute_id" not in kwargs:
            kwargs["compute_id"] = "local"

        response = self.http_call(
            "post", url=f"{self.base_url}/templates", json_data=kwargs
        )

        return response.json()

    def delete_template(self, name=None, template_id=None):
        """
        Deletes a template by giving its attributes. For more information [API INFO]
        (http://api.gns3.net/en/2.2/api/v2/controller/template/
        templatestemplateid.html#id16)

        **Required Attributes:**

        - `name` or `template_id`
        """
        if name and not template_id:
            _template = self.get_template(name=name)
            template_id = _template["template_id"]

        self.http_call("delete", url=f"{self.base_url}/templates/{template_id}")

    def get_nodes(self, project_id):
        """
        Retieves the nodes defined on the project

        **Required Attributes:**

        - `project_id`
        """
        return self.http_call(
            "get", url=f"{self.base_url}/projects/{project_id}/nodes"
        ).json()

    def get_node(self, project_id, node_id):
        """
        Returns the node by locating its ID.

        **Required Attributes:**

        - `project_id`
        - `node_id`
        """
        _url = f"{self.base_url}/projects/{project_id}/nodes/{node_id}"
        return self.http_call("get", _url).json()

    def get_links(self, project_id):
        """
        Retrieves the links defined in the project.

        **Required Attributes:**

        - `project_id`
        """
        return self.http_call(
            "get", url=f"{self.base_url}/projects/{project_id}/links"
        ).json()

    def get_link(self, project_id, link_id):
        """
        Returns the link by locating its ID.

        **Required Attributes:**

        - `project_id`
        - `link_id`
        """
        _url = f"{self.base_url}/projects/{project_id}/links/{link_id}"
        return self.http_call("get", _url).json()

    def create_project(self, **kwargs):
        """
        Pass a dictionary type object with the project parameters to be created.

        **Required Attributes:**

        - `name`

        **Returns**

        JSON project information
        """
        _url = f"{self.base_url}/projects"
        if "name" not in kwargs:
            raise ValueError("Parameter 'name' is mandatory")
        return self.http_call("post", _url, json_data=kwargs).json()

    def delete_project(self, project_id):
        """
        Deletes a project from server.

        **Required Attributes:**

        - `project_id`
        """
        _url = f"{self.base_url}/projects/{project_id}"
        self.http_call("delete", _url)
        return

    def get_computes(self):
        """
        Returns a list of computes.

        **Returns:**

        List of dictionaries of the computes attributes like cpu/memory usage
        """
        _url = f"{self.base_url}/computes"
        return self.http_call("get", _url).json()

    def get_compute(self, compute_id="local"):
        """
        Returns a compute.

        **Returns:**

        Dictionary of the compute attributes like cpu/memory usage
        """
        _url = f"{self.base_url}/computes/{compute_id}"
        return self.http_call("get", _url).json()

    def get_compute_images(self, emulator, compute_id="local"):
        """
        Returns a list of images available for a compute.

        **Required Attributes:**

        - `emulator`: the likes of 'qemu', 'iou', 'docker' ...
        - `compute_id` By default is 'local'

        **Returns:**

        List of dictionaries with images available for the compute for the specified
        emulator
        """
        _url = f"{self.base_url}/computes/{compute_id}/{emulator}/images"
        return self.http_call("get", _url).json()

    def upload_compute_image(self, emulator, file_path, compute_id="local"):
        """
        uploads an image for use by a compute.

        **Required Attributes:**

        - `emulator`: the likes of 'qemu', 'iou', 'docker' ...
        - `file_path`: path of file to be uploaded
        - `compute_id` By default is 'local'
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Could not find file: {file_path}")

        _filename = os.path.basename(file_path)
        _url = f"{self.base_url}/computes/{compute_id}/{emulator}/images/{_filename}"
        self.http_call("post", _url, data=open(file_path, "rb"))

    def get_compute_ports(self, compute_id="local"):
        """
        Returns ports used and configured by a compute.

        **Required Attributes:**

        - `compute_id` By default is 'local'

        **Returns:**

        Dictionary of `console_ports` used and range, as well as the `udp_ports`
        """
        _url = f"{self.base_url}/computes/{compute_id}/ports"
        return self.http_call("get", _url).json()


def verify_connector_and_id(f):
    """
    Main checker for connector object and respective object's ID for their retrieval
    or actions methods.
    """

    @wraps(f)
    def wrapper(self, *args, **kwargs):
        if not self.connector:
            raise ValueError("Gns3Connector not assigned under 'connector'")
        if not self.project_id:
            raise ValueError("Need to submit project_id")
        # Checks for Node
        if self.__class__.__name__ == "Node":
            if not self.node_id:
                if not self.name:
                    raise ValueError("Need to either submit node_id or name")

                # Try to retrieve the node_id
                _url = f"{self.connector.base_url}/projects/{self.project_id}/nodes"
                _response = self.connector.http_call("get", _url)

                extracted = [
                    node for node in _response.json() if node["name"] == self.name
                ]
                if len(extracted) > 1:  # pragma: no cover
                    raise ValueError(
                        "Multiple nodes found with same name. Need to submit node_id"
                    )
                self.node_id = extracted[0]["node_id"]
        # Checks for Link
        if self.__class__.__name__ == "Link":
            if not self.link_id:
                raise ValueError("Need to submit link_id")
        return f(self, *args, **kwargs)

    return wrapper


@dataclass(config=Config)
class Link:
    """
    GNS3 Link API object. For more information visit: [Links Endpoint API information](
    http://api.gns3.net/en/2.2/api/v2/controller/link/projectsprojectidlinks.html)

    **Attributes:**

    - `link_id` (str): Link UUID (**required** to be set when using `get` method)
    - `link_type` (enum): Possible values: ethernet, serial
    - `link_style` (dict): Describes the visual style of the link
    - `project_id` (str): Project UUID (**required**)
    - `connector` (object): `Gns3Connector` instance used for interaction (**required**)
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
    >>> link = Link(project_id=<pr_id>, link_id=<link_id> connector=<Gns3Connector
    instance>)
    >>> link.get()
    >>> print(link.link_type)
    'ethernet'
    ```
    """

    link_id: Optional[str] = None
    link_type: Optional[str] = None
    link_style: Optional[Any] = None
    project_id: Optional[str] = None
    suspend: Optional[bool] = None
    nodes: Optional[List[Any]] = None
    filters: Optional[Dict] = None
    capturing: Optional[bool] = None
    capture_file_path: Optional[str] = None
    capture_file_name: Optional[str] = None
    capture_compute_id: Optional[str] = None

    connector: Optional[Any] = field(default=None, repr=False)

    @validator("link_type")
    def _valid_link_type(cls, value):
        if value not in LINK_TYPES and value is not None:
            raise ValueError(f"Not a valid link_type - {value}")
        return value

    @validator("suspend")
    def _valid_suspend(cls, value):
        if type(value) is not bool and value is not None:
            raise ValueError(f"Not a valid suspend - {value}")  # pragma: no cover
        return value

    @validator("filters")
    def _valid_filters(cls, value):
        if type(value) is not dict and value is not None:
            raise ValueError(f"Not a valid filters - {value}")  # pragma: no cover
        return value

    def _update(self, data_dict):
        for k, v in data_dict.items():
            if k in self.__dict__.keys():
                self.__setattr__(k, v)

    @verify_connector_and_id
    def get(self):
        """
        Retrieves the information from the link endpoint.

        **Required Attributes:**

        - `project_id`
        - `connector`
        - `link_id`
        """
        _url = (
            f"{self.connector.base_url}/projects/{self.project_id}/links/{self.link_id}"
        )
        _response = self.connector.http_call("get", _url)

        # Update object
        self._update(_response.json())

    @verify_connector_and_id
    def delete(self):
        """
        Deletes a link endpoint from the project. It sets to `None` the attributes
        `link_id` when executed sucessfully

        **Required Attributes:**

        - `project_id`
        - `connector`
        - `link_id`
        """
        _url = (
            f"{self.connector.base_url}/projects/{self.project_id}/links/{self.link_id}"
        )

        self.connector.http_call("delete", _url)

        self.project_id = None
        self.link_id = None

    def create(self):
        """
        Creates a link endpoint

        **Required Attributes:**

        - `project_id`
        - `connector`
        - `nodes`
        """
        if not self.connector:
            raise ValueError("Gns3Connector not assigned under 'connector'")
        if not self.project_id:
            raise ValueError("Need to submit project_id")

        _url = f"{self.connector.base_url}/projects/{self.project_id}/links"

        data = {
            k: v
            for k, v in self.__dict__.items()
            if k not in ("connector", "__initialised__")
            if v is not None
        }

        _response = self.connector.http_call("post", _url, json_data=data)

        # Now update it
        self._update(_response.json())

    @verify_connector_and_id
    def update(self, **kwargs):
        """
        Updates the link instance by passing the keyword arguments of the attributes
        you want updated

        Example:

        ```python
        link1.update(suspend=True)
        ```

        This will update the link `suspend` attribute to `True`

        **Required Attributes:**

        - `project_id`
        - `connector`
        - `link_id`
        """
        _url = (
            f"{self.connector.base_url}/projects/{self.project_id}/links/{self.link_id}"
        )

        # TODO: Verify that the passed kwargs are supported ones
        _response = self.connector.http_call("put", _url, json_data=kwargs)

        # Update object
        self._update(_response.json())


@dataclass(config=Config)
class Node:
    """
    GNS3 Node API object. For more information visit: [Node Endpoint API information](
    http://api.gns3.net/en/2.2/api/v2/controller/node/projectsprojectidnodes.html)

    **Attributes:**

    - `name` (str): Node name (**required** when using `create` method)
    - `project_id` (str): Project UUID (**required**)
    - `node_id` (str): Node UUID (**required** when using `get` method)
    - `compute_id` (str): Compute identifier (**required**, default=local)
    - `node_type` (enum): frame_relay_switch, atm_switch, docker, dynamips, vpcs,
    traceng, virtualbox, vmware, iou, qemu (**required** when using `create` method)
    - `connector` (object): `Gns3Connector` instance used for interaction (**required**)
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
    project_id=<pr_id>, connector=<Gns3Connector instance>)
    >>> alpine.create()
    >>> print(alpine.node_id)
    'SOME-UUID-GENERATED'
    ```
    """

    name: Optional[str] = None
    project_id: Optional[str] = None
    node_id: Optional[str] = None
    compute_id: str = "local"
    node_type: Optional[str] = None
    node_directory: Optional[str] = None
    status: Optional[str] = None
    ports: Optional[List] = None
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
    x: Optional[int] = None
    y: Optional[int] = None
    z: Optional[int] = None
    template_id: Optional[str] = None
    properties: Optional[Any] = None

    template: Optional[str] = None
    links: List[Link] = field(default_factory=list, repr=False)
    connector: Optional[Any] = field(default=None, repr=False)

    @validator("node_type")
    def _valid_node_type(cls, value):
        if value not in NODE_TYPES and value is not None:
            raise ValueError(f"Not a valid node_type - {value}")
        return value

    @validator("console_type")
    def _valid_console_type(cls, value):
        if value not in CONSOLE_TYPES and value is not None:
            raise ValueError(f"Not a valid console_type - {value}")
        return value

    @validator("status")
    def _valid_status(cls, value):
        if value not in ("stopped", "started", "suspended") and value is not None:
            raise ValueError(f"Not a valid status - {value}")
        return value

    def _update(self, data_dict):
        for k, v in data_dict.items():
            if k in self.__dict__.keys():
                self.__setattr__(k, v)

    @verify_connector_and_id
    def get(self, get_links=True):
        """
        Retrieves the node information. When `get_links` is `True` it also retrieves the
        links respective to the node.

        **Required Attributes:**

        - `project_id`
        - `connector`
        - `node_id`
        """
        _url = (
            f"{self.connector.base_url}/projects/{self.project_id}/nodes/{self.node_id}"
        )
        _response = self.connector.http_call("get", _url)

        # Update object
        self._update(_response.json())

        if get_links:
            self.get_links()

    @verify_connector_and_id
    def get_links(self):
        """
        Retrieves the links of the respective node. They will be saved at the `links`
        attribute

        **Required Attributes:**

        - `project_id`
        - `connector`
        - `node_id`
        """
        _url = (
            f"{self.connector.base_url}/projects/{self.project_id}/nodes"
            f"/{self.node_id}/links"
        )
        _response = self.connector.http_call("get", _url)

        # Create the Link array but cleanup cache if there is one
        if self.links:
            self.links = []
        for _link in _response.json():
            self.links.append(Link(connector=self.connector, **_link))

    @verify_connector_and_id
    def start(self):
        """
        Starts the node.

        **Required Attributes:**

        - `project_id`
        - `connector`
        - `node_id`
        """
        _url = (
            f"{self.connector.base_url}/projects/{self.project_id}/nodes"
            f"/{self.node_id}/start"
        )
        _response = self.connector.http_call("post", _url)

        # Update object or perform get if change was not reflected
        if _response.json().get("status") == "started":
            self._update(_response.json())
        else:
            self.get()  # pragma: no cover

    @verify_connector_and_id
    def stop(self):
        """
        Stops the node.

        **Required Attributes:**

        - `project_id`
        - `connector`
        - `node_id`
        """
        _url = (
            f"{self.connector.base_url}/projects/{self.project_id}/nodes"
            f"/{self.node_id}/stop"
        )
        _response = self.connector.http_call("post", _url)

        # Update object or perform get if change was not reflected
        if _response.json().get("status") == "stopped":
            self._update(_response.json())
        else:
            self.get()  # pragma: no cover

    @verify_connector_and_id
    def reload(self):
        """
        Reloads the node.

        **Required Attributes:**

        - `project_id`
        - `connector`
        - `node_id`
        """
        _url = (
            f"{self.connector.base_url}/projects/{self.project_id}/nodes"
            f"/{self.node_id}/reload"
        )
        _response = self.connector.http_call("post", _url)

        # Update object or perform get if change was not reflected
        if _response.json().get("status") == "started":
            self._update(_response.json())
        else:
            self.get()  # pragma: no cover

    @verify_connector_and_id
    def suspend(self):
        """
        Suspends the node.

        **Required Attributes:**

        - `project_id`
        - `connector`
        - `node_id`
        """
        _url = (
            f"{self.connector.base_url}/projects/{self.project_id}/nodes"
            f"/{self.node_id}/suspend"
        )
        _response = self.connector.http_call("post", _url)

        # Update object or perform get if change was not reflected
        if _response.json().get("status") == "suspended":
            self._update(_response.json())
        else:
            self.get()  # pragma: no cover

    @verify_connector_and_id
    def update(self, **kwargs):
        """
        Updates the node instance by passing the keyword arguments of the attributes
        you want updated

        Example:

        ```python
        router01.update(name="router01-CSX")
        ```

        This will update the project `auto_close` attribute to `True`

        **Required Attributes:**

        - `project_id`
        - `connector`
        """
        _url = (
            f"{self.connector.base_url}/projects/{self.project_id}/nodes/{self.node_id}"
        )

        # TODO: Verify that the passed kwargs are supported ones
        _response = self.connector.http_call("put", _url, json_data=kwargs)

        # Update object
        self._update(_response.json())

    def create(self):
        """
        Creates a node.

        By default it will fetch the nodes properties for creation based on the
        `template` or `template_id` attribute supplied. This can be overriden/updated
        by sending a dictionary of the properties under `extra_properties`.

        **Required Node instance attributes:**

        - `project_id`
        - `connector`
        - `compute_id`: Defaults to "local"
        - `template` or `template_id` - if not passed as arguments
        """
        if self.node_id:
            raise ValueError("Node already created")
        if not self.connector:
            raise ValueError("Gns3Connector not assigned under 'connector'")
        if not self.project_id:
            raise ValueError("Node object needs to have project_id attribute")
        if not self.template_id:
            if self.template:
                _template = self.connector.get_template(name=self.template)
                if _template is None:
                    raise ValueError(f"Template {self.template} not found")
                self.template_id = self.connector.get_template(name=self.template).get(
                    "template_id"
                )
            else:
                raise ValueError("Need either 'template' of 'template_id'")

        cached_data = {
            k: v
            for k, v in self.__dict__.items()
            if k
            not in (
                "project_id",
                "template",
                "template_id",
                "links",
                "connector",
                "__initialised__",
            )
            if v is not None
        }

        _url = (
            f"{self.connector.base_url}/projects/{self.project_id}/"
            f"templates/{self.template_id}"
        )

        _response = self.connector.http_call(
            "post", _url, json_data=dict(x=0, y=0, compute_id=self.compute_id)
        )

        self._update(_response.json())

        # Update the node attributes based on cached data
        self.update(**cached_data)

    @verify_connector_and_id
    def delete(self):
        """
        Deletes the node from the project. It sets to `None` the attributes `node_id`
        and `name` when executed successfully

        **Required Attributes:**

        - `project_id`
        - `connector`
        - `node_id`
        """
        _url = (
            f"{self.connector.base_url}/projects/{self.project_id}/nodes/{self.node_id}"
        )

        self.connector.http_call("delete", _url)

        self.project_id = None
        self.node_id = None
        self.name = None

    @verify_connector_and_id
    def get_file(self, path):
        """
        Retrieve a file in the node directory.

        **Required Attributes:**

        - `project_id`
        - `connector`
        - `path`: Node's relative path of the file
        """
        _url = (
            f"{self.connector.base_url}/projects/{self.project_id}/nodes/{self.node_id}"
            f"/files/{path}"
        )

        return self.connector.http_call("get", _url).text

    @verify_connector_and_id
    def write_file(self, path, data):
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
            f"{self.connector.base_url}/projects/{self.project_id}/nodes/{self.node_id}"
            f"/files/{path}"
        )

        self.connector.http_call("post", _url, data=data)


@dataclass(config=Config)
class Project:
    """
    GNS3 Project API object. For more information visit: [Project Endpoint API
    information](http://api.gns3.net/en/2.2/api/v2/controller/project/projects.html)

    **Attributes:**

    - `name`: Project name (**required** when using `create` method)
    - `project_id` (str): Project UUID (**required**)
    - `connector` (object): `Gns3Connector` instance used for interaction (**required**)
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
    >>> lab = Project(name="lab", connector=<Gns3Connector instance>)
    >>> lab.create()
    >>> print(lab.status)
    'opened'
    ```
    """

    name: Optional[str] = None
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
    snapshots: Optional[List[Dict]] = None
    drawings: Optional[List[Dict]] = None
    nodes: List[Node] = field(default_factory=list, repr=False)
    links: List[Link] = field(default_factory=list, repr=False)
    connector: Optional[Any] = field(default=None, repr=False)

    @validator("status")
    def _valid_status(cls, value):
        if value != "opened" and value != "closed" and value is not None:
            raise ValueError("status must be opened or closed")
        return value

    def _update(self, data_dict):
        for k, v in data_dict.items():
            if k in self.__dict__.keys():
                self.__setattr__(k, v)

    def get(self, get_links=True, get_nodes=True, get_stats=True):
        """
        Retrieves the projects information.

        - `get_links`: When true it also queries for the links inside the project
        - `get_nodes`: When true it also queries for the nodes inside the project
        - `get_stats`: When true it also queries for the stats inside the project

        It `get_stats` is set to `True`, it also verifies if snapshots and drawings are
        inside the project and stores them in their respective attributes
        (`snapshots` and `drawings`)

        **Required Attributes:**

        - `connector`
        - `project_id` or `name`
        """
        if not self.connector:
            raise ValueError("Gns3Connector not assigned under 'connector'")

        # Get projects if no ID was provided by the name
        if not self.project_id:
            if not self.name:
                raise ValueError("Need to submit either project_id or name")
            _url = f"{self.connector.base_url}/projects"
            # Get all projects and filter the respective project
            _response = self.connector.http_call("get", _url)

            # Filter the respective project
            for _project in _response.json():
                if _project.get("name") == self.name:
                    self.project_id = _project.get("project_id")

        # Get project
        _url = f"{self.connector.base_url}/projects/{self.project_id}"
        _response = self.connector.http_call("get", _url)

        # Update object
        self._update(_response.json())

        if get_stats:
            self.get_stats()
            if self.stats.get("snapshots", 0) > 0:
                self.get_snapshots()
            if self.stats.get("drawings", 0) > 0:
                self.get_drawings()
        if get_nodes:
            self.get_nodes()
        if get_links:
            self.get_links()

    def create(self):
        """
        Creates the project.

        **Required Attributes:**

        - `name`
        - `connector`
        """
        if not self.name:
            raise ValueError("Need to submit project name")
        if not self.connector:
            raise ValueError("Gns3Connector not assigned under 'connector'")

        _url = f"{self.connector.base_url}/projects"

        data = {
            k: v
            for k, v in self.__dict__.items()
            if k not in ("stats", "nodes", "links", "connector", "__initialised__")
            if v is not None
        }

        _response = self.connector.http_call("post", _url, json_data=data)

        # Now update it
        self._update(_response.json())

    @verify_connector_and_id
    def update(self, **kwargs):
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
        _url = f"{self.connector.base_url}/projects/{self.project_id}"

        # TODO: Verify that the passed kwargs are supported ones
        _response = self.connector.http_call("put", _url, json_data=kwargs)

        # Update object
        self._update(_response.json())

    @verify_connector_and_id
    def delete(self):
        """
        Deletes the project from the server. It sets to `None` the attributes
        `project_id` and `name` when executed successfully

        **Required Attributes:**

        - `project_id`
        - `connector`
        """
        _url = f"{self.connector.base_url}/projects/{self.project_id}"

        self.connector.http_call("delete", _url)

        self.project_id = None
        self.name = None

    @verify_connector_and_id
    def close(self):
        """
        Closes the project on the server.

        **Required Attributes:**

        - `project_id`
        - `connector`
        """
        _url = f"{self.connector.base_url}/projects/{self.project_id}/close"

        _response = self.connector.http_call("post", _url)

        # Update object
        if _response.status_code == 204:
            self.status = "closed"

    @verify_connector_and_id
    def open(self):
        """
        Opens the project on the server.

        **Required Attributes:**

        - `project_id`
        - `connector`
        """
        _url = f"{self.connector.base_url}/projects/{self.project_id}/open"

        _response = self.connector.http_call("post", _url)

        # Update object
        self._update(_response.json())

    @verify_connector_and_id
    def get_stats(self):
        """
        Retrieve the stats of the project.

        **Required Attributes:**

        - `project_id`
        - `connector`
        """
        _url = f"{self.connector.base_url}/projects/{self.project_id}/stats"

        _response = self.connector.http_call("get", _url)

        # Update object
        self.stats = _response.json()

    @verify_connector_and_id
    def get_file(self, path):
        """
        Retrieve a file in the project directory. Beware you have warranty to be able to
        access only to file global to the project.

        **Required Attributes:**

        - `project_id`
        - `connector`
        - `path`: Project's relative path of the file
        """
        _url = f"{self.connector.base_url}/projects/{self.project_id}/files/{path}"

        return self.connector.http_call("get", _url).text

    @verify_connector_and_id
    def write_file(self, path, data):
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
        _url = f"{self.connector.base_url}/projects/{self.project_id}/files/{path}"

        self.connector.http_call("post", _url, data=data)

    @verify_connector_and_id
    def get_nodes(self):
        """
        Retrieve the nodes of the project.

        **Required Attributes:**

        - `project_id`
        - `connector`
        """
        _url = f"{self.connector.base_url}/projects/{self.project_id}/nodes"

        _response = self.connector.http_call("get", _url)

        # Create the Nodes array but cleanup cache if there is one
        if self.nodes:
            self.nodes = []
        for _node in _response.json():
            _n = Node(connector=self.connector, **_node)
            _n.project_id = self.project_id
            self.nodes.append(_n)

    @verify_connector_and_id
    def get_links(self):
        """
        Retrieve the links of the project.

        **Required Attributes:**

        - `project_id`
        - `connector`
        """
        _url = f"{self.connector.base_url}/projects/{self.project_id}/links"

        _response = self.connector.http_call("get", _url)

        # Create the Nodes array but cleanup cache if there is one
        if self.links:
            self.links = []
        for _link in _response.json():
            _l = Link(connector=self.connector, **_link)
            _l.project_id = self.project_id
            self.links.append(_l)

    @verify_connector_and_id
    def start_nodes(self, poll_wait_time=5):
        """
        Starts all the nodes inside the project.

        - `poll_wait_time` is used as a delay when performing the next query of the
        nodes status.

        **Required Attributes:**

        - `project_id`
        - `connector`
        """
        _url = f"{self.connector.base_url}/projects/{self.project_id}/nodes/start"

        self.connector.http_call("post", _url)

        # Update object
        time.sleep(poll_wait_time)
        self.get_nodes()

    @verify_connector_and_id
    def stop_nodes(self, poll_wait_time=5):
        """
        Stops all the nodes inside the project.

        - `poll_wait_time` is used as a delay when performing the next query of the
        nodes status.

        **Required Attributes:**

        - `project_id`
        - `connector`
        """
        _url = f"{self.connector.base_url}/projects/{self.project_id}/nodes/stop"

        self.connector.http_call("post", _url)

        # Update object
        time.sleep(poll_wait_time)
        self.get_nodes()

    @verify_connector_and_id
    def reload_nodes(self, poll_wait_time=5):
        """
        Reloads all the nodes inside the project.

        - `poll_wait_time` is used as a delay when performing the next query of the
        nodes status.

        **Required Attributes:**

        - `project_id`
        - `connector`
        """
        _url = f"{self.connector.base_url}/projects/{self.project_id}/nodes/reload"

        self.connector.http_call("post", _url)

        # Update object
        time.sleep(poll_wait_time)
        self.get_nodes()

    @verify_connector_and_id
    def suspend_nodes(self, poll_wait_time=5):
        """
        Suspends all the nodes inside the project.

        - `poll_wait_time` is used as a delay when performing the next query of the
        nodes status.

        **Required Attributes:**

        - `project_id`
        - `connector`
        """
        _url = f"{self.connector.base_url}/projects/{self.project_id}/nodes/suspend"

        self.connector.http_call("post", _url)

        # Update object
        time.sleep(poll_wait_time)
        self.get_nodes()

    def nodes_summary(self, is_print=True):
        """
        Returns a summary of the nodes insode the project. If `is_print` is `False`, it
        will return a list of tuples like:

        `[(node_name, node_status, node_console, node_id) ...]`

        **Required Attributes:**

        - `project_id`
        - `connector`
        """
        if not self.nodes:
            self.get_nodes()

        _nodes_summary = []
        for _n in self.nodes:
            if is_print:
                print(
                    f"{_n.name}: {_n.status} -- Console: {_n.console} -- "
                    f"ID: {_n.node_id}"
                )
            _nodes_summary.append((_n.name, _n.status, _n.console, _n.node_id))

        return _nodes_summary if not is_print else None

    def nodes_inventory(self):
        """
        Returns an inventory-style dictionary of the nodes

        Example:

        `{
            "router01": {
                "server": "127.0.0.1",
                "name": "router01",
                "console_port": 5077,
                "type": "vEOS"
            }
        }`

        **Required Attributes:**

        - `project_id`
        - `connector`
        """

        if not self.nodes:
            self.get_nodes()

        _nodes_inventory = {}
        _server = urlparse(self.connector.base_url).hostname

        for _n in self.nodes:

            _nodes_inventory.update(
                {
                    _n.name: {
                        "server": _server,
                        "name": _n.name,
                        "console_port": _n.console,
                        "console_type": _n.console_type,
                        "type": _n.node_type,
                        "template": _n.template,
                    }
                }
            )

        return _nodes_inventory

    def links_summary(self, is_print=True):
        """
        Returns a summary of the links insode the project. If `is_print` is False, it
        will return a list of tuples like:

        `[(node_a, port_a, node_b, port_b) ...]`

        **Required Attributes:**

        - `project_id`
        - `connector`
        """
        if not self.nodes:
            self.get_nodes()
        if not self.links:
            self.get_links()

        _links_summary = []
        for _l in self.links:
            if not _l.nodes:
                continue
            _side_a = _l.nodes[0]
            _side_b = _l.nodes[1]
            _node_a = [x for x in self.nodes if x.node_id == _side_a["node_id"]][0]
            _port_a = [
                x["name"]
                for x in _node_a.ports
                if x["port_number"] == _side_a["port_number"]
                and x["adapter_number"] == _side_a["adapter_number"]
            ][0]
            _node_b = [x for x in self.nodes if x.node_id == _side_b["node_id"]][0]
            _port_b = [
                x["name"]
                for x in _node_b.ports
                if x["port_number"] == _side_b["port_number"]
                and x["adapter_number"] == _side_b["adapter_number"]
            ][0]
            endpoint_a = f"{_node_a.name}: {_port_a}"
            endpoint_b = f"{_node_b.name}: {_port_b}"
            if is_print:
                print(f"{endpoint_a} ---- {endpoint_b}")
            _links_summary.append((_node_a.name, _port_a, _node_b.name, _port_b))

        return _links_summary if not is_print else None

    def _search_node(self, key, value):
        "Performs a search based on a key and value"
        # Retrive nodes if neccesary
        if not self.nodes:
            self.get_nodes()

        try:
            return [_p for _p in self.nodes if getattr(_p, key) == value][0]
        except IndexError:
            return None

    def get_node(self, name=None, node_id=None):
        """
        Returns the Node object by searching for the `name` or the `node_id`.

        **Required Attributes:**

        - `project_id`
        - `connector`

        **Required keyword arguments:**
        - `name` or `node_id`

        **NOTE:** Run method `get_nodes()` manually to refresh list of nodes if
        necessary
        """
        if node_id:
            return self._search_node(key="node_id", value=node_id)
        elif name:
            return self._search_node(key="name", value=name)
        else:
            raise ValueError("name or node_ide must be provided")

    def _search_link(self, key, value):
        "Performs a search based on a key and value"
        # Retrive links if neccesary
        if not self.links:
            self.get_links()

        try:
            return next(_p for _p in self.links if getattr(_p, key) == value)
        except StopIteration:
            return None

    def get_link(self, link_id):
        """
        Returns the Link object by locating its ID

        **Required Attributes:**

        - `project_id`
        - `connector`
        - `link_id`

        **NOTE:** Run method `get_links()` manually to refresh list of links if
        necessary
        """
        return self._search_link(key="link_id", value=link_id)

    def create_node(self, **kwargs):
        """
        Creates a node. To know available parameters see `Node` object, specifically
        the `create` method. The most basic example would be:

        ```python
        project.create_node(name='test-switch01', template='Ethernet switch')
        ```

        **Required Project instance attributes:**

        - `project_id`
        - `connector`

        **Required keyword aguments:**

        - `template` or `template_id`
        """
        if not self.nodes:
            self.get_nodes()

        _node = Node(project_id=self.project_id, connector=self.connector, **kwargs)

        _node.create()
        self.nodes.append(_node)
        print(
            f"Created: {_node.name} -- Type: {_node.node_type} -- "
            f"Console: {_node.console}"
        )

    def create_link(self, node_a, port_a, node_b, port_b):
        """
        Creates a link.

        **Required Attributes:**

        - `project_id`
        - `connector`
        - `node_a`: Node name of the A side
        - `port_a`: Port name of the A side (must match the `name` attribute of the
        port)
        - `node_b`: Node name of the B side
        - `port_b`: Port name of the B side (must match the `name` attribute of the
        port)
        """
        if not self.nodes:
            self.get_nodes()
        if not self.links:
            self.get_links()

        _node_a = self.get_node(name=node_a)
        if not _node_a:
            raise ValueError(f"node_a: {node_a} not found")
        try:
            _port_a = [_p for _p in _node_a.ports if _p["name"] == port_a][0]
        except IndexError:
            raise ValueError(f"port_a: {port_a} not found")

        _node_b = self.get_node(name=node_b)
        if not _node_b:
            raise ValueError(f"node_b: {node_b} not found")
        try:
            _port_b = [_p for _p in _node_b.ports if _p["name"] == port_b][0]
        except IndexError:
            raise ValueError(f"port_b: {port_b} not found")

        _matches = []
        for _l in self.links:
            if not _l.nodes:
                continue
            if (
                _l.nodes[0]["node_id"] == _node_a.node_id
                and _l.nodes[0]["adapter_number"] == _port_a["adapter_number"]
                and _l.nodes[0]["port_number"] == _port_a["port_number"]
            ):
                _matches.append(_l)
            elif (
                _l.nodes[1]["node_id"] == _node_b.node_id
                and _l.nodes[1]["adapter_number"] == _port_b["adapter_number"]
                and _l.nodes[1]["port_number"] == _port_b["port_number"]
            ):
                _matches.append(_l)  # pragma: no cover
        if _matches:
            raise ValueError(f"At least one port is used, ID: {_matches[0].link_id}")

        # Now create the link!
        _link = Link(
            project_id=self.project_id,
            connector=self.connector,
            nodes=[
                dict(
                    node_id=_node_a.node_id,
                    adapter_number=_port_a["adapter_number"],
                    port_number=_port_a["port_number"],
                    label=dict(text=_port_a["name"]),
                ),
                dict(
                    node_id=_node_b.node_id,
                    adapter_number=_port_b["adapter_number"],
                    port_number=_port_b["port_number"],
                    label=dict(text=_port_b["name"]),
                ),
            ],
        )

        _link.create()
        self.links.append(_link)
        print(f"Created Link-ID: {_link.link_id} -- Type: {_link.link_type}")

    def delete_link(self, node_a, port_a, node_b, port_b):
        """
        Deletes  a link.

        **Required Attributes:**

        - `project_id`
        - `connector`
        - `node_a`: Node name of the A side
        - `port_a`: Port name of the A side (must match the `name` attribute of the
        port)
        - `node_b`: Node name of the B side
        - `port_b`: Port name of the B side (must match the `name` attribute of the
        port)
        """
        if not self.nodes:
            self.get_nodes()  # pragma: no cover
        if not self.links:
            self.get_links()  # pragma: no cover

        # checking link info
        _node_a = self.get_node(name=node_a)
        if not _node_a:
            raise ValueError(f"node_a: {node_a} not found")
        try:
            _port_a = [_p for _p in _node_a.ports if _p["name"] == port_a][0]
        except IndexError:
            raise ValueError(f"port_a: {port_a} not found")

        _node_b = self.get_node(name=node_b)
        if not _node_b:
            raise ValueError(f"node_b: {node_b} not found")
        try:
            _port_b = [_p for _p in _node_b.ports if _p["name"] == port_b][0]
        except IndexError:
            raise ValueError(f"port_b: {port_b} not found")

        _matches = []
        for _l in self.links:
            if not _l.nodes:
                continue
            if (
                _l.nodes[0]["node_id"] == _node_a.node_id
                and _l.nodes[0]["adapter_number"] == _port_a["adapter_number"]
                and _l.nodes[0]["port_number"] == _port_a["port_number"]
            ):
                _matches.append(_l)
            elif (
                _l.nodes[1]["node_id"] == _node_b.node_id
                and _l.nodes[1]["adapter_number"] == _port_b["adapter_number"]
                and _l.nodes[1]["port_number"] == _port_b["port_number"]
            ):
                _matches.append(_l)  # pragma: no cover
        if not _matches:
            raise ValueError(f"Link not found: {node_a, port_a, node_b, port_b}")  # pragma: no cover

            # now to delete the link via GNS3_api
        _link = _matches[0]
        self.links.remove(_link)
        _link_id = _link.link_id
        _link.delete()
        print(
            f"Deleted Link-ID: {_link_id} From node {node_a }, port: {port_a} <-->  "
            f"to node {node_b}, port: {port_b}"
        )

    @verify_connector_and_id
    def get_snapshots(self):
        """
        Retrieves list of snapshots of the project

        **Required Project instance attributes:**

        - `project_id`
        - `connector`
        """
        _url = f"{self.connector.base_url}/projects/{self.project_id}/snapshots"

        response = self.connector.http_call("get", _url)
        self.snapshots = response.json()

    def _search_snapshot(self, key, value):
        "Performs a search based on a key and value"
        if not self.snapshots:
            self.get_snapshots()

        try:
            return next(_p for _p in self.snapshots if _p[key] == value)
        except StopIteration:
            return None

    def get_snapshot(self, name=None, snapshot_id=None):
        """
        Returns the Snapshot by searching for the `name` or the `snapshot_id`.

        **Required Attributes:**

        - `project_id`
        - `connector`

        **Required keyword arguments:**
        - `name` or `snapshot_id`
        """
        if snapshot_id:
            return self._search_snapshot(key="snapshot_id", value=snapshot_id)
        elif name:
            return self._search_snapshot(key="name", value=name)
        else:
            raise ValueError("name or snapshot_id must be provided")

    @verify_connector_and_id
    def create_snapshot(self, name):
        """
        Creates a snapshot of the project

        **Required Project instance attributes:**

        - `project_id`
        - `connector`

        **Required keyword aguments:**

        - `name`
        """
        self.get_snapshots()

        _snapshot = self.get_snapshot(name=name)
        if _snapshot:
            raise ValueError("Snapshot already created")

        _url = f"{self.connector.base_url}/projects/{self.project_id}/snapshots"

        response = self.connector.http_call("post", _url, json_data=dict(name=name))

        _snapshot = response.json()

        self.snapshots.append(_snapshot)
        print(f"Created snapshot: {_snapshot['name']}")

    @verify_connector_and_id
    def delete_snapshot(self, name=None, snapshot_id=None):
        """
        Deletes a snapshot of the project

        **Required Project instance attributes:**

        - `project_id`
        - `connector`

        **Required keyword aguments:**

        - `name` or `snapshot_id`
        """
        self.get_snapshots()

        _snapshot = self.get_snapshot(name=name, snapshot_id=snapshot_id)
        if not _snapshot:
            raise ValueError("Snapshot not found")

        _url = (
            f"{self.connector.base_url}/projects/{self.project_id}/snapshots/"
            f"{_snapshot['snapshot_id']}"
        )

        self.connector.http_call("delete", _url)

        self.get_snapshots()

    @verify_connector_and_id
    def restore_snapshot(self, name=None, snapshot_id=None):
        """
        Restore a snapshot from disk

        **Required Project instance attributes:**

        - `project_id`
        - `connector`

        **Required keyword aguments:**

        - `name` or `snapshot_id`
        """
        self.get_snapshots()

        _snapshot = self.get_snapshot(name=name, snapshot_id=snapshot_id)
        if not _snapshot:
            raise ValueError("Snapshot not found")

        _url = (
            f"{self.connector.base_url}/projects/{self.project_id}/snapshots/"
            f"{_snapshot['snapshot_id']}/restore"
        )

        self.connector.http_call("post", _url)

        # Update the whole project
        self.get()

    def arrange_nodes_circular(self, radius=120):
        """
        Re-arrgange the existing nodes
        in a circular fashion

        **Attributes:**

        - project instance created

        **Example**

        ```python
        >>> proj = Project(name='project_name', connector=Gns3connector)
        >>> proj.arrange_nodes()
        ```
        """

        self.get()
        if self.status != "opened":
            self.open()  # pragma: no cover

        _angle = (2 * pi) / len(self.nodes)
        # The Y Axis is inverted in GNS3, so the -Y is UP
        for index, n in enumerate(self.nodes):
            _x = int(radius * (sin(_angle * index)))
            _y = int(radius * (-cos(_angle * index)))
            n.update(x=_x, y=_y)

    def get_drawing(self, drawing_id=None):
        """
        Returns the drawing by searching for the `svg` or the `drawing_id`.

        **Required Attributes:**

        - `project_id`
        - `connector`

        **Required keyword arguments:**
        - `svg` or `drawing_id`
        """
        if not self.drawings:
            self.get_drawings()

        try:
            return next(
                _drawing
                for _drawing in self.drawings
                if _drawing["drawing_id"] == drawing_id
            )
        except StopIteration:
            return None

    @verify_connector_and_id
    def get_drawings(self):
        """
        Retrieves list of drawings  of the project

        **Required Project instance attributes:**

        - `project_id`
        - `connector`
        """
        _url = f"{self.connector.base_url}/projects/{self.project_id}/drawings"

        _response = self.connector.http_call("get", _url)
        self.drawings = _response.json()

    @verify_connector_and_id
    def create_drawing(self, svg, locked=False, x=10, y=10, z=1):
        """
        Creates a drawing on the project

        **Required Project instance attributes:**

        - `project_id`
        - `connector`
        """
        _url = f"{self.connector.base_url}/projects/{self.project_id}/drawings"

        response = self.connector.http_call(
            "post", _url, json_data=dict(svg=svg, locked=locked, x=x, y=y, z=z)
        )

        _drawing = response.json()

        self.drawings.append(_drawing)
        print(f"Created drawing: {_drawing['drawing_id']}")

    @verify_connector_and_id
    def update_drawing(self, drawing_id, svg=None, locked=None, x=None, y=None, z=None):
        """
        Updates a drawing on the project

        **Required Project instance attributes:**

        - `project_id`
        - `connector`
        """
        _url = (
            f"{self.connector.base_url}/projects/{self.project_id}/drawings/"
            f"{drawing_id}"
        )

        if svg is None:
            svg = [
                draw["svg"]
                for draw in self.drawings
                if draw["drawing_id"] == drawing_id
            ][0]

        if locked is None:
            locked = [
                draw["locked"]
                for draw in self.drawings
                if draw["drawing_id"] == drawing_id
            ][0]

        if x is None:
            x = [
                draw["x"] for draw in self.drawings if draw["drawing_id"] == drawing_id
            ][0]

        if y is None:
            y = [
                draw["y"] for draw in self.drawings if draw["drawing_id"] == drawing_id
            ][0]

        if z is None:
            z = [
                draw["z"] for draw in self.drawings if draw["drawing_id"] == drawing_id
            ][0]

        response = self.connector.http_call(
            "put", _url, json_data=dict(svg=svg, locked=locked, x=x, y=y, z=z)
        )

        self.get_drawings()

        return response.json()

    @verify_connector_and_id
    def delete_drawing(self, drawing_id=None):
        """
        Deletes a drawing of the project

        **Required Project instance attributes:**

        - `project_id`
        - `connector`

        **Required keyword aguments:**

        - `drawing_id`
        """
        self.get_drawings()

        _drawing = self.get_drawing(drawing_id=drawing_id)
        if not _drawing:
            raise ValueError("drawing not found")

        _url = (
            f"{self.connector.base_url}/projects/{self.project_id}/drawings/"
            f"{_drawing['drawing_id']}"
        )

        self.connector.http_call("delete", _url)

        self.get_drawings()
