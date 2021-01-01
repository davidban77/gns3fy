import json
import pytest
from pathlib import Path
from pydantic import ValidationError
from gns3fy.services import (
    get_templates,
    search_template,
    create_template,
    delete_template,
)


DATA_FILES = Path(__file__).resolve().parent / "data"


def templates_new_data():
    with open(DATA_FILES / "templates_new.json") as fdata:
        data = json.load(fdata)
    return data


class TestTemplates:
    def test_get_templates(self, connector_mock):
        templates = get_templates(connector_mock)
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

    @pytest.mark.parametrize(
        "params,expected",
        [
            (({"name": "alpine"}), ("alpine", "docker", "guest")),
            (
                ({"template_id": "c6203d4b-d0ce-4951-bf18-c44369d46804"}),
                ("vEOS", "qemu", "router"),
            ),
        ],
        ids=["by_name", "by_id"],
    )
    def test_search_template(self, connector_mock, params, expected):
        template = search_template(connector_mock, **params)
        # Refresh
        template.get()
        assert expected[0] == template.name
        assert expected[1] == template.template_type
        assert expected[2] == template.category

    @pytest.mark.parametrize(
        "params",
        [
            (("dummy", "name")),
            ((None, None)),
        ],
        ids=["template_not_found", "invalid_query"],
    )
    def test_search_template_error(self, connector_mock, params):
        if params[1] == "name":
            template = search_template(connector_mock, name=params[0])
            assert template is None
        elif params[1] is None:
            with pytest.raises(
                ValueError, match="Need to submit either name or template_id"
            ):
                search_template(connector_mock, params[0], params[1])

    def test_create_template(self, connector_mock):
        new_data_template = templates_new_data()[0]
        new_template = create_template(connector_mock, **new_data_template)
        assert new_template.name == "alpinev2"
        assert new_template.template_type == "docker"
        assert new_template.category == "guest"
        assert new_template.template_id == "7777777-4444"

    def test_create_template_already_exists(self, connector_mock):
        with pytest.raises(
            ValueError, match="Template with same name already exists: alpine"
        ):
            create_template(connector_mock, "alpine")

    def test_update_template(self, connector_mock):
        template = search_template(connector_mock, "alpine")
        assert template.category == "guest"
        # Update
        template.update(category="switch")
        assert template.name == "alpine"
        assert template.category == "switch"

    def test_update_template_invalid_parameter(self, connector_mock):
        template = search_template(connector_mock, "alpine")
        with pytest.raises(ValidationError):
            template.update(builtin="dummy")

    @pytest.mark.parametrize(
        "params",
        [
            (({"name": "alpine"})),
            (({"template_id": "847e5333-6ac9-411f-a400-89838584371b"})),
        ],
        ids=["by_name", "by_id"],
    )
    def test_delete_template(self, connector_mock, params):
        response = delete_template(connector_mock, **params)
        assert response is None

    @pytest.mark.parametrize(
        "params,expected",
        [
            ((None), ("Need to submit either name or template_id")),
            (("dummy"), ("Template not found")),
        ],
        ids=["none_args", "template_not_found"],
    )
    def test_delete_template_error(self, connector_mock, params, expected):
        with pytest.raises(ValueError, match=expected):
            delete_template(connector_mock, params)
