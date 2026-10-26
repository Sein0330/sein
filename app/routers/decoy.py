from fastapi import APIRouter, Request
from app.core.logging import honeypot_logger
from app.core.config import settings
import asyncio
import json

router = APIRouter()

async def tarpit_and_log(request: Request, fake_data: dict):
    if not settings.ENABLE_HONEYPOT:
        return {"status": "disabled"}

    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    
    # Log serangan
    log_msg = json.dumps({
        "action": "honeypot_hit",
        "ip": client_ip,
        "path": request.url.path,
        "ua": user_agent
    })
    honeypot_logger.info(f'{log_msg}')
    
    # Tarpit: Delay 3 detik biar hacker nunggu
    await asyncio.sleep(3)
    return fake_data

@router.get("/admin")
async def fake_admin(request: Request):
    return await tarpit_and_log(request, {"status": "ok", "msg": "Admin panel (fake)", "user": "admin"})

@router.get("/.env")
async def fake_env(request: Request):
    return await tarpit_and_log(request, {"DB_PASSWORD": "super_secret_fake_123", "API_KEY": "fake_key_abc"})

@router.post("/wp-login.php")
async def fake_wp(request: Request):
    return await tarpit_and_log(request, {"error": "Invalid credentials (fake)"})
