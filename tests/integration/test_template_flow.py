from gns3fy.services import (
    create_template,
    delete_template,
    search_template,
)


def test_create_template(gns3_conn):
    data = {
        "adapters": 4,
        "builtin": False,
        "category": "guest",
        "compute_id": "local",
        "console_auto_start": False,
        "console_http_path": "/",
        "console_http_port": 8080,
        "console_resolution": "1024x768",
        "console_type": "telnet",
        "custom_adapters": [],
        "default_name_format": "{name}-{0}",
        "environment": "",
        "extra_hosts": "",
        "extra_volumes": [],
        "image": "alpine",
        "name": "alpinev2",
        "start_command": "",
        "symbol": ":/symbols/affinity/circle/gray/docker.svg",
        "template_type": "docker",
        "usage": "New template",
    }
    template = create_template(gns3_conn, **data)

    assert template.name == "alpinev2"
    assert template.console_http_port == 8080  # type: ignore
    assert template.adapters == 4  # type: ignore
    assert template.console_type == "telnet"  # type: ignore
    assert template.usage == "New template"  # type: ignore


def test_update_template(gns3_conn):
    template = search_template(gns3_conn, name="alpinev2")
    assert template.name == "alpinev2"

    template.update(console_http_port=7070, adapters=2)
    assert template.console_http_port == 7070  # type: ignore
    assert template.adapters == 2  # type: ignore


def test_delete_template(gns3_conn):
    response = delete_template(gns3_conn, name="alpinev2")
    assert response is None
