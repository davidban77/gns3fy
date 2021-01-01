import pytest
from gns3fy.services import (
    create_link,
    create_node,
    delete_link,
    delete_node,
    search_link,
    search_node,
)


def test_close_project(gns3_project):
    gns3_project.close()
    assert gns3_project.status == "closed"


def test_reopen_project(gns3_project):
    gns3_project.open()
    assert gns3_project.status == "closed"


def test_create_nodes(gns3_project):
    sw1 = create_node(gns3_project, name="sw1", template_name="Ethernet switch")
    sw2 = create_node(gns3_project, name="sw2", template_name="Ethernet switch")
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
    link = create_link(
        gns3_project, node_a="sw1", port_a="Ethernet0", node_b="sw2", port_b="Ethernet0"
    )
    assert link.link_type == "ethernet"
    assert link.suspend is False
    assert link.capturing is False
    assert link.nodes[0].label["text"] == "Ethernet0"
    assert link.nodes[1].label["text"] == "Ethernet0"


def test_rename_node(gns3_project):
    sw1 = search_node(gns3_project, "sw1")
    sw1.update(name="renamed_sw1")
    assert sw1.name == "renamed_sw1"
    renamed_sw1 = search_node(gns3_project, "renamed_sw1")
    assert sw1 == renamed_sw1
    renamed_sw1.update(name="sw1")
    assert renamed_sw1.name == "sw1"


def test_start_nodes(gns3_project):
    sw1 = search_node(gns3_project, "sw1")
    sw1.start()
    assert sw1.status == "started"
    sw2 = search_node(gns3_project, "sw2")
    sw2.start()
    assert sw2.status == "started"


def test_suspend_link(gns3_project):
    link = search_link(
        gns3_project, node_a="sw1", port_a="Ethernet0", node_b="sw2", port_b="Ethernet0"
    )
    link.update(suspend=True)
    assert link.suspend is True


def test_delete_link(gns3_project):
    response = delete_link(
        gns3_project, node_a="sw1", port_a="Ethernet0", node_b="sw2", port_b="Ethernet0"
    )
    assert response is None


@pytest.mark.skip(reason="skipping for the time being")
def test_reload_suspend_stop_nodes(gns3_project):
    r1 = create_node(gns3_project, name="r1", template_name="Cisco IOSv 15.7(3)M3")
    r1.reload()
    assert r1.status == "started"
    r1.suspend()
    assert r1.status == "suspended"
    r1.stop()
    assert r1.status == "stopped"
    delete_node(gns3_project, name="r1")


def test_delete_nodes(gns3_project):
    response = delete_node(gns3_project, name="sw1")
    assert response is None
    response = delete_node(gns3_project, name="sw2")
    assert response is None
