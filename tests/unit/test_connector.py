from gns3fy.services import get_version


class TestConnector:
    def test_get_version(self, connector_mock):
        assert dict(local=True, version="2.2.0") == get_version(connector_mock)
