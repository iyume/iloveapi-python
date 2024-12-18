from __future__ import annotations

from datetime import datetime, timezone
from typing import Generator

import httpx
import jwt

ALGORITHM = "HS256"
EXPIRE_SEC = 3600  # 1 hour


class TokenAuth(httpx.Auth):

    def __init__(self, public_key: str, secret_key: str) -> None:
        self._public_key = public_key
        self._secret_key = secret_key
        self._token_cache: tuple[str, int] | None = None

    def get_token(self) -> str:
        if self._token_cache is not None:
            token, exp = self._token_cache
            # Refresh token if it's going to expire in less than 2 minutes
            if exp - 120 > int(datetime.now(timezone.utc).timestamp()):
                return token
        now = int(datetime.now(timezone.utc).timestamp())
        exp = now + EXPIRE_SEC
        payload = {
            "iss": "api.ilovepdf.com",
            "aud": "",
            "iat": now,
            "nbf": now,
            "exp": exp,
            "jti": self._public_key,
        }
        token = jwt.encode(payload, self._secret_key, algorithm=ALGORITHM)
        self._token_cache = (token, exp)
        return token

    def auth_flow(
        self, request: httpx.Request
    ) -> Generator[httpx.Request, httpx.Response, None]:
        request.headers["Authorization"] = f"Bearer {self.get_token()}"
        yield request
