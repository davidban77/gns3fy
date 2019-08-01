import json
import pytest
from pathlib import Path
from gns3fy import Link, Node, Project
from .data import links, nodes, projects

DATA_FILES = Path(__file__).resolve().parent / "data"


@pytest.fixture
def links_data():
    with open(DATA_FILES / "links.json") as fdata:
        data = json.load(fdata)
    return data


@pytest.fixture
def nodes_data():
    with open(DATA_FILES / "nodes.json") as fdata:
        data = json.load(fdata)
    return data


@pytest.fixture
def projects_data():
    with open(DATA_FILES / "projects.json") as fdata:
        data = json.load(fdata)
    return data


class TestLink:
    def test_instatiation(self, links_data):
        for index, link_data in enumerate(links_data):
            assert links.LINKS_REPR[index] == repr(Link(**link_data))


class TestNode:
    def test_instatiation(self, nodes_data):
        for index, node_data in enumerate(nodes_data):
            assert nodes.NODES_REPR[index] == repr(Node(**node_data))


class TestProject:
    def test_instatiation(self, projects_data):
        for index, project_data in enumerate(projects_data):
            assert projects.PROJECTS_REPR[index] == repr(Project(**project_data))
