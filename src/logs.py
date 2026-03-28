import logging

from config import LOG_PATH

LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

# Configure basic logging to console with a specific format and level
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler()
    ]
)