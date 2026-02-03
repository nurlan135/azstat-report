# Configuration for azstat-report backend

from pathlib import Path


class Config:
    """Application configuration."""
    
    # Database
    DB_PATH = Path("data/reports.db")
    
    # File limits
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {".html", ".htm"}
    
    # Validation
    ANOMALY_THRESHOLD = 0.5  # 50% change threshold
    
    # Paths
    UPLOAD_DIR = Path("data/uploads")
    
    # Form codes
    FORM_1ISTH = "03104055"  # Annual
    FORM_12ISTH = "03104047"  # Monthly


# Singleton config instance
config = Config()
