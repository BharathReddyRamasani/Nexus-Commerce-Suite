from ..common.supabase_client import get_supabase_client

def sign_up(email, password):
    """
    Handles new user registration using Supabase Auth.
    Returns a dictionary with 'success' (bool) and 'message' (str).
    """
    supabase = get_supabase_client()
    try:
        # Use the Supabase client's built-in authentication methods
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
        })

        # Supabase returns a user object on success, even if email confirmation is needed
        if response.user:
            return {"success": True, "message": "Registration successful! Please log in."}
        # Supabase often returns session=None on initial signup without error
        elif response.session is None and response.user is None:
             # This can happen if email confirmation is on, but we treat it as success for now
             return {"success": True, "message": "Registration successful! Please check your email to confirm."}
        else:
            # Fallback for unexpected responses
            return {"success": False, "message": "An unknown error occurred during registration."}

    except Exception as e:
        # Provide user-friendly error messages for common issues
        error_message = str(e)
        if "User already registered" in error_message:
            return {"success": False, "message": "This email is already registered. Please try logging in."}
        if "Password should be at least 6 characters" in error_message:
            return {"success": False, "message": "Password must be at least 6 characters long."}
        
        return {"success": False, "message": f"An unexpected error occurred: {error_message}"}

def sign_in(email, password):
    """
    Handles user login using Supabase Auth.
    Returns a dictionary with 'success' (bool) and 'message' (str).
    """
    supabase = get_supabase_client()
    try:
        # Use the Supabase client's sign-in method
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password,
        })

        # On successful login, Supabase returns a session object
        if response.session:
            return {"success": True, "message": "Login successful!"}
        else:
            return {"success": False, "message": "An unknown error occurred during login."}
            
    except Exception as e:
        # Provide a user-friendly message for the most common login failure
        error_message = str(e)
        if "Invalid login credentials" in error_message:
            return {"success": False, "message": "Invalid email or password. Please try again."}
            
        return {"success": False, "message": f"An unexpected error occurred: {error_message}"}

