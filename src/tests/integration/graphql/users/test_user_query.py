class TestGraphQLUserDetailsQuery:
    """GraphQL.query.user"""

    query = "query QueryUserDetails($userId: String!) { user(userId: $userId) { id email } }"
    variables = {"userId": "USER-CLOE"}

    def _query_user(self, client, headers={}):
        json = {"query": self.query, "variables": self.variables}
        response = client.post("/graphql", headers=headers, json=json)

        assert response.status_code == 200

        result = response.json()
        return result["data"]["user"]

    def test_query_user_details_without_token(self, client):
        """[GQL-US-101] returns None when queried without token"""
        user = self._query_user(client)

        assert user == None

    def test_query_user_details_with_invalid_id(self, client):
        """[GQL-US-102] returns None when the user does not exist"""
        json = {"query": self.query, "variables": {"userId": "---"}}
        response = client.post("/graphql", json=json)

        assert response.status_code == 200

        result = response.json()
        assert result["data"]["user"] == None

    def test_query_user_details_as_admin(self, client, get_auth_headers):
        """[GQL-US-103] returns user when querying user is an admin"""
        headers = get_auth_headers("USER-ADM")
        user = self._query_user(client, headers)

        assert user != None
        assert user["id"] == self.variables["userId"]

    def test_query_user_details_with_same_organisation(self, client, get_auth_headers):
        """[GQL-US-104] returns user when querying user is in the same organisation"""
        headers = get_auth_headers("USER-MARY")
        user = self._query_user(client, headers)

        assert user != None
        assert user["id"] == self.variables["userId"]

    def test_query_user_details_with_diff_organisation(self, client, get_auth_headers):
        """[GQL-US-105] returns None when querying user is in a different organisation"""
        headers = get_auth_headers("USER-BIG-STEVE")
        user = self._query_user(client, headers)

        assert user == None
