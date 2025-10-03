"""Secrets loader. Reads environment variables and (optionally) a .env file.

Usage:
    from src.secrets import SECRETS
    rf_key = SECRETS.ROBOFLOW_API_KEY
"""
from pathlib import Path
import os

# try to load .env if python-dotenv is installed
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
except Exception:
    # python-dotenv is optional; env vars may already be set in the OS
    pass


class _Secrets:
    def __init__(self):
        self.ROBOFLOW_API_KEY = os.environ.get('ROBOFLOW_API_KEY')
        self.ROBOFLOW_WORKSPACE = os.environ.get('ROBOFLOW_WORKSPACE')
        self.ROBOFLOW_PROJECT = os.environ.get('ROBOFLOW_PROJECT')
        self.ROBOFLOW_VERSION = os.environ.get('ROBOFLOW_VERSION')
        self.BEST_WEIGHTS = os.environ.get('BEST_WEIGHTS')


SECRETS = _Secrets()
