class TestHealthCheckQuery:
    """REST API"""

    def test_healthcheck(self, client):
        """[REST-HC-01] /healthcheck returns 200 status"""
        response = client.get("/healthcheck")
        assert response.status_code == 200

    def test_healthcheck_data(self, client):
        """[REST-HC-02] /healthcheck reports the environment"""
        response = client.get("/healthcheck")

        json = response.json()
        assert json["environment"] == "test"
