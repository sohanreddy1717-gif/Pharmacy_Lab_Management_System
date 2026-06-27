"""
config.py
---------
Centralized database configuration.
Loads credentials from the .env file using python-dotenv.
Never hardcode passwords in source code.
"""

import os
from dotenv import load_dotenv

# Load variables from .env file into environment
load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'Pharmacydb'),
}

DB_CONFIG_NO_DB = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
}

ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'Pharmacydb')
