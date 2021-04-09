class TestGraphQLUsersQuery:
    """GraphQL.query.users"""

    query = "query QueryUsers { users { id email } }"

    def test_query_users_list_without_token(self, client):
        """[GQL-US-001] returns an empty list without token"""
        json = {"query": self.query}
        response = client.post("/graphql", json=json)

        assert response.status_code == 200

        result = response.json()
        assert len(result["data"]["users"]) == 0

    def test_query_users_list_as_admin(self, all_users, client, get_auth_headers):
        """[GQL-US-002] returns a list of all users when queried as admin"""
        headers = get_auth_headers("USER-ADM")
        json = {"query": self.query}
        response = client.post("/graphql", headers=headers, json=json)

        assert response.status_code == 200

        result = response.json()
        assert len(result["data"]["users"]) == len(all_users)

    def test_query_users_list_as_user(self, client, get_auth_headers):
        """[GQL-US-003] returns a list of users in the current user's organisation"""
        combinations = [["USER-CLOE", 7], ["USER-BIG-STEVE", 3]]

        for user_id, count in combinations:
            headers = get_auth_headers(user_id)
            json = {"query": self.query}
            response = client.post("/graphql", headers=headers, json=json)

            assert response.status_code == 200

            result = response.json()
            assert len(result["data"]["users"]) == count
