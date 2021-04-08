class TestGraphQLProfileQuery:
    """GraphQL.query.profile"""

    query = "query QueryProfile { profile { id email organizationId } }"

    def test_query_profile_without_token(self, client):
        """[GQL-PFL-01] returns null if no authentication token is provided"""

        json = {"query": self.query}
        response = client.post("/graphql", json=json)

        assert response.status_code == 200

        # confirm no profile has been returned
        result = response.json()
        assert result["data"]["profile"] is None

    def test_query_profile_with_user_token(self, all_users, client, get_auth_headers):
        """[GQL-PFL-02] returns the correct profile data for an authenticated user"""
        user = all_users[3]
        headers = get_auth_headers(user["id"])
        json = {"query": self.query}
        response = client.post("/graphql", headers=headers, json=json)

        assert response.status_code == 200

        # confirm the right user data has been returned as profile
        result = response.json()
        profile = result["data"]["profile"]

        assert profile["id"] == user["id"]
        assert profile["email"] == user["email"]
        assert profile["organizationId"] == user["organization_id"]
