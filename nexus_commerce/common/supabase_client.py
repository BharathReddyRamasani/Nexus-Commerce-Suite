"""
Nexus Commerce Suite — Supabase Client
========================================
Singleton pattern for the Supabase client with logging and connection validation.
"""
import streamlit as st
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
    Supports Streamlit Secrets (Cloud) and Environment Variables (Local).
    """
    global _supabase_client

    if _supabase_client is None:
        # 1. Try Streamlit Secrets (Best for Cloud)
        url = ""
        key = ""
        
        try:
            if hasattr(st, "secrets"):
                url = st.secrets.get("SUPABASE_URL", "").strip()
                key = st.secrets.get("SUPABASE_KEY", "").strip()
                if url: logger.info("Using Streamlit Secrets for database connection.")
        except Exception:
            pass

        # 2. Try Environment Variables / .env (Best for Local)
        if not url or not key:
            load_dotenv()
            url = os.environ.get("SUPABASE_URL", "").strip()
            key = os.environ.get("SUPABASE_KEY", "").strip()
            if url: logger.info("Using Environment Variables for database connection.")

        if not url or not key or url.startswith("your_"):
            raise ValueError(
                "SUPABASE_URL or SUPABASE_KEY is missing. "
                "Local: Set them in .env | Cloud: Add them to Streamlit Dashboard -> Secrets."
            )

        try:
            logger.info("Initializing Supabase client for %s", url[:30] + "...")
            _supabase_client = create_client(url, key)
            logger.info("Supabase client initialized successfully.")
        except Exception as e:
            logger.error("Failed to create Supabase client: %s", e)
            raise ConnectionError(
                f"Connection Failed. URL: {url[:25]}... Detail: {e}"
            )

    return _supabase_client


def reset_supabase_client():
    """Clears the singleton client to force a re-read of credentials."""
    global _supabase_client
    _supabase_client = None
    logger.info("Supabase client reset. Will re-initialize on next request.")


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
