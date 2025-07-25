import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

@dataclass
class Config:
    apollo_api_key: str
    openai_api_key: str
    hunter_api_key: str
    google_sheets_endpoint: Optional[str] = None
    output_directory: str = "data/output"
    log_level: str = "INFO"

def load_config() -> Config:
    """
    Load configuration from environment variables
    """
    load_dotenv()  # Load variables from .env file
    
    apollo_api_key = os.getenv("APOLLO_API_KEY")
    if not apollo_api_key:
        raise ValueError("APOLLO_API_KEY environment variable is required")
    
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    hunter_api_key = os.getenv("HUNTER_API_KEY")
    if not hunter_api_key:
        raise ValueError("HUNTER_API_KEY environment variable is required")
    
    # Google Sheets endpoint is optional
    google_sheets_endpoint = os.getenv("GOOGLE_SHEETS_ENDPOINT")
    
    return Config(
        apollo_api_key=apollo_api_key,
        openai_api_key=openai_api_key,
        hunter_api_key=hunter_api_key,
        google_sheets_endpoint=google_sheets_endpoint,
        output_directory=os.getenv("OUTPUT_DIR", "data/output"),
        log_level=os.getenv("LOG_LEVEL", "INFO")
    )