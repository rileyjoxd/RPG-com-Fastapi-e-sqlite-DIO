import time
from typing import Annotated
from uuid import uuid4

from jwt import encode, decode
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

bearer_scheme = HTTPBearer()

SECRET = "rpg-secret"
ALGORITHM = "HS256"


class AccessToken(BaseModel):
    iss: str
    sub: str
    aud: str
    exp: float
    iat: float
    nbf: float
    jti: str


class JWTToken(BaseModel):
    access_token: str


def sign_jwt(user_id: int) -> JWTToken:
    now = time.time()
    payload = {
        "iss": "rpg-api.com.br",
        "sub": str(user_id),
        "aud": "rpg-api",
        "exp": int(now) + (60 * 30),
        "iat": int(now),
        "nbf": int(now),
        "jti": uuid4().hex,
    }
    token = encode(payload, SECRET, algorithm=ALGORITHM)
    return JWTToken(access_token=token)


async def decode_jwt(token: str) -> JWTToken | None:
    try:
        decoded_token = decode(token, SECRET, audience="rpg-api", algorithms=[ALGORITHM])
        _token = AccessToken(**decoded_token)
        return JWTToken(access_token=token) if _token.exp >= time.time() else None
    except Exception as e:
        print(f"decode_jwt error: {e}")
        return None


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)]
) -> dict[str, int]:
    token = credentials.credentials
    payload = await decode_jwt(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido ou expirado.")
    decoded = decode(token, SECRET, audience="rpg-api", algorithms=[ALGORITHM])
    return {"user_id": int(decoded["sub"])}


def login_required(current_user: Annotated[dict[str, int], Depends(get_current_user)]):
    return current_user
