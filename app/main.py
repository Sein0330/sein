from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os

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

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(track.router)
app.include_router(decoy.router)

app.dependencies = [Depends(verify_cloudflare)]

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"}
    )

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Not Found"}
    )

@app.get("/")
@limiter.limit("10/minute")
async def health_check(request: Request):
    return {"status": "ok"}

@app.get("/about")
async def about(auth_type: str = Depends(verify_api_key)):
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "attribution": "GeoLite2 data created by MaxMind",
        "auth_mode": auth_type
    }

# ================= ENDPOINT DOWNLOAD FILE =================
@app.get("/download/{filename}")
async def download_file(filename: str):
    # Path folder tempat nyimpen hasil capture
    file_path = f"/home/almaarij/sein/{filename}"
    
    # Keamanan: cegah path traversal (../)
    if ".." in filename or "/" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
        
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
        
    return FileResponse(path=file_path, filename=filename, media_type="image/png")
