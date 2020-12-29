class TestConnector:
    def test_get_version(self, connector_mock):
        assert dict(local=True, version="2.2.0") == connector_mock.get_version()
