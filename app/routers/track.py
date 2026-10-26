from fastapi import APIRouter, Depends, HTTPException, Request
from app.core.security import verify_api_key
from app.services.geo import lookup_ip
from app.core.config import settings
import ipaddress
import random

router = APIRouter()

@router.get("/track/{ip_address}")
async def track_ip(request: Request, ip_address: str, auth_type: str = Depends(verify_api_key)):
    try:
        ipaddress.ip_address(ip_address)
    except ValueError:
        raise HTTPException(status_code=400, detail="Format IP tidak valid")
        
    # JIKA PAKE DECOY KEY, KASIH DATA PALSU
    if auth_type == "decoy":
        return {
            "status": "success",
            "auth_mode": "real", # Pura-pura sukses
            "data": {
                "ip": ip_address,
                "city": "Nowhere",
                "region": "Antarctica",
                "country": "Antarctica",
                "country_code": "AQ",
                "latitude": round(random.uniform(-90, 90), 4),
                "longitude": round(random.uniform(-180, 180), 4),
                "timezone": "Antarctica/Troll",
                "postal_code": "00000"
            }
        }

    # JIKA REAL, KASIH DATA ASLI
    result = lookup_ip(ip_address)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
        
    return {
        "status": "success",
        "auth_mode": auth_type,
        "data": result
    }
