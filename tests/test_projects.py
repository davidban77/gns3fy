import json
import pytest
from pathlib import Path
from pydantic import ValidationError
from gns3fy.services import get_projects, search_project, create_project, delete_project


DATA_FILES = Path(__file__).resolve().parent / "data"


def projects_new_data():
    with open(DATA_FILES / "projects_new.json") as fdata:
        data = json.load(fdata)
    return data


class TestProjects:
    def test_get_projects(self, connector_mock):
        projects = get_projects(connector_mock)
        for index, n in enumerate(
            [
                ("test2", "test2.gns3", "closed"),
                ("API_TEST", "test_api1.gns3", "opened"),
            ]
        ):
            assert n[0] == projects[index].name
            assert n[1] == projects[index].filename
            assert n[2] == projects[index].status

    @pytest.mark.parametrize(
        "params,expected",
        [
            (({"name": "API_TEST"}), ("API_TEST", "test_api1.gns3", "opened")),
            (
                ({"project_id": "c9dc56bf-37b9-453b-8f95-2845ce8908e3"}),
                ("test2", "test2.gns3", "closed"),
            ),
        ],
        ids=["by_name", "by_id"],
    )
    def test_search_project(self, connector_mock, params, expected):
        project = search_project(connector_mock, **params)
        # Refresh
        project.get()
        assert expected[0] == project.name
        assert expected[1] == project.filename
        assert expected[2] == project.status

    @pytest.mark.parametrize(
        "params",
        [
            (("dummy", "name")),
            ((None, None)),
        ],
        ids=["project_not_found", "invalid_query"],
    )
    def test_search_project_error(self, connector_mock, params):
        if params[1] == "name":
            project = search_project(connector_mock, name=params[0])
            assert project is None
        elif params[1] is None:
            with pytest.raises(
                ValueError, match="Need to submit either name or project_id"
            ):
                search_project(connector_mock, params[0], params[1])

    def test_create_project(self, connector_mock):
        new_data_project = projects_new_data()[0]
        new_project = create_project(connector_mock, **new_data_project)
        assert new_project.name == "new_project"
        assert new_project.status == "opened"
        assert new_project.project_id == "7777777-4444-PROJECT"

    def test_create_project_already_exists(self, connector_mock):
        with pytest.raises(
            ValueError, match="Project with same name already exists: API_TEST"
        ):
            create_project(connector_mock, "API_TEST")

    def test_update_project(self, connector_mock):
        project = search_project(connector_mock, "API_TEST")
        assert project.auto_close is False
        assert project.filename == "test_api1.gns3"
        # Update
        project.update(auto_close=True, filename="new_name.gns3")
        assert project.name == "API_TEST"
        assert project.auto_close is True
        assert project.filename == "new_name.gns3"

    def test_update_project_invalid_parameter(self, connector_mock):
        project = search_project(connector_mock, "API_TEST")
        with pytest.raises(ValidationError):
            project.update(scene_height="dummy")

    @pytest.mark.parametrize(
        "params",
        [
            (({"name": "API_TEST"})),
            (({"project_id": "4b21dfb3-675a-4efa-8613-2f7fb32e76fe"})),
        ],
        ids=["by_name", "by_id"],
    )
    def test_delete_project(self, connector_mock, params):
        response = delete_project(connector_mock, **params)
        assert response is None

    @pytest.mark.parametrize(
        "params,expected",
        [
            ((None), ("Need to submit either name or project_id")),
            (("dummy"), ("Project not found")),
        ],
        ids=["none_args", "project_not_found"],
    )
    def test_delete_project_error(self, connector_mock, params, expected):
        with pytest.raises(ValueError, match=expected):
            delete_project(connector_mock, params)
