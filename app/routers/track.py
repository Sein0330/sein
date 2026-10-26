from fastapi import APIRouter, Depends, HTTPException
from app.core.security import verify_api_key
from app.services.geo import lookup_ip
import ipaddress

router = APIRouter()

@router.get("/track/{ip_address}")
async def track_ip(ip_address: str, auth_type: str = Depends(verify_api_key)):
    # Validasi format IP (IPv4 atau IPv6)
    try:
        ipaddress.ip_address(ip_address)
    except ValueError:
        raise HTTPException(status_code=400, detail="Format IP tidak valid")
        
    # Panggil service
    result = lookup_ip(ip_address)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
        
    return {
        "status": "success",
        "auth_mode": auth_type,
        "data": result
    }
