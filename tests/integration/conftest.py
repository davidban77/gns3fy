import pytest
from gns3fy.models.connector import Connector
from gns3fy.services import create_project, delete_project


# SERVER_PARAMS = {"url": "http://gns3-server:80"}
SERVER_PARAMS = {"url": "http://0.0.0.0:7070"}


@pytest.fixture(scope="session")
def gns3_conn():
    return Connector(**SERVER_PARAMS)


@pytest.fixture(scope="session")
def gns3_project(gns3_conn):
    # Creating a project
    project = create_project(gns3_conn, name="integration-test")
    yield project
    # Stop and Delete project
    project.close()
    delete_project(gns3_conn, name="integration-test")
