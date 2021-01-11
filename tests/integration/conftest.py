import pytest
from gns3fy.server import Server


# SERVER_PARAMS = {"url": "http://gns3-server:80"}
SERVER_PARAMS = {"url": "http://0.0.0.0:7070"}


def pytest_addoption(parser):
    parser.addoption(
        "--run_gns3vm", action="store_true", help="run GNS3 VM dependent tests"
    )


def pytest_runtest_setup(item):
    if "gns3vm" in item.keywords and not item.config.getvalue("run_gns3vm"):
        pytest.skip("need --rungns3vm option to run")


@pytest.fixture(scope="session")
def gns3_server():
    return Server(**SERVER_PARAMS)


@pytest.fixture(scope="session")
def gns3_project(gns3_server):
    # Creating a project
    project = gns3_server.create_project(name="integration-test")
    yield project
    # Stop and Delete project
    project.close()
    gns3_server.delete_project(name="integration-test")
