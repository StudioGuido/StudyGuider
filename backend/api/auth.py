from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
import requests
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")

JWKS_URL = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json"

security = HTTPBearer()

# Load Supabase public signing keys
jwks = requests.get(JWKS_URL).json()


def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials

    try:
        header = jwt.get_unverified_header(token)
        kid = header["kid"]

        key = next(k for k in jwks["keys"] if k["kid"] == kid)

        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience="authenticated",
            issuer=f"{SUPABASE_URL}/auth/v1",
        )

        return payload

    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")