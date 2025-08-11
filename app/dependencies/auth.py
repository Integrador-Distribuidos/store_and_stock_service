import os
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime

SECRET_KEY = os.getenv("SECRET_KEY", "dev-unsafe-secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
bearer_scheme = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id") or payload.get("sub") or payload.get("id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário inválido no token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        expiration = payload.get("exp")
        if expiration and expiration < datetime.utcnow().timestamp():
            raise HTTPException(status_code=401, detail="Token expirado.")

        try:
            user_id = int(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="ID do usuário inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return {"id_user": user_id, "token": token}

    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado.")

class AuthUserMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get("Authorization")
        user_id = None
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                user_id = payload.get("user_id")
            except JWTError:
                pass

        request.state.user_id = user_id
        response = await call_next(request)
        return response
