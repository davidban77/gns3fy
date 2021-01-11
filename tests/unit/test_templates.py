import json
import pytest
from pathlib import Path
from gns3fy.server import Server


DATA_FILES = Path(__file__).resolve().parent / "data"


def templates_new_data():
    with open(DATA_FILES / "templates_new.json") as fdata:
        data = json.load(fdata)
    return data


class TestTemplates:
    def test_get_templates(self, connector_mock):
        server = Server(connector_mock)
        server.get_templates()
        templates = list(server.templates.values())
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
            assert n[0] == templates[index].name
            assert n[1] == templates[index].template_type
            assert n[2] == templates[index].category

    def test_search_template(self, connector_mock):
        server = Server(connector_mock)
        template = server.search_template(name="alpine")
        assert template.name == "alpine"
        assert template.template_type == "docker"
        assert template.category == "guest"

    def test_search_template_error(self, connector_mock):
        server = Server(connector_mock)
        template = server.search_template(name="dummy")
        assert template is None

    def test_create_template(self, connector_mock):
        new_data_template = templates_new_data()[0]
        server = Server(connector_mock)
        new_template = server.create_template(**new_data_template)
        assert new_template.name == "alpinev2"
        assert new_template.template_type == "docker"
        assert new_template.category == "guest"
        assert new_template.template_id == "7777777-4444"

    def test_create_template_already_exists(self, connector_mock):
        server = Server(connector_mock)
        with pytest.raises(ValueError, match="Template alpine already exists"):
            server.create_template("alpine", "docker")

    def test_update_template(self, connector_mock):
        server = Server(connector_mock)
        template = server.search_template("alpine")
        assert template.category == "guest"
        # Update
        template.update(category="switch")
        assert template.name == "alpine"
        assert template.category == "switch"

    # NOTE: Values are not validated on UPDATE, only on creation
    # def test_update_template_invalid_parameter(self, connector_mock):
    #     server = Server(connector_mock)
    #     template = server.search_template("alpine")
    #     with pytest.raises(ValidationError):
    #         template.update(template_type="dummy")

    def test_delete_template(self, connector_mock):
        server = Server(connector_mock)
        response = server.delete_template(name="alpine")
        assert response is True

    def test_delete_template_error(self, connector_mock):
        server = Server(connector_mock)
        with pytest.raises(ValueError, match="Template dummy not found"):
            server.delete_template("dummy")
