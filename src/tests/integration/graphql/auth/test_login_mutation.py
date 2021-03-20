from jose import jwt
from unittest.mock import patch

VALID_CREDENTIALS = {"email": "cloe@example.com", "password": "password"}

class TestGraphQLLoginMutation:
    """GraphQL.mutation.login"""
    
    login_mutation = """
    mutation Login($input: LoginInput!) { 
        login(input: $input) { 
            token 
            __typename 
        } 
    }"""

    def make_login_request(self, client, input_vars=VALID_CREDENTIALS):
        """make a login request with valid email and password"""
        json = {
            "query": self.login_mutation,
            "variables": {"input": input_vars},
        }
        return client.post("/graphql", json=json)


    def test_login_mutation_requires_email_and_password(self, client):
        """[GQL-AU-01] requires email and password"""

        response = self.make_login_request(client, {"email": "cloe@example.com"})
        assert response.status_code == 400

        response = self.make_login_request(client, {"password": "password"})
        assert response.status_code == 400

        # confirm successful input combination
        response = self.make_login_request(client)
        assert response.status_code == 200


    def test_login_mutation_returns_token(self, client):
        """[GQL-AU-02] returns TokenData with a token (string) on success"""
        response = self.make_login_request(client)

        data = response.json()["data"]
        assert data["login"]["__typename"] == "TokenData"
        assert isinstance(data["login"]["token"], str)


    def test_login_mutation_token_includes_user_data(self, client):
        """[GQL-AU-03] token payload contains the user's id and email"""
        response = self.make_login_request(client)

        data = response.json()["data"]
        token = data["login"]["token"]

        options = {"verify_signature": False}
        decoded = jwt.decode(token, "", options=options)

        assert decoded["user"]["id"] == "USER-CLOE"
        assert decoded["user"]["email"] == "cloe@example.com"


    def test_login_mutation_auth_error_message(self, client):
        """[GQL-AU-04] user receives AuthenticationError"""
        variations = [
            {"email": "NO_SUCH_EMAIL@example.com", "password": "password"},
            {"email": "cloe@example.com", "password": "wrong_password"},
        ]

        for credentials in variations:
            response = self.make_login_request(client, credentials)

            error = response.json()["errors"][0]
            assert error["message"].startswith("AuthenticationError")


    def test_login_mutation_any_other_error(self, client):
        """[GQL-AU-05] Processing errors are exposed to the user"""

        expected = "Out of Cheese Error. Redo From Start."

        with patch(
            "app.domain.services.AuthService.authenticate_user",
            side_effect=Exception(expected),
        ):
            response = self.make_login_request(client)

            error = response.json()["errors"][0]
            assert error["message"] == expected
