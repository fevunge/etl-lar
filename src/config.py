import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DATA_RAW = BASE_DIR / "data_raw"
OUTPUT_DIR = BASE_DIR / "output"
LOG_PATH = BASE_DIR / "logs" / "etl.log"

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "0.0.0.0:4501"),
    "port": int(os.getenv("DB_PORT", "4501")),
    "user": os.getenv("DB_USER", "zfleet"),
    "password": os.getenv("DB_PASSWORD", "papers-catch-sorrows"),
    "database": os.getenv("DB_NAME", "zfleet_auth"),
}
