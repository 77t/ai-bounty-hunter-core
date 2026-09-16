# utils/__init__.py
import os
import logging
from datetime import datetime

def setup_logger(name: str) -> logging.Logger:
    """Setup logger dengan format standar."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s [%(name)s]: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def validate_secrets():
    """Validasi environment variables wajib."""
    required = ['HF_TOKEN', 'SUPABASE_URL', 'SUPABASE_SERVICE_KEY']
    missing = [k for k in required if not os.environ.get(k)]
    if missing:
        raise EnvironmentError(f"Missing secrets: {', '.join(missing)}")

def format_response(status: str, data=None, message: str = "") -> dict:
    """Format response JSON standar."""
    return {
        "status": status,
        "data": data,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }

def get_timestamp_id() -> str:
    """Generate unique ID berdasarkan timestamp."""
    return datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
  
