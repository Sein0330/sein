import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env dari root project
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "sein")
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "8765"))

    API_KEY_REAL: str = os.getenv("API_KEY_REAL", "")
    API_KEY_DECOY: str = os.getenv("API_KEY_DECOY", "")

    ENABLE_HONEYPOT: bool = os.getenv("ENABLE_HONEYPOT", "false").lower() == "true"
    ENABLE_CLOUDFLARE_CHECK: bool = os.getenv("ENABLE_CLOUDFLARE_CHECK", "false").lower() == "true"

    GEOIP_DB_PATH: str = os.getenv("GEOIP_DB_PATH", "./data/GeoLite2-City.mmdb")
    LOG_DIR: str = os.getenv("LOG_DIR", "./logs")

settings = Settings()

# Validasi biar gak lupa isi .env
if settings.API_KEY_REAL in ("", "CHANGE_ME_REAL"):
    raise ValueError("API_KEY_REAL belum diisi di .env! Tolong generate dulu.")
