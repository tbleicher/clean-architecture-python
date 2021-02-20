class TestGraphQLHealthCheckQuery:
    """GraphQL"""

    query = "query HealthCheck($name: String) { healthcheck(name: $name) }"

    def test_graphql_healthcheck_response(self, client):
        """[GQL-HC-01] 'healthcheck' returns a default greeting"""
        json = {
            "query": self.query,
        }
        response = client.post("/graphql", json=json)
        result = response.json()

        assert result["data"]["healthcheck"] == "Hello GraphQL!"

    def test_graphql_healthcheck_with_data(self, client):
        """[GQL-HC-02] 'healthcheck' returns a custom greeting with 'name' variable"""
        json = {"query": self.query, "variables": {"name": "Test"}}
        response = client.post("/graphql", json=json)
        result = response.json()

        assert result["data"]["healthcheck"] == "Hello Test!"
