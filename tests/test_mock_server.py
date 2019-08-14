from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
from threading import Thread

import requests


class MockServerRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Process an HTTP GET request and return a response with an HTTP 200 status.
        self.send_response(requests.codes.ok)
        self.end_headers()
        return


def get_free_port():
    s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
    s.bind(("localhost", 0))
    address, port = s.getsockname()
    s.close()
    return port


class TestMockServer:
    @classmethod
    def setup_class(cls):
        # Configure mock server.
        cls.mock_server_port = get_free_port()
        cls.mock_server = HTTPServer(
            ("localhost", cls.mock_server_port), MockServerRequestHandler
        )

        # Start running mock server in a separate thread.
        # Daemon threads automatically shut down when the main process exits.
        cls.mock_server_thread = Thread(target=cls.mock_server.serve_forever)
        cls.mock_server_thread.setDaemon(True)
        cls.mock_server_thread.start()

    def test_get_version(self):
        version_url = f"http://localhost:{self.mock_server_port}/v2/version"
        response = requests.get(version_url)
        assert 200 == response.status_code
        # assert dict(local=True, version="2.2.0") == response.json()
