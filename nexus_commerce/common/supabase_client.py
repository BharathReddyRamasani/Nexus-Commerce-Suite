"""
Nexus Commerce Suite — Supabase Client
========================================
Singleton pattern for the Supabase client with logging and connection validation.
"""
import os
import logging
from dotenv import load_dotenv
from supabase import create_client, Client

logger = logging.getLogger("nexus_commerce.supabase")

# ── Global singleton ──
_supabase_client: Client = None


def get_supabase_client() -> Client:
    """
    Creates and returns the Supabase client instance.
    Uses singleton pattern — only one client per process.
    """
    global _supabase_client

    if _supabase_client is None:
        load_dotenv()
        url: str = os.environ.get("SUPABASE_URL", "").strip()
        key: str = os.environ.get("SUPABASE_KEY", "").strip()

        if not url or not key or url.startswith("your_"):
            raise ValueError(
                "SUPABASE_URL and SUPABASE_KEY must be set in your .env file. "
                "Get these from: Supabase Dashboard → Project Settings → API"
            )

        try:
            logger.info("Initializing Supabase client for %s", url[:40] + "…")
            _supabase_client = create_client(url, key)
            logger.info("Supabase client initialized successfully.")
        except Exception as e:
            logger.error("Failed to create Supabase client: %s", e)
            raise ConnectionError(
                f"Could not connect to Supabase. "
                f"Verify your credentials in .env are correct. Details: {e}"
            )

    return _supabase_client


def check_connection() -> bool:
    """
    Verify credentials on startup. Raises ValueError or ConnectionError
    if the connection cannot be established.
    """
    try:
        get_supabase_client()
        return True
    except (ValueError, ConnectionError) as e:
        logger.critical("Database connection check FAILED: %s", e)
        raise
