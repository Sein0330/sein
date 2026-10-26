from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.security import verify_cloudflare, verify_api_key
from app.routers import track

app = FastAPI(
    title=settings.APP_NAME,
    docs_url=None,      # Matikan docs default
    redoc_url=None,
    openapi_url=None    # Sembunyikan openapi.json dari publik
)

# Daftarin router
app.include_router(track.router)

# Pasang proteksi Cloudflare global
app.dependencies = [Depends(verify_cloudflare)]

# Handler error generic (biar stack trace gak bocor)
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"}
    )

@app.get("/")
async def health_check():
    # Tanpa auth, biar Cloudflare bisa probe
    return {"status": "ok"}

@app.get("/about")
async def about(auth_type: str = Depends(verify_api_key)):
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "attribution": "GeoLite2 data created by MaxMind, available from https://www.maxmind.com",
        "auth_mode": auth_type
    }
