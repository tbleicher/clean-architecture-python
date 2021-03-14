class TestGraphQLHealthCheckQuery:
    """GraphQL.query.users"""

    query = "query QueryUsers { users { id email } }"

    def test_query_users_list(self, client, all_users):
        """[GQL-US-000] returns all users"""

        json = {"query": self.query}
        response = client.post("/graphql", json=json)

        assert response.status_code == 200

        # confirm that all users have been returned
        result = response.json()
        assert len(result["data"]["users"]) == len(all_users)
