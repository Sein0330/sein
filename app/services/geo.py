import geoip2.database
from app.core.config import settings
import os

# Cek apakah file database ada
if not os.path.exists(settings.GEOIP_DB_PATH):
    print(f"WARNING: Database GeoIP belum ada di {settings.GEOIP_DB_PATH}")

reader = None

def get_reader():
    global reader
    if reader is None:
        reader = geoip2.database.Reader(settings.GEOIP_DB_PATH)
    return reader

def lookup_ip(ip_address: str) -> dict:
    try:
        r = get_reader()
        response = r.city(ip_address)
        return {
            "ip": ip_address,
            "city": response.city.name,
            "region": response.subdivisions.most_specific.name,
            "country": response.country.name,
            "country_code": response.country.iso_code,
            "latitude": response.location.latitude,
            "longitude": response.location.longitude,
            "timezone": response.location.time_zone,
            "postal_code": response.postal.code
        }
    except geoip2.errors.AddressNotFoundError:
        return {"error": "IP tidak ditemukan di database"}
    except Exception as e:
        return {"error": f"Terjadi kesalahan internal: {str(e)}"}
