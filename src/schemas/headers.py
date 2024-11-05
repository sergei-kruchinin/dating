from pydantic import BaseModel


class AuthorizationHeaders(BaseModel):
    authorization: str | None = None

    def token(self) -> str:
        prefix = 'Bearer '
        if not self.authorization or not self.authorization.startswith(prefix):
            return ""
        token = self.authorization[len(prefix):]
        return token
