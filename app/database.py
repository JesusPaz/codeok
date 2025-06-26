from supabase import create_client, Client
from .config import get_supabase_url, get_supabase_key
import logging

logger = logging.getLogger(__name__)

# Global Supabase client instance
supabase: Client = None

def get_supabase_client() -> Client:
    """Get or create Supabase client instance"""
    global supabase
    if supabase is None:
        try:
            url = get_supabase_url()
            key = get_supabase_key()
            supabase = create_client(url, key)
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise
    return supabase

def init_database():
    """Initialize database connection"""
    try:
        client = get_supabase_client()
        # Test connection
        response = client.table('repositories').select('id').limit(1).execute()
        logger.info("Database connection established successfully")
        return client
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise
