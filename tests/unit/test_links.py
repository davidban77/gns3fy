import json
import pytest
from pathlib import Path
from gns3fy.links import get_links


DATA_FILES = Path(__file__).resolve().parent / "data"


def links_new_data():
    with open(DATA_FILES / "links_new.json") as fdata:
        data = json.load(fdata)
    return data


class Testlinks:
    def test_get_links_from_project(self, project_mock):
        project_mock.get()
        links = list(project_mock.links.values())
        for index, n in enumerate(
            [
                # ("d7dd01d6-9577-4076-b7f2-911b231044f8", "ethernet", "e1"),
                # ("cda8707a-79e2-4088-a5f8-c1664928453b", "ethernet", "e1/0"),
                ("fb27704f-7be5-4152-8ecd-1db6633b2bd9", "ethernet", "e0"),
                ("4d9f1235-7fd1-466b-ad26-0b4b08beb778", "ethernet", "eth0"),
                ("52cdd27d-fa97-47e7-ab99-ea810c20e614", "ethernet", "e7"),
            ]
        ):
            assert n[0] == links[index].link_id
            assert n[1] == links[index].link_type
            assert n[2] == links[index].nodes[-1].label["text"]

    def test_get_links_from_function(self, project_mock):
        links = get_links(project_mock._connector, project_mock.project_id)
        for index, n in enumerate(
            [
                ("fb27704f-7be5-4152-8ecd-1db6633b2bd9", "ethernet", "e0"),
                ("4d9f1235-7fd1-466b-ad26-0b4b08beb778", "ethernet", "eth0"),
                ("52cdd27d-fa97-47e7-ab99-ea810c20e614", "ethernet", "e7"),
            ]
        ):
            assert n[0] == links[index].link_id
            assert n[1] == links[index].link_type
            assert n[2] == links[index].nodes[-1].label["text"]

    def test_search_link(self, project_mock):
        link = project_mock.search_link(
            node_a="Cloud-1",
            port_a="eth1",
            node_b="Ethernetswitch-1",
            port_b="Ethernet7",
        )
        # Refresh
        link.get()
        assert link.link_id == "52cdd27d-fa97-47e7-ab99-ea810c20e614"
        assert link.link_type == "ethernet"
        assert link.suspend is False

    @pytest.mark.parametrize(
        "params,expected",
        [
            (
                (
                    {
                        "node_a": "Cloud-1",
                        "port_a": "eth1",
                        "node_b": "Ethernetswitch-1",
                        "port_b": "Ethernet77",
                    }
                ),
                ("port_b: Ethernet77 not found"),
            ),
            (
                (
                    {
                        "node_a": "Cloudish-1",
                        "port_a": "eth1",
                        "node_b": "Ethernetswitch-1",
                        "port_b": "Ethernet7",
                    }
                ),
                ("node_a: Cloudish-1 not found"),
            ),
        ],
        ids=["port_not_found", "node_not_found"],
    )
    def test_search_link_error(self, project_mock, params, expected):
        with pytest.raises(ValueError, match=expected):
            project_mock.search_link(**params)

    def test_create_link(self, project_mock):
        new_data_link = links_new_data()[0]
        new_link = project_mock.create_link(**new_data_link)
        assert new_link.link_type == "ethernet"
        assert new_link.suspend is False
        assert new_link.link_id == "7777777-4444-link"

    def test_create_link_already_exists(self, project_mock):
        with pytest.raises(
            ValueError,
            match="At least one port is used, ID: 52cdd27d-fa97-47e7-ab99-ea810c20e614",
        ):
            project_mock.create_link(
                node_a="Cloud-1",
                port_a="eth1",
                node_b="Ethernetswitch-1",
                port_b="Ethernet7",
            )

    def test_delete_link(self, project_mock):
        response = project_mock.delete_link(
            node_a="vEOS",
            port_a="Ethernet1",
            node_b="alpine-1",
            port_b="eth0",
        )
        assert response is True

    @pytest.mark.parametrize(
        "params,expected",
        [
            (
                (
                    {
                        "node_a": "Cloud-1",
                        "port_a": "eth1",
                        "node_b": "Ethernetswitch-1",
                        "port_b": "Ethernet77",
                    }
                ),
                ("port_b: Ethernet77 not found"),
            ),
            (
                (
                    {
                        "node_a": "Cloudish-1",
                        "port_a": "eth1",
                        "node_b": "Ethernetswitch-1",
                        "port_b": "Ethernet7",
                    }
                ),
                ("node_a: Cloudish-1 not found"),
            ),
        ],
        ids=["port_not_found", "node_not_found"],
    )
    def test_delete_link_error(self, project_mock, params, expected):
        with pytest.raises(ValueError, match=expected):
            project_mock.delete_link(**params)
