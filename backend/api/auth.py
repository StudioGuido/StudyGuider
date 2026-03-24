from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
import requests
import os
import logging

logger = logging.getLogger(__name__)

raw_url = os.getenv("SUPABASE_URL")
if not raw_url:
    raise RuntimeError("Supabase URL not found in environment variables")

# .rstrip("/") removes the trailing slash if it exists
SUPABASE_URL = raw_url.rstrip("/")
JWKS_URL = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json"

security = HTTPBearer()

# Load Supabase public signing keys
try:
    response = requests.get(JWKS_URL)
    response.raise_for_status()
    jwks = response.json()
    print("Successfully loaded JWKS")
except Exception as e:
    print(f"Failed to load JWKS from {JWKS_URL}: {e}")
    jwks = {"keys": []}

def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        header = jwt.get_unverified_header(token)
        kid = header["kid"]
        
        # Find the matching key
        key = next(k for k in jwks["keys"] if k["kid"] == kid)
        
        payload = jwt.decode(
            token,
            key,
            algorithms=[key["alg"]],
            audience="authenticated",
            issuer=f"{SUPABASE_URL}/auth/v1",
        )
        return payload

    except Exception as e:
        logger.error(f"JWT verification failed: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")