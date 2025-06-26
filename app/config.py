import os
from typing import Optional

# GitHub App configuration
GITHUB_APP_ID: Optional[str] = os.getenv("GITHUB_APP_ID")
GITHUB_PRIVATE_KEY: Optional[str] = os.getenv("GITHUB_PRIVATE_KEY")
GITHUB_WEBHOOK_SECRET: Optional[str] = os.getenv("GITHUB_WEBHOOK_SECRET")

# Supabase configuration
SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL")
SUPABASE_KEY: Optional[str] = os.getenv("SUPABASE_ANON_KEY")

# Default values for development/testing
DEFAULT_WEBHOOK_SECRET = "your-webhook-secret-here"

def get_github_webhook_secret() -> str:
    """Get GitHub webhook secret from environment or use default"""
    return GITHUB_WEBHOOK_SECRET or DEFAULT_WEBHOOK_SECRET

def get_github_app_id() -> str:
    """Get GitHub App ID from environment"""
    if not GITHUB_APP_ID:
        raise ValueError("GITHUB_APP_ID environment variable is required")
    return GITHUB_APP_ID

def get_github_private_key() -> str:
    """Get GitHub private key from environment"""
    if not GITHUB_PRIVATE_KEY:
        raise ValueError("GITHUB_PRIVATE_KEY environment variable is required")
    return GITHUB_PRIVATE_KEY

def get_supabase_url() -> str:
    """Get Supabase URL from environment"""
    if not SUPABASE_URL:
        raise ValueError("SUPABASE_URL environment variable is required")
    return SUPABASE_URL

def get_supabase_key() -> str:
    """Get Supabase anon key from environment"""
    if not SUPABASE_KEY:
        raise ValueError("SUPABASE_ANON_KEY environment variable is required")
    return SUPABASE_KEY
