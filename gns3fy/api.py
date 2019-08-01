import time
import requests
from urllib.parse import urlencode
from requests import ConnectionError, ConnectTimeout, HTTPError
from dataclasses import field
from typing import Optional, Any, Dict, List
from pydantic import validator
from pydantic.dataclasses import dataclass


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

    Attributes:
    - `base_url`: url passed + api_version
    - `user`: User used for authentication
    - `cred`: Password used for authentication
    - `verify`: Whether or not to verify SSL
    - `api_calls`: Counter of amount of `http_calls` has been performed
    - `session`: Requests Session object

    Methods:
    - `http_call`: Main method to perform REST API calls
    - `error_checker`: Performs basic HTTP code checking
    - `get_projects`: Retrieves ALL the projects configured on a GNS3 server
    """

    def __init__(self, url=None, user=None, cred=None, verify=False, api_version=2):
        requests.packages.urllib3.disable_warnings()
        self.base_url = f"{url.strip('/')}/v{api_version}"
        self.user = user
        self.headers = {"Content-Type": "application/json"}
        self.verify = verify
        self.api_calls = 0

        # Create session object
        self.session = requests.Session()
        self.session.headers["Accept"] = "application/json"
        if self.user:
            self.session.auth = (user, cred)

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
        "Standard method to perform calls"
        try:
            if data:
                _response = getattr(self.session, method.lower())(
                    url,
                    data=urlencode(data),
                    headers=headers,
                    params=params,
                    verify=verify,
                )

            elif json_data:
                _response = getattr(self.session, method.lower())(
                    url, json=json_data, headers=headers, params=params, verify=verify
                )

            else:
                _response = getattr(self.session, method.lower())(
                    url, headers=headers, params=params, verify=verify
                )

            time.sleep(0.5)
            self.api_calls += 1

        except (ConnectTimeout, ConnectionError) as err:
            print(
                f"[ERROR] Connection Error, could not perform {method}"
                f" operation: {err}"
            )
            return False
        except HTTPError as err:
            print(
                f"[ERROR] An unknown error has been encountered: {err} -"
                f" {_response.text}"
            )
            return False

        return _response

    @staticmethod
    def error_checker(response_obj):
        err = f"[ERROR][{response_obj.status_code}]: {response_obj.text}"
        return err if 400 <= response_obj.status_code <= 599 else False

    def get_projects(self):
        "Returns the list of dictionaries of the projects on the server"
        return self.http_call("get", url=f"{self.base_url}/projects").json()


@dataclass(config=Config)
class Link:
    """
    GNS3 Link API object

    Attributes:
    http://api.gns3.net/en/2.2/api/v2/controller/link/projectsprojectidlinks.html

    Methods:
    - `get`: Retrieves the link information
    - `delete`: Deletes the link
    """

    link_id: Optional[str] = None
    link_type: Optional[str] = None
    project_id: Optional[str] = None
    suspend: Optional[bool] = None
    nodes: Optional[List[Any]] = None
    filters: Optional[Any] = None
    capturing: Optional[bool] = None
    capture_file_path: Optional[str] = None
    capture_file_name: Optional[str] = None
    capture_compute_id: Optional[str] = None

    connector: Optional[Any] = field(default=None, repr=False)

    @validator("link_type")
    def valid_node_type(cls, value):
        if value not in LINK_TYPES:
            raise ValueError(f"Not a valid link_type - {value}")
        return value

    def _update(self, data_dict):
        for k, v in data_dict.items():
            if k in self.__dict__.keys():
                self.__setattr__(k, v)

    def _verify_before_action(self):
        if not self.connector:
            raise ValueError("Gns3Connector not assigned under 'connector'")
        if not self.project_id:
            raise ValueError("Need to submit project_id")
        if not self.link_id:
            raise ValueError("Need to submit link_id")

    def get(self):
        """
        Retrieves the information from the link
        """
        self._verify_before_action()

        _url = (
            f"{self.connector.base_url}/projects/{self.project_id}/links/{self.link_id}"
        )
        _response = self.connector.http_call("get", _url)
        _err = Gns3Connector.error_checker(_response)
        if _err:
            raise ValueError(f"{_err}")

        # Update object
        self._update(_response.json())

    def delete(self):
        """
        Deletes a link from the project
        """
        self._verify_before_action()

        _url = (
            f"{self.connector.base_url}/projects/{self.project_id}/links/{self.link_id}"
        )

        _response = self.connector.http_call("delete", _url)
        _err = Gns3Connector.error_checker(_response)
        if _err:
            raise ValueError(f"{_err}")

        self.project_id = None
        self.link_id = None


@dataclass(config=Config)
class Node:
    """
    GNS3 Node API object.

    Attributes:
    http://api.gns3.net/en/2.2/api/v2/controller/node/projectsprojectidnodes.html

    Methods:
    - `get`: Retrieves the node information
    - `delete`: Deletes the node
    - `get_links`: Retrieves the links of the node
    - `start`: Starts the node
    - `stop`: Stops the node
    - `suspend`: Suspends the node
    - `reload`: Reloads the node
    """

    name: Optional[str] = None
    project_id: Optional[str] = None
    node_id: Optional[str] = None
    compute_id: Optional[str] = None
    node_type: Optional[str] = None
    node_directory: Optional[str] = None
    status: Optional[str] = None
    ports: Optional[List] = None
    port_name_format: Optional[str] = None
    port_segment_size: Optional[int] = None
    first_port_name: Optional[str] = None
    locked: Optional[bool] = None
    label: Optional[Any] = None
    console: Optional[str] = None
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

    links: List[Link] = field(default_factory=list, repr=False)
    connector: Optional[Any] = field(default=None, repr=False)

    @validator("node_type")
    def valid_node_type(cls, value):
        if value not in NODE_TYPES:
            raise ValueError(f"Not a valid node_type - {value}")
        return value

    @validator("console_type")
    def valid_console_type(cls, value):
        if value not in CONSOLE_TYPES:
            raise ValueError(f"Not a valid console_type - {value}")
        return value

    @validator("status")
    def valid_status(cls, value):
        if value not in ("stopped", "started", "suspended"):
            raise ValueError(f"Not a valid status - {value}")
        return value

    def _update(self, data_dict):
        for k, v in data_dict.items():
            if k in self.__dict__.keys():
                self.__setattr__(k, v)

    def _verify_before_action(self):
        if not self.connector:
            raise ValueError("Gns3Connector not assigned under 'connector'")
        if not self.project_id:
            raise ValueError("Need to submit project_id")
        if not self.node_id:
            if not self.name:
                raise ValueError("Need to either submit node_id or name")

            # Try to retrieve the node_id
            _url = f"{self.connector.base_url}/projects/{self.project_id}/nodes"
            _response = self.connector.http_call("get", _url)
            _err = Gns3Connector.error_checker(_response)
            if _err:
                raise ValueError(f"{_err}")

            extracted = [node for node in _response.json() if node["name"] == self.name]
            if len(extracted) > 1:
                raise ValueError(
                    "Multiple nodes found with same name. Need to submit node_id"
                )
            self.node_id = extracted[0]["node_id"]

    def get(self, get_links=True):
        """
        Retrieves the node information.

        - `get_links`: When True is also retrieves the links of the node
        """
        self._verify_before_action()

        _url = (
            f"{self.connector.base_url}/projects/{self.project_id}/nodes/{self.node_id}"
        )
        _response = self.connector.http_call("get", _url)
        _err = Gns3Connector.error_checker(_response)
        if _err:
            raise ValueError(f"{_err}")

        # Update object
        self._update(_response.json())

        if get_links:
            self.get_links()

    def get_links(self):
        """
        Retrieves the links of the respective node
        """
        self._verify_before_action()

        _url = (
            f"{self.connector.base_url}/projects/{self.project_id}/nodes"
            f"/{self.node_id}/links"
        )
        _response = self.connector.http_call("get", _url)
        _err = Gns3Connector.error_checker(_response)
        if _err:
            raise ValueError(f"{_err}")

        # Create the Link array but cleanup cache if there is one
        if self.links:
            self.links = []
        for _link in _response.json():
            self.links.append(Link(connector=self.connector, **_link))

    def start(self):
        """
        Starts the node
        """
        self._verify_before_action()

        _url = (
            f"{self.connector.base_url}/projects/{self.project_id}/nodes"
            f"/{self.node_id}/start"
        )
        _response = self.connector.http_call("post", _url)
        _err = Gns3Connector.error_checker(_response)
        if _err:
            raise ValueError(f"{_err}")

        # Update object or perform get if change was not reflected
        if _response.json().get("status") == "started":
            self._update(_response.json())
        else:
            self.get()

    def stop(self):
        """
        Stops the node
        """
        self._verify_before_action()

        _url = (
            f"{self.connector.base_url}/projects/{self.project_id}/nodes"
            f"/{self.node_id}/stop"
        )
        _response = self.connector.http_call("post", _url)
        _err = Gns3Connector.error_checker(_response)
        if _err:
            raise ValueError(f"{_err}")

        # Update object or perform get if change was not reflected
        if _response.json().get("status") == "stopped":
            self._update(_response.json())
        else:
            self.get()

    def reload(self):
        """
        Reloads the node
        """
        self._verify_before_action()

        _url = (
            f"{self.connector.base_url}/projects/{self.project_id}/nodes"
            f"/{self.node_id}/reload"
        )
        _response = self.connector.http_call("post", _url)
        _err = Gns3Connector.error_checker(_response)
        if _err:
            raise ValueError(f"{_err}")

        # Update object or perform get if change was not reflected
        if _response.json().get("status") == "started":
            self._update(_response.json())
        else:
            self.get()

    def suspend(self):
        """
        Suspends the node
        """
        self._verify_before_action()

        _url = (
            f"{self.connector.base_url}/projects/{self.project_id}/nodes"
            f"/{self.node_id}/suspend"
        )
        _response = self.connector.http_call("post", _url)
        _err = Gns3Connector.error_checker(_response)
        if _err:
            raise ValueError(f"{_err}")

        # Update object or perform get if change was not reflected
        if _response.json().get("status") == "suspended":
            self._update(_response.json())
        else:
            self.get()

    def delete(self):
        """
        Deletes the node from the project
        """
        self._verify_before_action()

        _url = (
            f"{self.connector.base_url}/projects/{self.project_id}/nodes/{self.node_id}"
        )

        _response = self.connector.http_call("delete", _url)
        _err = Gns3Connector.error_checker(_response)
        if _err:
            raise ValueError(f"{_err}")

        self.project_id = None
        self.node_id = None
        self.name = None


@dataclass(config=Config)
class Project:
    """
    GNS3 Project API object

    Attributes:
    http://api.gns3.net/en/2.2/api/v2/controller/project/projects.html

    Methods:
    - `get`: Retrieves the project information
    - `open`: Opens up a project
    - `close`: Closes a project
    - `update`: Updates a project instance
    - `delete`: Deletes the project
    - `get_nodes`: Retrieves the nodes of the project
    - `get_stats`: Retrieves the stats of the project
    - `get_links`: Retrieves the links of the project
    - `start_nodes`: Starts ALL nodes inside the project
    - `stop_nodes`: Stops ALL nodes inside the project
    - `suspend_nodes`: Suspends ALL nodes inside the project
    - `nodes_summary`: Shows summary of the nodes created inside the project
    - `links_summary`: Shows summary of the links created inside the project
    """

    project_id: Optional[str] = None
    name: Optional[str] = None
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
    nodes: List[Node] = field(default_factory=list, repr=False)
    links: List[Link] = field(default_factory=list, repr=False)
    connector: Optional[Any] = field(default=None, repr=False)
    # There are more... but will develop them in due time

    @validator("status")
    def valid_status(cls, value):
        if value != "opened" and value != "closed":
            raise ValueError("status must be 'opened' or 'closed'")
        return value

    def _update(self, data_dict):
        for k, v in data_dict.items():
            if k in self.__dict__.keys():
                self.__setattr__(k, v)

    def _verify_before_action(self):
        if not self.connector:
            raise ValueError("Gns3Connector not assigned under 'connector'")
        if not self.project_id:
            raise ValueError("Need to submit project_id")

    def get(self, get_links=True, get_nodes=True, get_stats=True):
        """
        Retrieves the projects information.

        - `get_links`: When true it also queries for the links inside the project
        - `get_nodes`: When true it also queries for the nodes inside the project
        - `get_stats`: When true it also queries for the stats inside the project
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
            _err = Gns3Connector.error_checker(_response)
            if _err:
                raise ValueError(f"{_err}")

            # Filter the respective project
            for _project in _response.json():
                if _project.get("name") == self.name:
                    self.project_id = _project.get("project_id")

        # Get project
        _url = f"{self.connector.base_url}/projects/{self.project_id}"
        _response = self.connector.http_call("get", _url)
        _err = Gns3Connector.error_checker(_response)
        if _err:
            raise ValueError(f"{_err}")

        # Update object
        self._update(_response.json())

        if get_stats:
            self.get_stats()
        if get_nodes:
            self.get_nodes()
        if get_links:
            self.get_links()

    def update(self, **kwargs):
        """
        Updates the project instance by passing the keyword arguments directly into the
        body of the PUT method.

        Example:
        lab.update(auto_close=True)

        This will update the project `auto_close` attribute to True
        """
        self._verify_before_action()

        _url = f"{self.connector.base_url}/projects/{self.project_id}"

        # TODO: Verify that the passed kwargs are supported ones
        _response = self.connector.http_call("put", _url, json_data=kwargs)
        _err = Gns3Connector.error_checker(_response)
        if _err:
            raise ValueError(f"{_err}")

        # Update object
        self._update(_response.json())

    def delete(self):
        """
        Deletes the project from the server. It DOES NOT DELETE THE OBJECT locally, it
        justs sets the `project_id` and `name` to None
        """
        self._verify_before_action()

        _url = f"{self.connector.base_url}/projects/{self.project_id}"

        _response = self.connector.http_call("delete", _url)
        _err = Gns3Connector.error_checker(_response)
        if _err:
            raise ValueError(f"{_err}")

        self.project_id = None
        self.name = None

    def close(self):
        """
        Closes the project on the server.
        """
        self._verify_before_action()

        _url = f"{self.connector.base_url}/projects/{self.project_id}/close"

        _response = self.connector.http_call("post", _url)
        _err = Gns3Connector.error_checker(_response)
        if _err:
            raise ValueError(f"{_err}")

        # Update object
        self._update(_response.json())

    def open(self):
        """
        Opens the project on the server.
        """
        self._verify_before_action()

        _url = f"{self.connector.base_url}/projects/{self.project_id}/open"

        _response = self.connector.http_call("post", _url)
        _err = Gns3Connector.error_checker(_response)
        if _err:
            raise ValueError(f"{_err}")

        # Update object
        self._update(_response.json())

    def get_stats(self):
        """
        Retrieve the stats of the project
        """
        self._verify_before_action()

        _url = f"{self.connector.base_url}/projects/{self.project_id}/stats"

        _response = self.connector.http_call("get", _url)
        _err = Gns3Connector.error_checker(_response)
        if _err:
            raise ValueError(f"{_err}")

        # Update object
        self.stats = _response.json()

    def get_nodes(self):
        """
        Retrieve the nodes of the project
        """
        self._verify_before_action()

        _url = f"{self.connector.base_url}/projects/{self.project_id}/nodes"

        _response = self.connector.http_call("get", _url)
        _err = Gns3Connector.error_checker(_response)
        if _err:
            raise ValueError(f"{_err}")

        # Create the Nodes array but cleanup cache if there is one
        if self.nodes:
            self.nodes = []
        for _node in _response.json():
            _n = Node(connector=self.connector, **_node)
            _n.project_id = self.project_id
            self.nodes.append(_n)

    def get_links(self):
        """
        Retrieve the links of the project
        """
        self._verify_before_action()

        _url = f"{self.connector.base_url}/projects/{self.project_id}/links"

        _response = self.connector.http_call("get", _url)
        _err = Gns3Connector.error_checker(_response)
        if _err:
            raise ValueError(f"{_err}")

        # Create the Nodes array but cleanup cache if there is one
        if self.links:
            self.links = []
        for _link in _response.json():
            _l = Link(connector=self.connector, **_link)
            _l.project_id = self.project_id
            self.links.append(_l)

    def start_nodes(self, poll_wait_time=5):
        """
        Starts all the nodes inside the project.

        - `poll_wait_time` is used as a delay when performing the next query of the
        nodes status.
        """
        self._verify_before_action()

        _url = f"{self.connector.base_url}/projects/{self.project_id}/nodes/start"

        _response = self.connector.http_call("post", _url)
        _err = Gns3Connector.error_checker(_response)
        if _err:
            raise ValueError(f"{_err}")

        # Update object
        time.sleep(poll_wait_time)
        self.get_nodes()

    def stop_nodes(self, poll_wait_time=5):
        """
        Stops all the nodes inside the project.

        - `poll_wait_time` is used as a delay when performing the next query of the
        nodes status.
        """
        self._verify_before_action()

        _url = f"{self.connector.base_url}/projects/{self.project_id}/nodes/stop"

        _response = self.connector.http_call("post", _url)
        _err = Gns3Connector.error_checker(_response)
        if _err:
            raise ValueError(f"{_err}")

        # Update object
        time.sleep(poll_wait_time)
        self.get_nodes()

    def reload_nodes(self, poll_wait_time=5):
        """
        Reloads all the nodes inside the project.

        - `poll_wait_time` is used as a delay when performing the next query of the
        nodes status.
        """
        self._verify_before_action()

        _url = f"{self.connector.base_url}/projects/{self.project_id}/nodes/reload"

        _response = self.connector.http_call("post", _url)
        _err = Gns3Connector.error_checker(_response)
        if _err:
            raise ValueError(f"{_err}")

        # Update object
        time.sleep(poll_wait_time)
        self.get_nodes()

    def suspend_nodes(self, poll_wait_time=5):
        """
        Suspends all the nodes inside the project.

        - `poll_wait_time` is used as a delay when performing the next query of the
        nodes status.
        """
        self._verify_before_action()

        _url = f"{self.connector.base_url}/projects/{self.project_id}/nodes/suspend"

        _response = self.connector.http_call("post", _url)
        _err = Gns3Connector.error_checker(_response)
        if _err:
            raise ValueError(f"{_err}")

        # Update object
        time.sleep(poll_wait_time)
        self.get_nodes()

    def nodes_summary(self, is_print=True):
        """
        Returns a summary of the nodes insode the project. If `is_print` is False, it
        will return a list of tuples like:

        [(node_name, node_status, node_console, node_id) ...]
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

    def links_summary(self, is_print=True):
        """
        Returns a summary of the links insode the project. If `is_print` is False, it
        will return a list of tuples like:

        [(node_a, port_a, node_b, port_b) ...]
        """
        if not self.nodes:
            self.get_nodes()
        if not self.links:
            self.get_links()

        _links_summary = []
        for _l in self.links:
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
