"""
config.py
Handles application configuration, environment variables, and global constants.
"""

import os

# --- Global Logic Constants ---
# These are used by core.py and services.py to maintain consistent behavior
DEFAULT_ALLOCATION_TYPE = "proportional"
MAX_ALLOCATION_LIMIT = 1000000  # Safety cap for allocation quantities
PRECISION_DECIMALS = 4          # Number of decimals for quantity calculations


class Settings:
    """
    Application settings class. 
    Values are loaded from environment variables with safe defaults.
    """
    def __init__(self):
        # General App Info
        self.app_name: str = os.getenv("APP_NAME", "Smart Allocation API")
        self.version: str = "1.0.0"
        self.app_env: str = os.getenv("APP_ENV", "development")  # development, staging, production
        
        # Debugging
        # Converts string env var to boolean
        self.debug: bool = os.getenv("DEBUG_MODE", "False").lower() == "true"
        
        # API Security (Placeholder for future use)
        self.api_key: str = os.getenv("API_KEY", "dev-key-123")

        # Inventory Specifics
        self.allow_over_allocation: bool = os.getenv("ALLOW_OVER_ALLOCATION", "False").lower() == "true"


# Initialize a single instance of settings to be imported across the app
settings = Settings()

# Documentation for developers
def get_config_summary():
    """Returns a brief summary of the active configuration."""
    return {
        "app": settings.app_name,
        "version": settings.version,
        "environment": settings.app_env,
        "debug": settings.debug
    }
