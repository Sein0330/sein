from fastapi import Header, HTTPException, status
from app.core.config import settings

def verify_cloudflare(cf_access_jwt: str | None = Header(None, alias="Cf-Access-Jwt-Assertion")):
    if settings.ENABLE_CLOUDFLARE_CHECK:
        if not cf_access_jwt:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

def verify_api_key(x_api_key: str | None = Header(None, alias="X-API-Key")):
    if not x_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    
    if x_api_key == settings.API_KEY_REAL:
        return "real"
    elif x_api_key == settings.API_KEY_DECOY:
        return "decoy"
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
