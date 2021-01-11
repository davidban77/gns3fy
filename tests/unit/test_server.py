from gns3fy.server import Server


class TestConnector:
    def test_get_version(self, connector_mock):
        server = Server(connector_mock)
        assert dict(local=True, version="2.2.0") == server.get_version()
