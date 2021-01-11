def test_create_template(gns3_server):
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
    template = gns3_server.create_template(**data)

    assert template.name == "alpinev2"
    assert template.console_http_port == 8080
    assert template.adapters == 4
    assert template.console_type == "telnet"
    assert template.usage == "New template"


def test_update_template(gns3_server):
    template = gns3_server.search_template(name="alpinev2")
    assert template.name == "alpinev2"

    template.update(console_http_port=7070, adapters=2)
    assert template.console_http_port == 7070
    assert template.adapters == 2


def test_delete_template(gns3_server):
    response = gns3_server.delete_template(name="alpinev2")
    assert response is True
