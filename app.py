import json
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from utils.database import (
    obtain_firestore_client, 
    get_user_role,
    manage_user_roles
)
from utils.auth_module import Authentication
from ui.navigation import navigation
from pages.map_page import page_map
from pages.general_stats import page_general_stats
from pages.user_stats import page_user_stats

# Configure the page
st.set_page_config(page_title="Pescapp Dashboard", page_icon="🎣", layout="wide")

# Initialize authentication
auth = Authentication()

def main():
    # Authenticate user
    if not auth.authenticate():
        return

    # Initialize Firestore client
    db = obtain_firestore_client()
    
    # Get user role
    user_role = st.session_state.get('user_role', 'user')
    user_email = st.session_state['user_email']

    # User is authenticated, show dashboard header
    st.sidebar.title(f"Pescapp Dashboard 🎣")
    st.sidebar.write(f"Usuario: {user_email}")
    st.sidebar.write(f"Rol: {user_role.capitalize()}")

    # Add logout button
    if st.sidebar.button("Cerrar Sesión"):
        auth.logout()
        return
    
    # Add role management for admins
    if user_role == 'admin':
        if st.sidebar.button("Gestionar Usuarios"):
            st.session_state['show_user_management'] = True
            st.rerun()
    
    # Show user management if requested
    if st.session_state.get('show_user_management', False):
        manage_user_roles(db, user_email)
        
        if st.button("Volver al Dashboard"):
            st.session_state['show_user_management'] = False
            st.rerun()
        
        return  # Skip the rest of the dashboard

    # Navigation and page display
    page = navigation()
    
    try:
        if page == "Mapa de Viajes":
            page_map(db, user_role, user_email)
        elif page == "Estadísticas Generales":
            page_general_stats(db, user_role, user_email)
        elif page == "Estadísticas por Usuario":
            page_user_stats(db, user_role, user_email)
    except Exception as e:
        st.error(f"Error inesperado: {str(e)}")
        import traceback
        st.error(traceback.format_exc())

if __name__ == "__main__":
    main()