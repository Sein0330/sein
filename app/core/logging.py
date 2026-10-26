import logging
import os
from app.core.config import settings

# Pastiin folder logs ada
os.makedirs(settings.LOG_DIR, exist_ok=True)

# Setup logger khusus honeypot
honeypot_logger = logging.getLogger("honeypot")
honeypot_logger.setLevel(logging.INFO)

# Format: JSON biar gampang di-parse nanti
formatter = logging.Formatter('{"time": "%(asctime)s", "level": "%(levelname)s", "msg": %(message)s}')

# File handler
fh = logging.FileHandler(os.path.join(settings.LOG_DIR, "honeypot.log"))
fh.setFormatter(formatter)
honeypot_logger.addHandler(fh)

# Jangan kirim ke stdout (biar gak numpuk di journalctl)
honeypot_logger.propagate = False
