from fastapi import Header, HTTPException, status
from app.core.config import settings

def verify_cloudflare(cf_access_jwt: str | None = Header(None, alias="Cf-Access-Jwt-Assertion")):
    if settings.ENABLE_CLOUDFLARE_CHECK:
        if not cf_access_jwt:
            # Generic 403 biar hacker gak tau apa-apa
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    if x_api_key == settings.API_KEY_REAL:
        return "real"
    elif x_api_key == settings.API_KEY_DECOY:
        return "decoy" # Nanti di Fase 3 dipake buat jebakan
    else:
        # Generic 401
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
