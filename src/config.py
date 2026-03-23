import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_RAW = os.path.join(BASE_DIR, "data_raw")
DATA_PROCESSED = os.path.join(BASE_DIR, "data_processed")
LOG_PATH = os.path.join(BASE_DIR, "logs", "etl.log")

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "SUA_SENHA",
    "database": "hospital_dw"
}
