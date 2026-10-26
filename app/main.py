from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.security import verify_cloudflare, verify_api_key
from app.routers import track, decoy

# Setup Rate Limiter (30 request per menit per IP)
limiter = Limiter(key_func=get_remote_address, default_limits=["30/minute"])

app = FastAPI(
    title=settings.APP_NAME,
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

# Pasang rate limiter ke app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Daftarin router
app.include_router(track.router)
app.include_router(decoy.router)

# Pasang proteksi Cloudflare global
app.dependencies = [Depends(verify_cloudflare)]

# Handler error generic (biar stack trace gak bocor)
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"}
    )

# Handler 404 (Not Found) generic
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Not Found"}
    )

@app.get("/")
@limiter.limit("10/minute") # Health check lebih ketat (10x per menit)
async def health_check(request: Request):
    return {"status": "ok"}

@app.get("/about")
async def about(auth_type: str = Depends(verify_api_key)):
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "attribution": "GeoLite2 data created by MaxMind, available from https://www.maxmind.com",
        "auth_mode": auth_type
    }
