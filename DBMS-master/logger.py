"""
logger.py
---------
Shared logger for the Pharmacy Lab Management System.
Logs to both the console and a rotating log file (pharmacy.log).
Import this in any module: from logger import logger
"""

import logging
from logging.handlers import RotatingFileHandler

LOG_FILE = 'pharmacy.log'

# Create a named logger
logger = logging.getLogger('PharmacyApp')
logger.setLevel(logging.DEBUG)

# Formatter
formatter = logging.Formatter(
    fmt='%(asctime)s | %(levelname)-8s | %(module)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# File handler — rotates after 1 MB, keeps 3 backups
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=3)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

# Console handler — only INFO and above
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)
