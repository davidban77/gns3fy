import json
import pytest
from pathlib import Path
from pydantic import ValidationError
from gns3fy.server import Server


DATA_FILES = Path(__file__).resolve().parent / "data"


def projects_new_data():
    with open(DATA_FILES / "projects_new.json") as fdata:
        data = json.load(fdata)
    return data


class TestProjects:
    def test_get_projects(self, connector_mock):
        server = Server(connector_mock)
        server.get_projects()
        projects = list(server.projects.values())
        for index, n in enumerate(
            [
                ("test2", "test2.gns3", "closed"),
                ("API_TEST", "test_api1.gns3", "opened"),
            ]
        ):
            assert n[0] == projects[index].name
            assert n[1] == projects[index].filename
            assert n[2] == projects[index].status

    def test_search_project(self, connector_mock):
        server = Server(connector_mock)
        project = server.search_project(name="API_TEST")
        assert project.name == "API_TEST"
        assert project.filename == "test_api1.gns3"
        assert project.status == "opened"

    @pytest.mark.parametrize(
        "params",
        [
            (("dummy", "name")),
            ((None, None)),
        ],
        ids=["project_not_found", "invalid_query"],
    )
    def test_search_project_not_found(self, connector_mock, params):
        server = Server(connector_mock)
        project = server.search_project(name="dummy")
        assert project is None

    def test_create_project(self, connector_mock):
        new_data_project = projects_new_data()[0]
        server = Server(connector_mock)
        new_project = server.create_project(**new_data_project)
        assert new_project.name == "new_project"
        assert new_project.status == "opened"
        assert new_project.project_id == "7777777-4444-PROJECT"

    def test_create_project_already_exists(self, connector_mock):
        server = Server(connector_mock)
        with pytest.raises(ValueError, match="Project API_TEST already created"):
            server.create_project("API_TEST")

    def test_update_project(self, connector_mock):
        server = Server(connector_mock)
        project = server.search_project("API_TEST")
        assert project.auto_close is False
        assert project.filename == "test_api1.gns3"
        # Update
        project.update(auto_close=True, filename="new_name.gns3")
        assert project.name == "API_TEST"
        assert project.auto_close is True
        assert project.filename == "new_name.gns3"

    def test_update_project_invalid_parameter(self, connector_mock):
        server = Server(connector_mock)
        project = server.search_project("API_TEST")
        with pytest.raises(ValidationError):
            project.update(scene_height="dummy")

    def test_delete_project(self, connector_mock):
        server = Server(connector_mock)
        response = server.delete_project(name="API_TEST")
        assert response is True

    def test_delete_project_error(self, connector_mock):
        server = Server(connector_mock)
        with pytest.raises(ValueError, match="Project dummy not found"):
            server.delete_project(name="dummy")
