import pytest
from pathlib import Path
from datetime import datetime, timedelta, timezone
from gns3fy.drawings import (
    generate_ellipse_svg,
    generate_line_svg,
    generate_rectangle_svg,
)

IMAGE_PATH = Path(__file__).parent.parent.parent / "build"


@pytest.mark.gns3vm
def test_upload_compute_image(gns3_server):
    # Upload Cisco IOSv image
    response = gns3_server.upload_compute_image(
        emulator="qemu",
        file_path=str(IMAGE_PATH / "vios-adventerprisek9-m.vmdk.SPA.157-3.M3"),
    )
    assert response is True
    assert len(gns3_server.get_compute_images(emulator="qemu")) == 1

    # Upload startup image
    response = gns3_server.upload_compute_image(
        emulator="qemu",
        file_path=str(IMAGE_PATH / "IOSv_startup_config.img"),
    )
    assert response is True


@pytest.mark.gns3vm
def test_create_template(gns3_server):
    data = {
        "name": "Cisco IOSv",
        "compute_id": "local",
        "builtin": False,
        "category": "router",
        "default_name_format": "{name}-{0}",
        "symbol": ":/symbols/router.svg",
        "template_type": "qemu",
        "custom_adapters": [],
        "hdd_disk_interface": "ide",
        "hdc_disk_image": "",
        "kernel_image": "",
        "cpus": 1,
        "initrd": "",
        "platform": "i386",
        "hdc_disk_interface": "ide",
        "mac_address": "",
        "ram": 512,
        "qemu_path": "/usr/bin/qemu-system-x86_64",
        "usage": "There is no default password and enable password",
        "bios_image": "",
        "console_type": "telnet",
        "hda_disk_interface": "virtio",
        "adapters": 4,
        "linked_clone": True,
        "first_port_name": "",
        "hdb_disk_interface": "virtio",
        "port_name_format": "Gi0/{0}",
        "kernel_command_line": "",
        "legacy_networking": False,
        "adapter_type": "e1000",
        "options": "",
        "cdrom_image": "",
        "hdd_disk_image": "",
        "hda_disk_image": "vios-adventerprisek9-m.vmdk.SPA.157-3.M3",
        "console_auto_start": False,
        "cpu_throttling": 0,
        "replicate_network_connection_state": True,
        "boot_priority": "c",
        "process_priority": "normal",
        "port_segment_size": 0,
        "on_close": "power_off",
        "hdb_disk_image": "IOSv_startup_config.img",
    }
    template = gns3_server.create_template(**data)

    assert template.name == "Cisco IOSv"
    assert template.adapters == 4  # type: ignore
    assert template.console_type == "telnet"  # type: ignore


def test_close_project(gns3_project):
    gns3_project.close()
    assert gns3_project.status == "closed"


def test_reopen_project(gns3_project):
    gns3_project.open()
    assert gns3_project.status == "opened"


def test_create_nodes(gns3_project):
    sw1 = gns3_project.create_node(name="sw1", template="Ethernet switch")
    sw2 = gns3_project.create_node(name="sw2", template="Ethernet switch")
    assert sw1 != sw2
    assert sw1.name == "sw1"
    assert sw1.console
    assert 5000 <= sw1.console <= 5999
    assert sw1.node_type == "ethernet_switch"
    assert len(sw1.ports) == 8
    assert sw2.name == "sw2"
    assert sw2.console
    assert 5000 <= sw2.console <= 5999
    assert sw2.node_type == "ethernet_switch"
    assert len(sw2.ports) == 8


def test_create_link(gns3_project):
    link = gns3_project.create_link(
        node_a="sw1", port_a="Ethernet0", node_b="sw2", port_b="Ethernet0"
    )
    assert link.link_type == "ethernet"
    assert link.suspend is False
    assert link.capturing is False
    assert link.nodes[0].label["text"] == "Ethernet0"
    assert link.nodes[1].label["text"] == "Ethernet0"


def test_rename_node(gns3_project):
    sw1 = gns3_project.search_node("sw1")
    sw1.update(name="renamed_sw1")
    assert sw1.name == "renamed_sw1"
    renamed_sw1 = gns3_project.search_node("renamed_sw1")
    assert sw1 == renamed_sw1
    renamed_sw1.update(name="sw1")
    assert renamed_sw1.name == "sw1"


def test_start_nodes(gns3_project):
    sw1 = gns3_project.search_node("sw1")
    sw1.start()
    assert sw1.status == "started"
    sw2 = gns3_project.search_node("sw2")
    sw2.start()
    assert sw2.status == "started"


def test_suspend_link(gns3_project):
    link = gns3_project.search_link(
        node_a="sw1", port_a="Ethernet0", node_b="sw2", port_b="Ethernet0"
    )
    link.update(suspend=True)
    assert link.suspend is True


def test_delete_link(gns3_project):
    response = gns3_project.delete_link(
        node_a="sw1", port_a="Ethernet0", node_b="sw2", port_b="Ethernet0"
    )
    assert response is True
    assert len(gns3_project.links) == 0


@pytest.mark.skip(reason="skipping for the time being")
# @pytest.mark.gns3vm
def test_reload_suspend_stop_nodes(gns3_project):
    r1 = gns3_project.create_node(name="r1", template="Cisco IOSv")
    r1.start()
    assert r1.status == "started"
    r1.suspend()
    assert r1.status == "suspended"
    r1.reload()
    assert r1.status == "started"
    r1.stop()
    assert r1.status == "stopped"
    gns3_project.delete_node(name="r1")


def test_delete_nodes(gns3_project):
    response = gns3_project.delete_node(name="sw1")
    assert response is True
    assert len(gns3_project.nodes) == 1

    response = gns3_project.delete_node(name="sw2")
    assert response is True
    assert len(gns3_project.nodes) == 0


def test_create_drawings(gns3_project):
    rectangle = gns3_project.create_drawing(svg=generate_rectangle_svg())
    ellipse = gns3_project.create_drawing(svg=generate_ellipse_svg())
    line = gns3_project.create_drawing(svg=generate_line_svg())

    assert rectangle.drawing_id is not None
    assert ellipse.drawing_id is not None
    assert line.drawing_id is not None


def test_delete_drawings(gns3_project):
    rectangle = [draw for draw in gns3_project.drawings if "rect" in draw.svg][0]
    response = gns3_project.delete_drawing(drawing_id=rectangle.drawing_id)
    assert response is True
    assert len(gns3_project.drawings) == 2


def test_create_snapshot(gns3_project):
    snap1 = gns3_project.create_snapshot(name="snap1")
    assert snap1.name == "snap1"
    assert snap1.snapshot_id is not None
    assert snap1.created_at is not None
    assert (
        datetime.now(tz=timezone.utc) - timedelta(days=1)
        < snap1.created_at
        < datetime.now(tz=timezone.utc) + timedelta(days=1)
    )


def test_delete_snapshot(gns3_project):
    response = gns3_project.delete_snapshot(name="snap1")
    assert response is True

    assert len(gns3_project.snapshots) == 0


@pytest.mark.gns3vm
def test_delete_template(gns3_server):
    response = gns3_server.delete_template(name="Cisco IOSv")
    assert response is True
