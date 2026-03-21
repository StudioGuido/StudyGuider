from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
import requests
import os
import logging

logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")

JWKS_URL = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json"

security = HTTPBearer()

# Load Supabase public signing keys
jwks = requests.get(JWKS_URL).json()
print("Loaded JWKS:", jwks)

def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    print(f"Received JWT for verification: {token}")
    
    try:
        header = jwt.get_unverified_header(token)
        kid = header["kid"]
        key = next(k for k in jwks["keys"] if k["kid"] == kid)
        
        
        payload = jwt.decode(
            token,
            key,
            algorithms=[key["alg"]],
            audience="authenticated",
            issuer=f"{SUPABASE_URL}/auth/v1",
        )
        
        print("JWT successfully verified. Payload:", payload)

        return payload

    except Exception as e:
        logger.exception("JWT verification failed")
        raise HTTPException(status_code=401, detail="Invalid or expired token")