"""
A unit test file to mock ping router
1. Valid response for GET /ping
2. Deny. Method not allowed for any other HTTP Method
"""


class TestPingRouter:
    def test_valid_response(self, ping_api_client):
        response = ping_api_client.get("/ping")
        assert response.status_code == 200
        assert response.json() == {"ping": "pong"}

    def test_invalid_http_method(self, ping_api_client):
        response = ping_api_client.post("/ping")
        assert response.status_code == 405
        assert response.json() == {"detail": "Method Not Allowed"}
