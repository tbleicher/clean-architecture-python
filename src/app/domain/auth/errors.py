class AuthError(Exception):
    """Exception raised on login error"""

    def __str__(self):
        return "AuthenticationError: email and password do not match."


class UnauthorizedError(Exception):
    """raised when session user is missing or has insufficient permissions"""

    def __init__(self, message=""):
        self.message = message

    def __str__(self):
        return (
            f"UnauthorizedError: {self.message}"
            if self.message
            else "UnauthorizedError"
        )
