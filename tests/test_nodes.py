import json
import pytest
from pathlib import Path
from gns3fy.services import get_nodes, search_node, create_node, delete_node


DATA_FILES = Path(__file__).resolve().parent / "data"


def nodes_new_data():
    with open(DATA_FILES / "nodes_new.json") as fdata:
        data = json.load(fdata)
    return data


class TestNodes:
    def test_get_nodes(self, project_mock):
        nodes = get_nodes(project_mock)
        for index, n in enumerate(
            [
                ("Ethernetswitch-1", "ethernet_switch", "started"),
                ("vEOS", "qemu", "started"),
                ("alpine-1", "docker", "started"),
                ("Cloud-1", "cloud", "started"),
            ]
        ):
            assert n[0] == nodes[index].name
            assert n[1] == nodes[index].node_type
            assert n[2] == nodes[index].status

    @pytest.mark.parametrize(
        "params,expected",
        [
            (({"name": "alpine-1"}), ("alpine-1", "docker", "started")),
            (
                ({"node_id": "8283b923-df0e-4bc1-8199-be6fea40f500"}),
                ("vEOS", "qemu", "started"),
            ),
        ],
        ids=["by_name", "by_id"],
    )
    def test_search_node(self, project_mock, params, expected):
        node = search_node(project_mock, **params)
        # Refresh
        node.get()
        assert expected[0] == node.name
        assert expected[1] == node.node_type
        assert expected[2] == node.status

    @pytest.mark.parametrize(
        "params",
        [
            (("dummy", "name")),
            ((None, None)),
        ],
        ids=["node_not_found", "invalid_query"],
    )
    def test_search_node_error(self, project_mock, params):
        if params[1] == "name":
            node = search_node(project_mock, name=params[0])
            assert node is None
        elif params[1] is None:
            with pytest.raises(
                ValueError, match="Need to submit either name or node_id"
            ):
                search_node(project_mock, params[0], params[1])

    def test_create_node(self, project_mock):
        new_data_node = nodes_new_data()[0]
        new_node = create_node(project_mock, **new_data_node)
        assert new_node.name == "new_node"
        assert new_node.status == "started"
        assert new_node.console == 5007
        assert new_node.node_id == "7777777-4444-node"

    def test_create_node_already_exists(self, project_mock):
        with pytest.raises(
            ValueError, match="Node with same name already exists: alpine-1"
        ):
            create_node(project_mock, "alpine-1", "alpine")

    @pytest.mark.parametrize(
        "params",
        [
            (({"name": "alpine-1"})),
            (({"node_id": "ef503c45-e998-499d-88fc-2765614b313e"})),
        ],
        ids=["by_name", "by_id"],
    )
    def test_delete_node(self, project_mock, params):
        response = delete_node(project_mock, **params)
        assert response is None

    @pytest.mark.parametrize(
        "params,expected",
        [
            ((None), ("Need to submit either name or node_id")),
            (("dummy"), ("Node not found")),
        ],
        ids=["none_args", "node_not_found"],
    )
    def test_delete_node_error(self, project_mock, params, expected):
        with pytest.raises(ValueError, match=expected):
            delete_node(project_mock, params)
