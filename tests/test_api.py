import json
import pytest
import requests
import requests_mock
from pathlib import Path
from pydantic.error_wrappers import ValidationError
from requests.exceptions import HTTPError
from gns3fy import Link, Node, Project, Gns3Connector
from .data import links, nodes, projects


DATA_FILES = Path(__file__).resolve().parent / "data"
BASE_URL = "mock://gns3server:3080"
CPROJECT = {"name": "API_TEST", "id": "4b21dfb3-675a-4efa-8613-2f7fb32e76fe"}
CNODE = {"name": "alpine-1", "id": "ef503c45-e998-499d-88fc-2765614b313e"}
CTEMPLATE = {"name": "alpine", "id": "847e5333-6ac9-411f-a400-89838584371b"}
CLINK = {"link_type": "ethernet", "id": "4d9f1235-7fd1-466b-ad26-0b4b08beb778"}


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


def templates_data():
    with open(DATA_FILES / "templates.json") as fdata:
        data = json.load(fdata)
    return data


def version_data():
    with open(DATA_FILES / "version.json") as fdata:
        data = json.load(fdata)
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


def json_api_test_link():
    "Fetches the alpine link response"
    return next((_l for _l in links_data() if _l["link_id"] == CLINK["id"]))


def post_put_matcher(request):
    "Creates the Responses for POST and PUT requests"
    resp = requests.Response()
    if request.method == "POST":
        if request.path_url.endswith("/projects"):
            # Now verify the data
            _data = request.json()
            if _data["name"] == "API_TEST":
                resp.status_code = 200
                resp.json = json_api_test_project
                return resp
            elif _data["name"] == "DUPLICATE":
                resp.status_code = 409
                resp.json = lambda: dict(
                    message="Project 'DUPLICATE' already exists", status=409
                )
                return resp
        elif request.path_url.endswith(f"/{CPROJECT['id']}/close"):
            _returned = json_api_test_project()
            _returned.update(status="closed")
            resp.status_code = 204
            resp.json = lambda: _returned
            return resp
        elif request.path_url.endswith(f"/{CPROJECT['id']}/open"):
            _returned = json_api_test_project()
            _returned.update(status="opened")
            resp.status_code = 204
            resp.json = lambda: _returned
            return resp
        elif request.path_url.endswith(f"/{CPROJECT['id']}/nodes"):
            _data = request.json()
            if not any(x in _data for x in ("compute_id", "name", "node_type")):
                resp.status_code == 400
                resp.json = lambda: dict(message="Invalid request", status=400)
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
            resp.json = lambda: _returned
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
            resp.json = lambda: _returned
            return resp
        elif request.path_url.endswith(f"/{CPROJECT['id']}/nodes/{CNODE['id']}/stop"):
            _returned = json_api_test_node()
            _returned.update(status="stopped")
            resp.status_code = 200
            resp.json = lambda: _returned
            return resp
        elif request.path_url.endswith(
            f"/{CPROJECT['id']}/nodes/{CNODE['id']}/suspend"
        ):
            _returned = json_api_test_node()
            _returned.update(status="suspended")
            resp.status_code = 200
            resp.json = lambda: _returned
            return resp
        elif request.path_url.endswith(f"/{CPROJECT['id']}/links"):
            _data = request.json()
            nodes = _data.get("nodes")
            if len(nodes) != 2:
                resp.status_code = 400
                resp.url = request.path_url
                resp.json = lambda: dict(message="Bad Request", status=400)
                return resp
            elif nodes[0]["node_id"] == nodes[1]["node_id"]:
                resp.status_code = 409
                resp.url = request.path_url
                resp.json = lambda: dict(message="Cannot connect to itself", status=409)
                return resp
            _returned = json_api_test_link()
            resp.status_code = 201
            if any(x for x in nodes if x["node_id"] == CNODE["id"]):
                resp.json = lambda: _returned
            else:
                _returned.update(**_data)
                _returned.update(link_id="NEW_LINK_ID")
                resp.json = lambda: _returned
            return resp
    elif request.method == "PUT":
        if request.path_url.endswith(f"/{CPROJECT['id']}"):
            _data = request.json()
            _returned = json_api_test_project()
            resp.status_code = 200
            resp.json = lambda: {**_returned, **_data}
            return resp
    return None


class Gns3ConnectorMock(Gns3Connector):
    def _create_session(self):
        self.session = requests.Session()
        self.adapter = requests_mock.Adapter()
        self.session.mount("mock", self.adapter)
        self.session.headers["Accept"] = "application/json"
        if self.user:
            self.session.auth = (self.user, self.cred)

        # Apply responses
        self._apply_responses()

    def _apply_responses(self):
        # Record the API expected responses
        # Version
        self.adapter.register_uri(
            "GET", f"{self.base_url}/version", json=version_data()
        )
        # Templates
        self.adapter.register_uri(
            "GET", f"{self.base_url}/templates", json=templates_data()
        )
        self.adapter.register_uri(
            "GET",
            f"{self.base_url}/templates/{CTEMPLATE['id']}",
            json=next(
                (_t for _t in templates_data() if _t["template_id"] == CTEMPLATE["id"])
            ),
        )
        self.adapter.register_uri(
            "GET",
            f"{self.base_url}/templates/7777-4444-0000",
            json={"message": "Template ID 7777-4444-0000 doesn't exist", "status": 404},
            status_code=404,
        )
        ############
        # Projects #
        ############
        self.adapter.register_uri(
            "GET", f"{self.base_url}/projects", json=projects_data()
        )
        self.adapter.register_uri(
            "GET",
            f"{self.base_url}/projects/{CPROJECT['id']}",
            json=json_api_test_project(),
        )
        self.adapter.register_uri(
            "GET",
            f"{self.base_url}/projects/{CPROJECT['id']}/stats",
            json={"drawings": 0, "links": 4, "nodes": 6, "snapshots": 0},
        )
        # Extra project
        self.adapter.register_uri(
            "GET",
            f"{self.base_url}/projects/c9dc56bf-37b9-453b-8f95-2845ce8908e3/stats",
            json={"drawings": 0, "links": 9, "nodes": 10, "snapshots": 0},
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
class Gns3ConnectorMockStopped(Gns3ConnectorMock):
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
class Gns3ConnectorMockSuspended(Gns3ConnectorMock):
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
def gns3_server():
    return Gns3ConnectorMock(url=BASE_URL)


class TestGns3Connector:
    def test_get_version(self, gns3_server):
        assert dict(local=True, version="2.2.0") == gns3_server.get_version()

    def test_get_templates(self, gns3_server):
        response = gns3_server.get_templates()
        for index, n in enumerate(
            [
                ("IOU-L3", "iou", "router"),
                ("IOU-L2", "iou", "switch"),
                ("vEOS", "qemu", "router"),
                ("alpine", "docker", "guest"),
                ("Cloud", "cloud", "guest"),
                ("NAT", "nat", "guest"),
                ("VPCS", "vpcs", "guest"),
                ("Ethernet switch", "ethernet_switch", "switch"),
                ("Ethernet hub", "ethernet_hub", "switch"),
                ("Frame Relay switch", "frame_relay_switch", "switch"),
                ("ATM switch", "atm_switch", "switch"),
            ]
        ):
            assert n[0] == response[index]["name"]
            assert n[1] == response[index]["template_type"]
            assert n[2] == response[index]["category"]

    def test_get_template_by_name(self, gns3_server):
        response = gns3_server.get_template(name="alpine")
        assert "alpine" == response["name"]
        assert "docker" == response["template_type"]
        assert "guest" == response["category"]

    def test_get_template_by_id(self, gns3_server):
        response = gns3_server.get_template(template_id=CTEMPLATE["id"])
        assert "alpine" == response["name"]
        assert "docker" == response["template_type"]
        assert "guest" == response["category"]

    def test_error_get_template_no_params(self, gns3_server):
        with pytest.raises(
            ValueError, match="Must provide either a name or template_id"
        ):
            gns3_server.get_template()

    def test_error_template_id_not_found(self, gns3_server):
        with pytest.raises(
            HTTPError, match="404: Template ID 7777-4444-0000 doesn't exist"
        ):
            gns3_server.get_template(template_id="7777-4444-0000")

    def test_error_template_name_not_found(self, gns3_server):
        # NOTE: Should it give the same output as the one above?
        response = gns3_server.get_template(name="NOTE_FOUND")
        assert response is None

    def test_get_projects(self, gns3_server):
        response = gns3_server.get_projects()
        for index, n in enumerate(
            [
                ("test2", "test2.gns3", "closed"),
                ("API_TEST", "test_api1.gns3", "opened"),
            ]
        ):
            assert n[0] == response[index]["name"]
            assert n[1] == response[index]["filename"]
            assert n[2] == response[index]["status"]

    def test_get_project_by_name(self, gns3_server):
        response = gns3_server.get_project(name="API_TEST")
        assert "API_TEST" == response["name"]
        assert "test_api1.gns3" == response["filename"]
        assert "opened" == response["status"]

    def test_get_project_by_id(self, gns3_server):
        response = gns3_server.get_project(project_id=CPROJECT["id"])
        assert "API_TEST" == response["name"]
        assert "test_api1.gns3" == response["filename"]
        assert "opened" == response["status"]

    def test_error_get_project_no_params(self, gns3_server):
        with pytest.raises(
            ValueError, match="Must provide either a name or project_id"
        ):
            gns3_server.get_project()

    def test_error_project_id_not_found(self, gns3_server):
        with pytest.raises(
            HTTPError, match="404: Project ID 7777-4444-0000 doesn't exist"
        ):
            gns3_server.get_project(project_id="7777-4444-0000")

    def test_error_project_name_not_found(self, gns3_server):
        # NOTE: Should it give the same output as the one above?
        response = gns3_server.get_project(name="NOTE_FOUND")
        assert response is None

    def test_get_nodes(self, gns3_server):
        response = gns3_server.get_nodes(project_id=CPROJECT["id"])
        for index, n in enumerate(
            [
                ("Ethernetswitch-1", "ethernet_switch"),
                ("IOU1", "iou"),
                ("IOU2", "iou"),
                ("vEOS", "qemu"),
                ("alpine-1", "docker"),
                ("Cloud-1", "cloud"),
            ]
        ):
            assert n[0] == response[index]["name"]
            assert n[1] == response[index]["node_type"]

    def test_get_node_by_id(self, gns3_server):
        response = gns3_server.get_node(project_id=CPROJECT["id"], node_id=CNODE["id"])
        assert response["name"] == "alpine-1"
        assert response["node_type"] == "docker"
        assert response["console"] == 5005

    def test_error_node_not_found(self, gns3_server):
        with pytest.raises(
            HTTPError, match="404: Node ID 7777-4444-0000 doesn't exist"
        ):
            gns3_server.get_node(project_id=CPROJECT["id"], node_id="7777-4444-0000")

    def test_get_links(self, gns3_server):
        response = gns3_server.get_links(project_id=CPROJECT["id"])
        assert response[0]["link_type"] == "ethernet"

    def test_get_link_by_id(self, gns3_server):
        response = gns3_server.get_link(project_id=CPROJECT["id"], link_id=CLINK["id"])
        assert response["link_type"] == "ethernet"
        assert response["project_id"] == CPROJECT["id"]
        assert response["suspend"] is False

    def test_error_link_not_found(self, gns3_server):
        with pytest.raises(
            HTTPError, match="404: Link ID 7777-4444-0000 doesn't exist"
        ):
            gns3_server.get_link(project_id=CPROJECT["id"], link_id="7777-4444-0000")

    def test_create_project(self, gns3_server):
        response = gns3_server.create_project(name="API_TEST")
        assert "API_TEST" == response["name"]
        assert "opened" == response["status"]

    def test_error_create_duplicate_project(self, gns3_server):
        with pytest.raises(HTTPError, match="409: Project 'DUPLICATE' already exists"):
            gns3_server.create_project(name="DUPLICATE")

    def test_error_create_project_with_no_name(self, gns3_server):
        with pytest.raises(ValueError, match="Parameter 'name' is mandatory"):
            gns3_server.create_project(dummy="DUMMY")

    def test_delete_project(self, gns3_server):
        response = gns3_server.delete_project(project_id=CPROJECT["id"])
        assert response is None

    def test_projects_summary(self, gns3_server):
        projects_summary = gns3_server.projects_summary(is_print=False)
        assert (
            str(projects_summary)
            == "[('test2', 'c9dc56bf-37b9-453b-8f95-2845ce8908e3', 10, 9, 'closed'), "
            "('API_TEST', '4b21dfb3-675a-4efa-8613-2f7fb32e76fe', 6, 4, 'opened')]"
        )

    def test_projects_summary_print(self, capsys, gns3_server):
        gns3_server.projects_summary(is_print=True)
        captured = capsys.readouterr()
        assert captured.out == (
            "test2: c9dc56bf-37b9-453b-8f95-2845ce8908e3 -- Nodes: 10 -- Links: 9 -- "
            "Status: closed\nAPI_TEST: 4b21dfb3-675a-4efa-8613-2f7fb32e76fe -- Nodes: "
            "6 -- Links: 4 -- Status: opened\n"
        )

    def test_templates_summary(self, gns3_server):
        templates_summary = gns3_server.templates_summary(is_print=False)
        assert (
            str(templates_summary)
            == "[('IOU-L3', '8504c605-7914-4a8f-9cd4-a2638382db0e', 'iou', False, "
            "'telnet', 'router'), ('IOU-L2', '92cccfb2-6401-48f2-8964-3c75323be3cb', "
            "'iou', False, 'telnet', 'switch'), ('vEOS', 'c6203d4b-d0ce-4951-bf18-"
            "c44369d46804', 'qemu', False, 'telnet', 'router'), ('alpine', "
            "'847e5333-6ac9-411f-a400-89838584371b', 'docker', False, 'telnet', 'guest'"
            "), ('Cloud', '39e257dc-8412-3174-b6b3-0ee3ed6a43e9', 'cloud', True, 'N/A'"
            ", 'guest'), ('NAT', 'df8f4ea9-33b7-3e96-86a2-c39bc9bb649c', 'nat', True, '"
            "N/A', 'guest'), ('VPCS', '19021f99-e36f-394d-b4a1-8aaa902ab9cc', 'vpcs', "
            "True, 'N/A', 'guest'), ('Ethernet switch', '1966b864-93e7-32d5-965f-"
            "001384eec461', 'ethernet_switch', True, 'none', 'switch'), ('Ethernet hub"
            "', 'b4503ea9-d6b6-3695-9fe4-1db3b39290b0', 'ethernet_hub', True, 'N/A', '"
            "switch'), ('Frame Relay switch', 'dd0f6f3a-ba58-3249-81cb-a1dd88407a47', "
            "'frame_relay_switch', True, 'N/A', 'switch'), ('ATM switch', "
            "'aaa764e2-b383-300f-8a0e-3493bbfdb7d2', 'atm_switch', True, 'N/A', 'switch"
            "')]"
        )

    def test_templates_summary_print(self, capsys, gns3_server):
        gns3_server.templates_summary(is_print=True)
        captured = capsys.readouterr()
        assert captured.out == (
            "IOU-L3: 8504c605-7914-4a8f-9cd4-a2638382db0e -- Type: iou -- Builtin: "
            "False -- Console: telnet -- Category: router\nIOU-L2: "
            "92cccfb2-6401-48f2-8964-3c75323be3cb -- Type: iou -- Builtin: False -- "
            "Console: telnet -- Category: switch\nvEOS: c6203d4b-d0ce-4951-bf18-"
            "c44369d46804 -- Type: qemu -- Builtin: False -- Console: telnet -- "
            "Category: router\nalpine: 847e5333-6ac9-411f-a400-89838584371b -- Type: "
            "docker -- Builtin: False -- Console: telnet -- Category: guest\nCloud: "
            "39e257dc-8412-3174-b6b3-0ee3ed6a43e9 -- Type: cloud -- Builtin: True -- "
            "Console: N/A -- Category: guest\nNAT: df8f4ea9-33b7-3e96-86a2-"
            "c39bc9bb649c -- Type: nat -- Builtin: True -- Console: N/A -- Category: "
            "guest\nVPCS: 19021f99-e36f-394d-b4a1-8aaa902ab9cc -- Type: vpcs -- Builtin"
            ": True -- Console: N/A -- Category: guest\nEthernet switch: "
            "1966b864-93e7-32d5-965f-001384eec461 -- Type: ethernet_switch -- Builtin: "
            "True -- Console: none -- Category: switch\nEthernet hub: "
            "b4503ea9-d6b6-3695-9fe4-1db3b39290b0 -- Type: ethernet_hub -- Builtin: "
            "True -- Console: N/A -- Category: switch\nFrame Relay switch: "
            "dd0f6f3a-ba58-3249-81cb-a1dd88407a47 -- Type: frame_relay_switch -- "
            "Builtin: True -- Console: N/A -- Category: switch\nATM switch: "
            "aaa764e2-b383-300f-8a0e-3493bbfdb7d2 -- Type: atm_switch -- Builtin: True "
            "-- Console: N/A -- Category: switch\n"
        )

    def test_wrong_server_url(self, gns3_server):
        gns3_server.base_url = "WRONG URL"
        with pytest.raises(requests.exceptions.InvalidURL):
            gns3_server.get_version()


@pytest.fixture(scope="class")
def api_test_link(gns3_server):
    link = Link(link_id=CLINK["id"], connector=gns3_server, project_id=CPROJECT["id"])
    link.get()
    return link


class TestLink:
    def test_instatiation(self):
        for index, link_data in enumerate(links_data()):
            assert links.LINKS_REPR[index] == repr(Link(**link_data))

    def test_error_instatiation_bad_link_type(self):
        with pytest.raises(ValueError, match="Not a valid link_type - dummy"):
            Link(link_type="dummy")

    @pytest.mark.parametrize(
        "params,expected",
        [
            (
                {"link_id": "SOME_ID", "project_id": "SOME_ID"},
                "Gns3Connector not assigned under 'connector'",
            ),
            (
                {"link_id": "SOME_ID", "connector": "SOME_CONN"},
                "Need to submit project_id",
            ),
            (
                {"project_id": "SOME_ID", "connector": "SOME_CONN"},
                "Need to submit link_id",
            ),
        ],
    )
    def test_error_get_with_no_required_param(self, params, expected):
        link = Link(**params)
        with pytest.raises(ValueError, match=expected):
            link.get()

    def test_get(self, api_test_link):
        assert api_test_link.link_type == "ethernet"
        assert api_test_link.filters == {}
        assert api_test_link.capturing is False
        assert api_test_link.suspend is False
        assert api_test_link.nodes[-1]["node_id"] == CNODE["id"]
        assert api_test_link.nodes[-1]["adapter_number"] == 0
        assert api_test_link.nodes[-1]["port_number"] == 0

    @pytest.mark.parametrize(
        "params,expected",
        [
            ({"project_id": "SOME_ID"}, "Gns3Connector not assigned under 'connector'"),
            ({"connector": "SOME_CONN"}, "Need to submit project_id"),
        ],
    )
    def test_error_create_with_no_required_param(self, params, expected):
        link = Link(**params)
        with pytest.raises(ValueError, match=expected):
            link.create()

    def test_create(self, gns3_server):
        _link_data = [
            {
                "adapter_number": 2,
                "port_number": 0,
                "node_id": "8283b923-df0e-4bc1-8199-be6fea40f500",
            },
            {"adapter_number": 0, "port_number": 0, "node_id": CNODE["id"]},
        ]
        link = Link(connector=gns3_server, project_id=CPROJECT["id"], nodes=_link_data)
        link.create()
        assert link.link_type == "ethernet"
        assert link.filters == {}
        assert link.capturing is False
        assert link.suspend is False
        assert link.nodes[-1]["node_id"] == CNODE["id"]

    def test_error_create_with_incomplete_node_data(self, gns3_server):
        _link_data = [{"adapter_number": 0, "port_number": 0, "node_id": CNODE["id"]}]
        link = Link(connector=gns3_server, project_id=CPROJECT["id"], nodes=_link_data)
        with pytest.raises(HTTPError, match="400"):
            link.create()

    def test_error_create_connecting_to_itself(self, gns3_server):
        _link_data = [
            {"adapter_number": 2, "port_number": 0, "node_id": CNODE["id"]},
            {"adapter_number": 0, "port_number": 0, "node_id": CNODE["id"]},
        ]
        link = Link(connector=gns3_server, project_id=CPROJECT["id"], nodes=_link_data)
        with pytest.raises(HTTPError, match="409: Cannot connect to itself"):
            link.create()

    def test_delete(self, api_test_link):
        api_test_link.delete()
        assert api_test_link.project_id is None
        assert api_test_link.link_id is None


@pytest.fixture(scope="class")
def api_test_node(gns3_server):
    node = Node(name="alpine-1", connector=gns3_server, project_id=CPROJECT["id"])
    # node.get()
    return node


class TestNode:
    def test_instatiation(self):
        for index, node_data in enumerate(nodes_data()):
            assert nodes.NODES_REPR[index] == repr(Node(**node_data))

    @pytest.mark.parametrize(
        "param,expected",
        [
            ({"node_type": "dummy"}, "Not a valid node_type - dummy"),
            ({"console_type": "dummy"}, "Not a valid console_type - dummy"),
            ({"status": "dummy"}, "Not a valid status - dummy"),
        ],
    )
    def test_error_link_instatiation_bad_param(self, param, expected):
        with pytest.raises(ValueError, match=expected):
            Node(**param)

    @pytest.mark.parametrize(
        "params,expected",
        [
            (
                {"node_id": "SOME_ID", "project_id": "SOME_ID"},
                "Gns3Connector not assigned under 'connector'",
            ),
            (
                {"node_id": "SOME_ID", "connector": "SOME_CONN"},
                "Need to submit project_id",
            ),
            (
                {"project_id": "SOME_ID", "connector": "SOME_CONN"},
                "Need to either submit node_id or name",
            ),
        ],
    )
    def test_error_get_with_no_required_param(self, params, expected):
        node = Node(**params)
        with pytest.raises(ValueError, match=expected):
            node.get()

    def test_get(self, api_test_node):
        api_test_node.get()
        assert "alpine-1" == api_test_node.name
        assert "started" == api_test_node.status
        assert "docker" == api_test_node.node_type
        assert "alpine:latest" == api_test_node.properties["image"]

    def test_get_links(self, api_test_node):
        api_test_node.get_links()
        assert "ethernet" == api_test_node.links[0].link_type
        assert 2 == api_test_node.links[0].nodes[0]["adapter_number"]
        assert 0 == api_test_node.links[0].nodes[0]["port_number"]

    def test_start(self, api_test_node):
        api_test_node.start()
        assert "alpine-1" == api_test_node.name
        assert "started" == api_test_node.status

    def test_stop(self, api_test_node):
        api_test_node.stop()
        assert "alpine-1" == api_test_node.name
        assert "stopped" == api_test_node.status

    def test_suspend(self, api_test_node):
        api_test_node.suspend()
        assert "alpine-1" == api_test_node.name
        assert "suspended" == api_test_node.status

    def test_reload(self, api_test_node):
        api_test_node.reload()
        assert "alpine-1" == api_test_node.name
        assert "started" == api_test_node.status

    @pytest.mark.parametrize(
        "param", [{"template": CTEMPLATE["name"]}, {"template_id": CTEMPLATE["id"]}]
    )
    def test_create(self, param, gns3_server):
        node = Node(
            name="alpine-1",
            node_type="docker",
            connector=gns3_server,
            project_id=CPROJECT["id"],
            **param,
        )
        node.create()
        assert "alpine-1" == node.name
        assert "started" == node.status
        assert "docker" == node.node_type
        assert "alpine:latest" == node.properties["image"]
        assert node.properties["console_http_port"] == 80

    def test_create_override_properties(self, gns3_server):
        node = Node(
            name="alpine-1",
            node_type="docker",
            connector=gns3_server,
            project_id=CPROJECT["id"],
            template=CTEMPLATE["name"],
        )
        node.create(extra_properties={"console_http_port": 8080})
        assert "alpine-1" == node.name
        # NOTE: The image name of alpine in teh template is different than the one
        # defined on the node properties, which has the version alpine:latest.
        # Need to keep an eye
        assert "alpine" == node.properties["image"]
        assert node.properties["console_http_port"] == 8080

    def test_error_create_with_invalid_parameter_type(self, gns3_server):
        with pytest.raises(ValidationError):
            Node(
                name="alpine-1",
                node_type="docker",
                template=CTEMPLATE["name"],
                connector=gns3_server,
                project_id=CPROJECT["id"],
                compute_id=None,
            )

    @pytest.mark.parametrize(
        "params,expected",
        [
            ({"project_id": "SOME_ID"}, "Gns3Connector not assigned under 'connector'"),
            ({"connector": "SOME_CONN"}, "Need to submit project_id"),
            (
                {
                    "connector": "SOME_CONN",
                    "project_id": "SOME_ID",
                    "compute_id": "SOME_ID",
                },
                "Need to submit name",
            ),
            (
                {
                    "connector": "SOME_CONN",
                    "project_id": "SOME_ID",
                    "compute_id": "SOME_ID",
                    "name": "SOME_NAME",
                },
                "Need to submit node_type",
            ),
            (
                {
                    "connector": "SOME_CONN",
                    "project_id": "SOME_ID",
                    "compute_id": "SOME_ID",
                    "name": "SOME_NAME",
                    "node_type": "docker",
                    "node_id": "SOME_ID",
                },
                "Node already created",
            ),
            (
                {
                    "connector": "CHANGE_TO_FIXTURE",
                    "project_id": "SOME_ID",
                    "compute_id": "SOME_ID",
                    "name": "SOME_NAME",
                    "node_type": "docker",
                },
                "You must provide template or template_id",
            ),
        ],
    )
    def test_error_create_with_no_required_param(self, params, expected, gns3_server):
        node = Node(**params)
        if node.connector == "CHANGE_TO_FIXTURE":
            node.connector = gns3_server
        with pytest.raises(ValueError, match=expected):
            node.create()

    def test_delete(self, api_test_node):
        api_test_node.delete()
        assert api_test_node.project_id is None
        assert api_test_node.node_id is None
        assert api_test_node.name is None


@pytest.fixture(scope="class")
def api_test_project(gns3_server):
    project = Project(name="API_TEST", connector=gns3_server)
    project.get()
    return project


class TestProject:
    def test_instatiation(self):
        for index, project_data in enumerate(projects_data()):
            assert projects.PROJECTS_REPR[index] == repr(Project(**project_data))

    def test_error_instatiation_bad_status(self):
        with pytest.raises(ValueError, match="status must be opened or closed"):
            Project(status="dummy")

    def test_create(self, gns3_server):
        api_test_project = Project(name="API_TEST", connector=gns3_server)
        api_test_project.create()
        assert "API_TEST" == api_test_project.name
        assert "opened" == api_test_project.status
        assert False is api_test_project.auto_close

    @pytest.mark.parametrize(
        "params,expected",
        [
            ({"name": "SOME_NAME"}, "Gns3Connector not assigned under 'connector'"),
            ({"connector": "SOME_CONN"}, "Need to submit project name"),
        ],
    )
    def test_error_create_with_no_required_param(self, params, expected):
        project = Project(**params)
        with pytest.raises(ValueError, match=expected):
            project.create()

    def test_delete(self, gns3_server):
        api_test_project = Project(name="API_TEST", connector=gns3_server)
        api_test_project.create()
        resp = api_test_project.delete()
        assert resp is None

    def test_get(self, api_test_project):
        assert "API_TEST" == api_test_project.name
        assert "opened" == api_test_project.status
        assert {
            "drawings": 0,
            "links": 4,
            "nodes": 6,
            "snapshots": 0,
        } == api_test_project.stats

    @pytest.mark.parametrize(
        "params,expected",
        [
            ({"project_id": "SOME_ID"}, "Gns3Connector not assigned under 'connector'"),
            ({"connector": "SOME_CONN"}, "Need to submit either project_id or name"),
        ],
    )
    def test_error_get_with_no_required_param(self, params, expected):
        project = Project(**params)
        with pytest.raises(ValueError, match=expected):
            project.get()

    def test_update(self, api_test_project):
        api_test_project.update(filename="file_updated.gns3")
        assert "API_TEST" == api_test_project.name
        assert "opened" == api_test_project.status
        assert "file_updated.gns3" == api_test_project.filename

    @pytest.mark.parametrize(
        "params,expected",
        [
            ({"project_id": "SOME_ID"}, "Gns3Connector not assigned under 'connector'"),
            ({"connector": "SOME_CONN"}, "Need to submit project_id"),
        ],
    )
    def test_error_update_with_no_required_param(self, params, expected):
        project = Project(**params)
        with pytest.raises(ValueError, match=expected):
            project.update()

    def test_open(self, api_test_project):
        api_test_project.open()
        assert "API_TEST" == api_test_project.name
        assert "opened" == api_test_project.status

    def test_close(self, api_test_project):
        api_test_project.close()
        assert "API_TEST" == api_test_project.name
        assert "closed" == api_test_project.status

    def test_get_stats(self, api_test_project):
        api_test_project.get_stats()
        assert {
            "drawings": 0,
            "links": 4,
            "nodes": 6,
            "snapshots": 0,
        } == api_test_project.stats

    def test_get_nodes(self, api_test_project):
        api_test_project.get_nodes()
        for index, n in enumerate(
            [
                ("Ethernetswitch-1", "ethernet_switch"),
                ("IOU1", "iou"),
                ("IOU2", "iou"),
                ("vEOS", "qemu"),
                ("alpine-1", "docker"),
                ("Cloud-1", "cloud"),
            ]
        ):
            assert n[0] == api_test_project.nodes[index].name
            assert n[1] == api_test_project.nodes[index].node_type

    def test_error_get_node_no_required_params(self, api_test_project):
        with pytest.raises(ValueError, match="name or node_ide must be provided"):
            api_test_project.get_node()

    def test_get_links(self, api_test_project):
        api_test_project.get_links()
        assert "ethernet" == api_test_project.links[0].link_type

    def test_error_get_link_not_found(self, api_test_project):
        assert api_test_project.get_link(link_id="DUMMY_ID") is None

    # TODO: Need to make a way to dynamically change the status of the nodes to started
    # when the inner method `get_nodes` hits again the server REST endpoint
    def test_start_nodes(self, api_test_project):
        api_test_project.start_nodes(poll_wait_time=0)
        for node in api_test_project.nodes:
            assert node.status == "started"

    def test_stop_nodes(self):
        project = Project(
            name="API_TEST",
            connector=Gns3ConnectorMockStopped(url=BASE_URL),
            project_id=CPROJECT["id"],
        )
        project.stop_nodes(poll_wait_time=0)
        for node in project.nodes:
            assert node.status == "stopped"

    def test_reload_nodes(self, api_test_project):
        api_test_project.reload_nodes(poll_wait_time=0)
        for node in api_test_project.nodes:
            assert node.status == "started"

    def test_suspend_nodes(self):
        project = Project(
            name="API_TEST",
            connector=Gns3ConnectorMockSuspended(url=BASE_URL),
            project_id=CPROJECT["id"],
        )
        project.suspend_nodes(poll_wait_time=0)
        for node in project.nodes:
            assert node.status == "suspended"

    def test_nodes_summary(self, api_test_project):
        nodes_summary = api_test_project.nodes_summary(is_print=False)
        assert str(nodes_summary) == (
            "[('Ethernetswitch-1', 'started', 5000, "
            "'da28e1c0-9465-4f7c-b42c-49b2f4e1c64d'), ('IOU1', 'started', 5001, "
            "'de23a89a-aa1f-446a-a950-31d4bf98653c'), ('IOU2', 'started', 5002, "
            "'0d10d697-ef8d-40af-a4f3-fafe71f5458b'), ('vEOS', 'started', 5003, "
            "'8283b923-df0e-4bc1-8199-be6fea40f500'), ('alpine-1', 'started', 5005, "
            "'ef503c45-e998-499d-88fc-2765614b313e'), ('Cloud-1', 'started', None, "
            "'cde85a31-c97f-4551-9596-a3ed12c08498')]"
        )

    def test_nodes_summary_print(self, capsys, api_test_project):
        api_test_project.nodes_summary(is_print=True)
        captured = capsys.readouterr()
        assert captured.out == (
            "Ethernetswitch-1: started -- Console: 5000 -- ID: "
            "da28e1c0-9465-4f7c-b42c-49b2f4e1c64d\nIOU1: started -- Console: 5001 -- ID"
            ": de23a89a-aa1f-446a-a950-31d4bf98653c\nIOU2: started -- Console: 5002 -- "
            "ID: 0d10d697-ef8d-40af-a4f3-fafe71f5458b\nvEOS: started -- Console: 5003 "
            "-- ID: 8283b923-df0e-4bc1-8199-be6fea40f500\nalpine-1: started -- Console"
            ": 5005 -- ID: ef503c45-e998-499d-88fc-2765614b313e\nCloud-1: started -- "
            "Console: None -- ID: cde85a31-c97f-4551-9596-a3ed12c08498\n"
        )

    def test_nodes_inventory(self, api_test_project):
        nodes_inventory = api_test_project.nodes_inventory()
        assert {
            "server": "gns3server",
            "name": "alpine-1",
            "console_port": 5005,
            "type": "docker",
        } == nodes_inventory["alpine-1"]

    def test_links_summary(self, api_test_project):
        api_test_project.get_links()
        links_summary = api_test_project.links_summary(is_print=False)
        assert str(links_summary) == (
            "[('IOU1', 'Ethernet0/0', 'Ethernetswitch-1', 'Ethernet1'), ('IOU1', "
            "'Ethernet1/0', 'IOU2', 'Ethernet1/0'), ('vEOS', 'Management1', "
            "'Ethernetswitch-1', 'Ethernet0'), ('vEOS', 'Ethernet1', 'alpine-1', "
            "'eth0'), ('Cloud-1', 'eth1', 'Ethernetswitch-1', 'Ethernet7')]"
        )

    def test_links_summary_print(self, capsys, api_test_project):
        api_test_project.links_summary(is_print=True)
        captured = capsys.readouterr()
        assert captured.out == (
            "IOU1: Ethernet0/0 ---- Ethernetswitch-1: Ethernet1\nIOU1: Ethernet1/0 "
            "---- IOU2: Ethernet1/0\nvEOS: Management1 ---- Ethernetswitch-1: Ethernet0"
            "\nvEOS: Ethernet1 ---- alpine-1: eth0\nCloud-1: eth1 ---- Ethernetswitch-"
            "1: Ethernet7\n"
        )

    def test_get_node_by_name(self, api_test_project):
        switch = api_test_project.get_node(name="IOU1")
        assert switch.name == "IOU1"
        assert switch.status == "started"
        assert switch.console == 5001

    def test_get_node_by_id(self, api_test_project):
        host = api_test_project.get_node(node_id=CNODE["id"])
        assert host.name == "alpine-1"
        assert host.status == "started"
        assert host.console == 5005

    def test_get_link_by_id(self, api_test_project):
        link = api_test_project.get_link(link_id=CLINK["id"])
        assert "ethernet" == link.link_type

    def test_create_node(self, api_test_project):
        api_test_project.create_node(
            name="alpine-2", node_type="docker", template=CTEMPLATE["name"]
        )
        alpine2 = api_test_project.get_node(name="alpine-2")
        assert alpine2.console == 5077
        assert alpine2.name == "alpine-2"
        assert alpine2.node_type == "docker"
        assert alpine2.node_id == "NEW_NODE_ID"

    def test_error_create_node_with_equal_name(self, api_test_project):
        with pytest.raises(ValueError, match="Node with equal name found"):
            api_test_project.create_node(
                name="alpine-1",
                node_type="docker",
                template=CTEMPLATE["name"],
                connector=gns3_server,
                project_id=CPROJECT["id"],
            )

    def test_create_link(self, api_test_project):
        api_test_project.create_link("IOU1", "Ethernet1/1", "vEOS", "Ethernet2")
        link = api_test_project.get_link(link_id="NEW_LINK_ID")
        assert link.link_id == "NEW_LINK_ID"
        assert link.link_type == "ethernet"

    @pytest.mark.parametrize(
        "link,expected",
        [
            (
                ("IOU1", "Ethernet77/1", "vEOS", "Ethernet2"),
                "port_a: Ethernet77/1 not found",
            ),
            (
                ("IOU1", "Ethernet1/1", "vEOS", "Ethernet77"),
                "port_b: Ethernet77 not found",
            ),
            (("IOU77", "Ethernet1/1", "vEOS", "Ethernet2"), "node_a: IOU77 not found"),
            (
                ("IOU1", "Ethernet1/1", "vEOS77", "Ethernet2"),
                "node_b: vEOS77 not found",
            ),
            (("IOU1", "Ethernet1/0", "vEOS", "Ethernet2"), "At least one port is used"),
        ],
    )
    def test_error_create_link_with_invalid_param(
        self, api_test_project, link, expected
    ):
        with pytest.raises(ValueError, match=expected):
            api_test_project.create_link(*link)
