import json
import pytest
from pathlib import Path


DATA_FILES = Path(__file__).resolve().parent / "data"


def nodes_new_data():
    with open(DATA_FILES / "nodes_new.json") as fdata:
        data = json.load(fdata)
    return data


class TestNodes:
    def test_get_nodes(self, project_mock):
        project_mock.get()
        nodes = list(project_mock.nodes.values())
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

    def test_search_node(self, project_mock):
        node = project_mock.search_node(name="alpine-1")
        assert node.name == "alpine-1"
        assert node.node_type == "docker"
        assert node.status == "started"

    def test_search_node_not_found(self, project_mock):
        project_mock.get()
        node = project_mock.search_node(name="dummy")
        assert len(project_mock.nodes) > 0
        assert node is None

    def test_create_node(self, project_mock):
        new_data_node = nodes_new_data()[0]
        new_node = project_mock.create_node(**new_data_node)
        assert new_node.name == "new_node"
        assert new_node.status == "started"
        assert new_node.console == 5007
        assert new_node.node_id == "7777777-4444-node"

    def test_create_node_already_exists(self, project_mock):
        with pytest.raises(ValueError, match="Node alpine-1 already created"):
            project_mock.create_node("alpine-1", "alpine")

    def test_delete_node(self, project_mock):
        response = project_mock.delete_node(name="alpine-1")
        assert response is True

    def test_delete_node_error(self, project_mock):
        with pytest.raises(ValueError, match="Node dummy not found"):
            project_mock.delete_node("dummy")
