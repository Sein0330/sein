from fastapi import Header, HTTPException, status, Request
from app.core.config import settings
from app.core.logging import honeypot_logger

def verify_cloudflare(cf_access_jwt: str | None = Header(None, alias="Cf-Access-Jwt-Assertion")):
    if settings.ENABLE_CLOUDFLARE_CHECK:
        if not cf_access_jwt:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

def verify_api_key(request: Request, x_api_key: str | None = Header(None, alias="X-API-Key")):
    if not x_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    
    if x_api_key == settings.API_KEY_REAL:
        return "real"
    elif x_api_key == settings.API_KEY_DECOY:
        # Catat ke log kalau ada yang pake kunci jebakan
        client_ip = request.client.host if request.client else "unknown"
        honeypot_logger.info(f'"action": "decoy_key_used", "ip": "{client_ip}", "path": "{request.url.path}"')
        return "decoy"
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
