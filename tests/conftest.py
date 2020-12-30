from gns3fy.models.projects import Project
import json
import pytest
import requests
import requests_mock
from pathlib import Path
from gns3fy.models.connector import Connector


DATA_FILES = Path(__file__).resolve().parent / "data"
BASE_URL = "mock://gns3server:3080"
CPROJECT = {"name": "API_TEST", "id": "4b21dfb3-675a-4efa-8613-2f7fb32e76fe"}
CNODE = {"name": "alpine-1", "id": "ef503c45-e998-499d-88fc-2765614b313e"}
CTEMPLATE = {"name": "alpine", "id": "847e5333-6ac9-411f-a400-89838584371b"}
CDRAWING = {"id": "04e326ab-09fa-47e6-957e-d5a285efb988"}
CLINK = {"link_type": "ethernet", "id": "4d9f1235-7fd1-466b-ad26-0b4b08beb778"}
CCOMPUTE = {"id": "local"}
CIMAGE = {"filename": "vEOS-lab-4.21.5F.vmdk"}


def links_data():
    with open(DATA_FILES / "links.json") as fdata:
        data = json.load(fdata)
    return data


def nodes_data():
    with open(DATA_FILES / "nodes.json") as fdata:
        data = json.load(fdata)
    return data


def projects_data():
    with open(DATA_FILES / "projects.json") as fdata:
        data = json.load(fdata)
    return data


def projects_snaphot_data():
    with open(DATA_FILES / "project_snapshots.json") as fdata:
        data = json.load(fdata)
    return data


def projects_drawings_data():
    with open(DATA_FILES / "project_drawings.json") as fdata:
        data = json.load(fdata)
    return data


def templates_data():
    with open(DATA_FILES / "templates.json") as fdata:
        data = json.load(fdata)
    return data


def version_data():
    with open(DATA_FILES / "version.json") as fdata:
        data = json.load(fdata)
    return data


def computes_data():
    with open(DATA_FILES / "computes.json") as fdata:
        data = json.load(fdata)
    return data


def compute_qemu_images_data():
    with open(DATA_FILES / "compute_qemu_images.json") as fdata:
        data = json.load(fdata)
    return data


def compute_ports_data():
    with open(DATA_FILES / "compute_ports.json") as fdata:
        data = json.load(fdata)
    return data


def files_data():
    with open(DATA_FILES / "files.txt") as fdata:
        data = fdata.read()
    return data


def json_api_test_project():
    "Fetches the API_TEST project response"
    return next((_p for _p in projects_data() if _p["project_id"] == CPROJECT["id"]))


def json_api_test_node():
    "Fetches the alpine-1 node response"
    return next((_n for _n in nodes_data() if _n["node_id"] == CNODE["id"]))


def json_api_test_template():
    "Fetches the alpine template response"
    return next((_t for _t in templates_data() if _t["template_id"] == CTEMPLATE["id"]))


def json_api_test_compute():
    "Fetches the alpine template response"
    return next((_t for _t in computes_data() if _t["compute_id"] == CCOMPUTE["id"]))


def json_api_test_link():
    "Fetches the alpine link response"
    return next((_l for _l in links_data() if _l["link_id"] == CLINK["id"]))


def post_put_matcher(request):
    "Creates the Responses for POST and PUT requests"
    resp = requests.Response()
    if request.method == "POST":
        if request.path_url.endswith("/computes/local/qemu/images/files.txt"):
            resp.status_code = 204
            return resp
        elif request.path_url.endswith("/projects"):
            # Now verify the data
            _data = request.json()
            if _data["name"] == "new_project":
                _data["project_id"] = "7777777-4444-PROJECT"
                _data["path"] = f"/opt/gns3/projects/{_data['project_id']}"
                _data["status"] = "opened"
                resp.status_code = 201
                resp.json = lambda: _data  # type: ignore
                return resp
            elif _data["name"] == "DUPLICATE":
                resp.status_code = 409
                resp.json = lambda: dict(  # type: ignore
                    message="Project 'DUPLICATE' already exists", status=409
                )
                return resp
        elif request.path_url.endswith(f"/{CPROJECT['id']}/close"):
            resp.status_code = 204
            return resp
        elif request.path_url.endswith(f"/{CPROJECT['id']}/open"):
            _returned = json_api_test_project()
            _returned.update(status="opened")
            resp.status_code = 204
            resp.json = lambda: _returned  # type: ignore
            return resp
        elif request.path_url.endswith(
            f"/{CPROJECT['id']}/templates/{CTEMPLATE['id']}"
        ):
            _data = request.json()
            _returned = json_api_test_node()
            _returned["name"] = "new_node"
            resp.status_code = 201
            resp.json = lambda: {**_returned, **_data}  # type: ignore
            return resp
        elif request.path_url.endswith(f"/{CPROJECT['id']}/files/README.txt"):
            resp.status_code = 200
            return resp
        elif request.path_url.endswith(f"/{CPROJECT['id']}/snapshots"):
            _data = request.json()
            # if _data.get("name") == "snap2":
            if _data.get("name") == "snap3":
                _returned = dict(
                    created_at=1_569_879_997,
                    name="snap3",
                    project_id="28ea5feb-c006-4724-80ec-a7cc0d8b8a5a",
                    snapshot_id="6796e3ad-ce6d-47db-bdd7-b305506ea22d",
                )
                resp.json = lambda: _returned  # type: ignore
                resp.status_code = 201
                return resp
        elif request.path_url.endswith(f"/{CPROJECT['id']}/drawings"):
            _data = request.json()
            _returned = dict(
                locked=False,
                rotation=0,
                x=10,
                y=20,
                z=0,
                svg=_data.get("svg"),
                project_id="28ea5feb-c006-4724-80ec-a7cc0d8b8a5a",
                drawing_id="62afa856-4a43-4444-a376-60f6f963bb3d",
            )
            resp.json = lambda: _returned  # type: ignore
            resp.status_code = 201
            return resp
        elif request.path_url.endswith(
            f"/{CPROJECT['id']}/snapshots/44e08d78-0ee4-4b8f-bad4-117aa67cb759/restore"
        ):
            _returned = json_api_test_project()
            resp.json = lambda: _returned  # type: ignore
            resp.status_code = 201
            return resp
        elif request.path_url.endswith(f"/{CPROJECT['id']}/nodes"):
            _data = request.json()
            if not any(x in _data for x in ("compute_id", "name", "node_type")):
                resp.status_code == 400
                resp.json = lambda: dict(  # type: ignore
                    message="Invalid request", status=400
                )
                return resp
            resp.status_code = 201
            _returned = json_api_test_node()
            _returned.update(
                name=_data["name"],
                compute_id=_data["compute_id"],
                node_type=_data["node_type"],
                console=_data.get("console")
                if _data["name"] == CNODE["name"]
                else 5077,
                node_id=CNODE["id"]
                if _data["name"] == CNODE["name"]
                else "NEW_NODE_ID",
            )
            # For the case when properties have been overriden
            if _data["properties"].get("console_http_port") == 8080:
                _returned.update(properties=_data["properties"])
            resp.json = lambda: _returned  # type: ignore
            return resp
        elif request.path_url.endswith(
            f"/{CPROJECT['id']}/nodes/start"
        ) or request.path_url.endswith(f"/{CPROJECT['id']}/nodes/reload"):
            resp.status_code = 204
            return resp
        elif request.path_url.endswith(f"/{CPROJECT['id']}/nodes/stop"):
            resp.status_code = 204
            return resp
        elif request.path_url.endswith(f"/{CPROJECT['id']}/nodes/suspend"):
            resp.status_code = 204
            return resp
        elif request.path_url.endswith(
            f"/{CPROJECT['id']}/nodes/{CNODE['id']}/start"
        ) or request.path_url.endswith(f"/{CPROJECT['id']}/nodes/{CNODE['id']}/reload"):
            _returned = json_api_test_node()
            _returned.update(status="started")
            resp.status_code = 200
            resp.json = lambda: _returned  # type: ignore
            return resp
        elif request.path_url.endswith(f"/{CPROJECT['id']}/nodes/{CNODE['id']}/stop"):
            _returned = json_api_test_node()
            _returned.update(status="stopped")
            resp.status_code = 200
            resp.json = lambda: _returned  # type: ignore
            return resp
        elif request.path_url.endswith(
            f"/{CPROJECT['id']}/nodes/{CNODE['id']}/files//etc/network/interfaces"
        ):
            resp.status_code = 201
            return resp
        elif request.path_url.endswith(
            f"/{CPROJECT['id']}/nodes/{CNODE['id']}/suspend"
        ):
            _returned = json_api_test_node()
            _returned.update(status="suspended")
            resp.status_code = 200
            resp.json = lambda: _returned  # type: ignore
            return resp
        elif request.path_url.endswith(f"/{CPROJECT['id']}/links"):
            _data = request.json()
            nodes = _data.get("nodes")
            if len(nodes) != 2:
                resp.status_code = 400
                resp.url = request.path_url
                resp.json = lambda: dict(  # type: ignore
                    message="Bad Request", status=400
                )
                return resp
            elif nodes[0]["node_id"] == nodes[1]["node_id"]:
                resp.status_code = 409
                resp.url = request.path_url
                resp.json = lambda: dict(  # type: ignore
                    message="Cannot connect to itself", status=409
                )
                return resp
            _returned = json_api_test_link()
            resp.status_code = 201
            if any(x for x in nodes if x["node_id"] == CNODE["id"]):
                _returned.update(**_data)
                _returned.update(link_id="7777777-4444-link")
                resp.json = lambda: _returned  # type: ignore
            # else:
            #     _returned.update(**_data)
            #     _returned.update(link_id="NEW_LINK_ID")
            #     resp.json = lambda: _returned  # type: ignore
            return resp
        elif request.path_url.endswith("/templates"):
            _data = request.json()
            if _data["name"] == "alpinev2":
                _data["template_id"] = "7777777-4444"
                resp.status_code = 201
                resp.json = lambda: _data  # type: ignore
                return resp
    elif request.method == "PUT":
        if request.path_url.endswith(f"/{CPROJECT['id']}"):
            _data = request.json()
            _returned = json_api_test_project()
            resp.status_code = 200
            resp.json = lambda: {**_returned, **_data}  # type: ignore
            return resp
        elif request.path_url.endswith(f"/{CPROJECT['id']}/nodes/{CNODE['id']}"):
            _data = request.json()
            print(_data)
            if _data.get("name") == "new_node":
                _returned = json_api_test_node()
                _returned["name"] = "new_node"
                _returned["template"] = "alpine"
                _returned["console"] = 5007
                _returned["properties"]["aux"] = 5008
                _returned["node_id"] = "7777777-4444-node"
            else:
                _returned = json_api_test_node()
                # Update the node data based on the _data sent on the request
                for sitem in _data:
                    if sitem in _returned:
                        if isinstance(_returned[sitem], list):
                            continue
                        elif isinstance(_returned[sitem], dict):
                            for k, v in _data[sitem].items():
                                if k in _returned[sitem]:
                                    _returned[sitem][k] = v
                        else:
                            _returned[sitem] = _data[sitem]
            resp.status_code = 200
            resp.json = lambda: _returned  # type: ignore
            return resp
        # For the arrange_nodes_circular
        elif f"/{CPROJECT['id']}/nodes" in request.path_url:
            # _data = request.json()
            _returned = json_api_test_node()
            resp.status_code = 200
            resp.json = lambda: _returned  # type: ignore
            return resp
        elif request.path_url.endswith(f"/templates/{CTEMPLATE['id']}"):
            _data = request.json()
            if _data["category"] == "switch":
                resp.status_code = 200
                resp.json = lambda: _data  # type: ignore
                return resp
        elif request.path_url.endswith(f"/drawings/{CDRAWING['id']}"):
            _data = request.json()
            if _data["x"] == -256:
                resp.status_code = 201
                resp.json = lambda: _data  # type: ignore
                return resp
    return None


class ConnectorMock(Connector):
    def _create_session(self):
        self.session = requests.Session()
        self.adapter = requests_mock.Adapter()
        self.session.mount("mock", self.adapter)
        self.session.headers["Accept"] = "application/json"
        if self.user:
            self.session.auth = (self.user, self.cred)  # type: ignore

        # Apply responses
        self._apply_responses()

    def _apply_responses(self):
        # Record the API expected responses
        # Version
        self.adapter.register_uri(
            "GET", f"{self.base_url}/version", json=version_data()
        )
        ############
        # Computes #
        ############
        self.adapter.register_uri(
            "GET", f"{self.base_url}/computes", json=computes_data()
        )
        self.adapter.register_uri(
            "GET", f"{self.base_url}/computes/local", json=json_api_test_compute()
        )
        self.adapter.register_uri(
            "GET",
            f"{self.base_url}/computes/local/qemu/images",
            json=compute_qemu_images_data(),
        )
        self.adapter.register_uri(
            "GET", f"{self.base_url}/computes/local/ports", json=compute_ports_data()
        )
        #############
        # Templates #
        #############
        self.adapter.register_uri(
            "GET", f"{self.base_url}/templates", json=templates_data()
        )
        for _template in templates_data():
            self.adapter.register_uri(
                "GET",
                f"{self.base_url}/templates/{_template['template_id']}",
                json=_template,
            )
        self.adapter.register_uri(
            "GET",
            f"{self.base_url}/templates/7777-4444-0000",
            json={"message": "Template ID 7777-4444-0000 doesn't exist", "status": 404},
            status_code=404,
        )
        self.adapter.register_uri(
            "DELETE", f"{self.base_url}/templates/{CTEMPLATE['id']}", status_code=204
        )
        ############
        # Projects #
        ############
        self.adapter.register_uri(
            "GET", f"{self.base_url}/projects", json=projects_data()
        )
        for _project in projects_data():
            self.adapter.register_uri(
                "GET",
                f"{self.base_url}/projects/{_project['project_id']}",
                json=_project,
            )
        self.adapter.register_uri(
            "GET",
            f"{self.base_url}/projects/{CPROJECT['id']}/stats",
            json={"drawings": 2, "links": 4, "nodes": 6, "snapshots": 2},
        )
        # Get a project README file info
        self.adapter.register_uri(
            "GET",
            f"{self.base_url}/projects/{CPROJECT['id']}/files/README.txt",
            text="\nThis is a README\n",
            status_code=200,
        )
        self.adapter.register_uri(
            "GET",
            f"{self.base_url}/projects/{CPROJECT['id']}/files//dummy/path",
            json={"message": "404: Not found", "status": 404},
            status_code=404,
        )
        self.adapter.register_uri(
            "GET",
            f"{self.base_url}/projects/{CPROJECT['id']}/snapshots",
            json=projects_snaphot_data(),
            status_code=200,
        )
        self.adapter.register_uri(
            "DELETE",
            f"{self.base_url}/projects/{CPROJECT['id']}/snapshots/"
            "44e08d78-0ee4-4b8f-bad4-117aa67cb759",
            status_code=204,
        )
        self.adapter.register_uri(
            "DELETE",
            f"{self.base_url}/projects/{CPROJECT['id']}/snapshots/dummmy",
            json={"message": "Snapshot ID dummy doesn't exist", "status": 404},
            status_code=404,
        )
        self.adapter.register_uri(
            "GET",
            f"{self.base_url}/projects/{CPROJECT['id']}/drawings",
            json=projects_drawings_data(),
            status_code=200,
        )
        self.adapter.register_uri(
            "DELETE",
            f"{self.base_url}/projects/{CPROJECT['id']}/drawings/{CDRAWING['id']}",
            status_code=204,
        )
        # Extra project
        self.adapter.register_uri(
            "GET",
            f"{self.base_url}/projects/c9dc56bf-37b9-453b-8f95-2845ce8908e3/stats",
            json={"drawings": 0, "links": 9, "nodes": 10, "snapshots": 2},
        )
        self.adapter.register_uri(
            "POST",
            f"{self.base_url}/projects/{CPROJECT['id']}/nodes/start",
            status_code=204,
        )
        self.adapter.register_uri(
            "POST",
            f"{self.base_url}/projects/{CPROJECT['id']}/nodes/stop",
            status_code=204,
        )
        self.adapter.register_uri(
            "GET",
            f"{self.base_url}/projects/7777-4444-0000",
            json={"message": "Project ID 7777-4444-0000 doesn't exist", "status": 404},
            status_code=404,
        )
        self.adapter.register_uri(
            "DELETE", f"{self.base_url}/projects/{CPROJECT['id']}"
        )
        #########
        # Nodes #
        #########
        self.adapter.register_uri(
            "GET", f"{self.base_url}/projects/{CPROJECT['id']}/nodes", json=nodes_data()
        )
        # Register all nodes data to the respective endpoint project
        _nodes_links = {}
        for _n in nodes_data():
            if _n["project_id"] == CPROJECT["id"]:
                self.adapter.register_uri(
                    "GET",
                    f"{self.base_url}/projects/{CPROJECT['id']}/nodes/{_n['node_id']}",
                    json=_n,
                )
                # Save all the links respective to that node
                _nodes_links[_n["node_id"]] = []
                for _l in links_data():
                    for _ln in _l["nodes"]:
                        if _n["node_id"] == _ln["node_id"]:
                            _nodes_links[_n["node_id"]].append(_l)
        # Now register all links to the respective node endpoint
        for _n, _sl in _nodes_links.items():
            self.adapter.register_uri(
                "GET",
                f"{self.base_url}/projects/{CPROJECT['id']}/nodes/{_n}/links",
                json=_sl,
            )
        self.adapter.register_uri(
            "GET",
            f"{self.base_url}/projects/{CPROJECT['id']}/nodes/" "7777-4444-0000",
            json={"message": "Node ID 7777-4444-0000 doesn't exist", "status": 404},
            status_code=404,
        )
        # Get a docker file interfaces info
        self.adapter.register_uri(
            "GET",
            (
                f"{self.base_url}/projects/{CPROJECT['id']}/nodes/{CNODE['id']}/"
                "files//etc/network/interfaces"
            ),
            text=files_data(),
            status_code=204,
        )
        dummy_path_url = (
            f"{self.base_url}/projects/{CPROJECT['id']}/nodes/{CNODE['id']}/"
            "files//dummy/path"
        )
        self.adapter.register_uri(
            "GET",
            dummy_path_url,
            json={"message": f"{dummy_path_url} not found", "status": 404},
            status_code=404,
        )
        self.adapter.register_uri(
            "DELETE",
            f"{self.base_url}/projects/{CPROJECT['id']}/nodes/{CNODE['id']}",
            status_code=204,
        )
        #########
        # Links #
        #########
        self.adapter.register_uri(
            "GET", f"{self.base_url}/projects/{CPROJECT['id']}/links", json=links_data()
        )
        # Register all links data to the respective endpoint
        for _l in links_data():
            self.adapter.register_uri(
                "GET",
                f"{self.base_url}/projects/{CPROJECT['id']}/links/{_l['link_id']}",
                json=_l,
            )
        self.adapter.register_uri(
            "GET",
            f"{self.base_url}/projects/{CPROJECT['id']}/links/" "7777-4444-0000",
            json={"message": "Link ID 7777-4444-0000 doesn't exist", "status": 404},
            status_code=404,
        )
        self.adapter.register_uri(
            "DELETE",
            f"{self.base_url}/projects/{CPROJECT['id']}/links/{CLINK['id']}",
            status_code=204,
        )
        ##################################
        # POST and PUT matcher endpoints #
        ##################################
        self.adapter.add_matcher(post_put_matcher)


# NOTE: Needed to register a different response for nodes endpoint
class ConnectorMockStopped(ConnectorMock):
    def _apply_responses(self):
        # Retrieve same responses
        super()._apply_responses()
        _nodes = nodes_data()
        # Now update nodes status data and save to the endpoint
        for n in _nodes:
            n.update(status="stopped")
        self.adapter.register_uri(
            "GET", f"{self.base_url}/projects/{CPROJECT['id']}/nodes", json=_nodes
        )


# NOTE: Needed to register a different response for nodes endpoint
class ConnectorMockSuspended(ConnectorMock):
    def _apply_responses(self):
        # Retrieve same responses
        super()._apply_responses()
        _nodes = nodes_data()
        # Now update nodes status data and save to the endpoint
        for n in _nodes:
            n.update(status="suspended")
        self.adapter.register_uri(
            "GET", f"{self.base_url}/projects/{CPROJECT['id']}/nodes", json=_nodes
        )


@pytest.fixture(scope="class")
def connector_mock():
    return ConnectorMock(url=BASE_URL)


@pytest.fixture(scope="class")
def project_mock():
    conn = ConnectorMock(url=BASE_URL)
    return Project(connector=conn, **json_api_test_project())
