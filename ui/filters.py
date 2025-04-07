import streamlit as st
from datetime import datetime, timedelta

from utils.database import get_all_users, get_monitor_assigned_users

def filter_controls(db, user_role, user_email):
    """
    Common filter controls for all pages
    
    Args:
        db: Firestore client
        user_role: Role of the current user
        user_email: Email of the current user
        
    Returns:
        tuple: (start_datetime, end_datetime, selected_users)
    """
    st.sidebar.header("Filtros")
    
    # Date filters
    st.sidebar.subheader("Filtrar por Fecha")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input("Desde", 
                                  value=datetime.now() - timedelta(days=30),
                                  max_value=datetime.now())
    with col2:
        end_date = st.date_input("Hasta", 
                                value=datetime.now(),
                                max_value=datetime.now())
    
    # Convert to datetime
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    # User selection based on role
    st.sidebar.subheader("Filtrar por Usuario")
    
    if user_role == 'admin':
        # Admin can see all users
        all_users = get_all_users(db)
        user_options = ["Todos"] + all_users
        selected_users = st.sidebar.multiselect("Seleccionar Usuarios", user_options, default=["Todos"])
        
        # Handle "Todos" option
        if "Todos" in selected_users and len(selected_users) > 1:
            selected_users = ["Todos"]
    
    elif user_role == 'monitor':
        # Monitor can see only assigned users
        assigned_users = get_monitor_assigned_users(db, user_email)
        if not assigned_users:
            st.sidebar.warning("No tienes usuarios asignados")
            assigned_users = []
        
        user_options = ["Todos"] + assigned_users
        selected_users = st.sidebar.multiselect("Seleccionar Usuarios", user_options, default=["Todos"])
        
        # Handle "Todos" option
        if "Todos" in selected_users and len(selected_users) > 1:
            selected_users = ["Todos"]
    
    else:
        # Regular user can only see their own data
        selected_users = [user_email]
    
    return start_datetime, end_datetime, selected_users

def get_users_to_analyze(db, user_role, user_email, selected_users):
    """
    Determine which users to analyze based on selection and role
    
    Args:
        db: Firestore client
        user_role: Role of the current user
        user_email: Email of the current user
        selected_users: List of selected users from filter
        
    Returns:
        list: Users to analyze
    """
    if "Todos" in selected_users:
        if user_role == 'admin':
            return get_all_users(db)
        elif user_role == 'monitor':
            return get_monitor_assigned_users(db, user_email)
        else:
            return [user_email]
    else:
        return selected_users