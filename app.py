import streamlit as st
import time
from nexus_commerce.common.supabase_client import check_connection
from nexus_commerce.auth import logic as auth_logic

# --- Page Configuration ---
# This sets the title that appears in the browser tab and configures the layout.
# It should be the first Streamlit command in your app for consistency.
st.set_page_config(
    page_title="Nexus Commerce Suite | Login",
    page_icon="🛒",
    layout="centered",  # 'centered' layout is best for a clean login page
    initial_sidebar_state="collapsed"
)

# --- Robust Connection Check ---
# This try/except block runs on startup to verify database credentials.
# It provides a clear, user-friendly error if the connection fails,
# preventing the rest of the app from loading with a cryptic error.
try:
    check_connection()
except (ValueError, ConnectionError) as e:
    st.error(f"**FATAL ERROR:** Could not connect to the database.", icon="🔥")
    st.error(f"Details: {e}")
    st.stop() # Stop the app from rendering further if the connection fails.

# --- Session State Initialization ---
# This ensures that our 'authenticated' flag exists in the session state
# when a user first visits the site. This is key to managing login status.
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_email = ""

# --- Header and Branding ---
st.image("https://placehold.co/600x150/2c3e50/ecf0f1?text=Nexus+Commerce&font=raleway", use_column_width=True)
st.title("Business Management Suite")

# --- Authentication Check ---
# If the user is already authenticated, provide a better user experience by showing
# a welcome message and a direct link to the dashboard.
if st.session_state.authenticated:
    st.success(f"You are already logged in as **{st.session_state.user_email}**.", icon="✅")
    if st.button("Go to Dashboard", use_container_width=True, type="primary"):
        st.switch_page("pages/1_Dashboard.py")
    st.stop()

# --- Login / Register Tabs ---
# Using tabs provides a clean interface for the user to choose their action.
login_tab, register_tab = st.tabs(["**Login**", "**Register**"])

# --- LOGIN TAB ---
with login_tab:
    with st.form("login_form"):
        st.subheader("Login to Your Account")
        email = st.text_input("Email", placeholder="you@example.com")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        login_submitted = st.form_submit_button("Login", use_container_width=True, type="primary")

        if login_submitted:
            if not email or not password:
                st.error("Please enter both email and password.", icon="🚨")
            else:
                with st.spinner("Authenticating..."):
                    response = auth_logic.sign_in(email, password)
                if response['success']:
                    # On successful login, set the session state flags.
                    # These flags will be used to protect all other pages.
                    st.session_state.authenticated = True
                    st.session_state.user_email = email
                    st.success("Login successful! Redirecting...", icon="✅")
                    time.sleep(1) # A small delay to let the user see the success message.
                    st.switch_page("pages/1_Dashboard.py") # The modern way to redirect in Streamlit.
                else:
                    st.error(response['message'], icon="🚨")

# --- REGISTER TAB ---
with register_tab:
    with st.form("register_form"):
        st.subheader("Create a New Account")
        new_email = st.text_input("Email", key="reg_email", placeholder="you@example.com")
        new_password = st.text_input("Password (min. 6 characters)", type="password", key="reg_pass", placeholder="••••••••")
        confirm_password = st.text_input("Confirm Password", type="password", key="reg_pass_confirm", placeholder="••••••••")
        register_submitted = st.form_submit_button("Register", use_container_width=True)

        if register_submitted:
            if not new_email or not new_password:
                st.error("Please enter both email and password.", icon="🚨")
            elif new_password != confirm_password:
                st.error("Passwords do not match.", icon="🚨")
            else:
                with st.spinner("Creating account..."):
                    response = auth_logic.sign_up(new_email, new_password)
                if response['success']:
                    st.success(response['message'], icon="✅")
                    st.info("You can now log in using the Login tab.", icon="ℹ️")
                else:
                    st.error(response['message'], icon="🚨")

