"""
Nexus Commerce Suite — Authentication Logic
==============================================
Handles user sign-up and sign-in via Supabase Auth.
"""
import logging
from ..common.supabase_client import get_supabase_client

logger = logging.getLogger("nexus_commerce.auth")


def sign_up(email: str, password: str) -> dict:
    """
    Register a new user via Supabase Auth.
    Returns: {'success': bool, 'message': str}
    """
    supabase = get_supabase_client()
    try:
        logger.info("Attempting registration for %s", email)
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
        })

        if response.user:
            logger.info("Registration successful for %s", email)
            return {"success": True, "message": "Registration successful! Please log in."}
        elif response.session is None and response.user is None:
            return {"success": True, "message": "Registration successful! Please check your email to confirm."}
        else:
            return {"success": False, "message": "An unknown error occurred during registration."}

    except Exception as e:
        error_message = str(e)
        logger.warning("Registration failed for %s: %s", email, error_message)

        if "User already registered" in error_message:
            return {"success": False, "message": "This email is already registered. Please try logging in."}
        if "Password should be at least 6 characters" in error_message:
            return {"success": False, "message": "Password must be at least 6 characters long."}

        return {"success": False, "message": f"Registration error: {error_message}"}


def sign_in(email: str, password: str) -> dict:
    """
    Authenticate a user via Supabase Auth.
    Returns: {'success': bool, 'message': str}
    """
    supabase = get_supabase_client()
    try:
        logger.info("Attempting login for %s", email)
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password,
        })

        if response.session:
            logger.info("Login successful for %s", email)
            return {"success": True, "message": "Login successful!"}
        else:
            return {"success": False, "message": "An unknown error occurred during login."}

    except Exception as e:
        error_message = str(e)
        logger.warning("Login failed for %s: %s", email, error_message)

        if "Invalid login credentials" in error_message:
            return {"success": False, "message": "Invalid email or password. Please try again."}
        
        if "Email not confirmed" in error_message:
            return {
                "success": False, 
                "message": "📧 **Email Not Confirmed.** Please check your inbox or disable 'Confirm Email' in Supabase Dashboard -> Authentication -> Settings."
            }

        return {"success": False, "message": f"Login error: {error_message}"}
