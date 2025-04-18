import streamlit as st
from components.auth_class import Authentication

# Función para configurar la barra lateral con navegación
def setup_sidebar():
    # Crear instancia de autenticación
    auth = Authentication()
    
    # Obtener información del usuario
    user = auth.get_current_user()
    
    if user:
        st.sidebar.title("🌍 Travel Tracker")
        
        # Mostrar información del usuario
        st.sidebar.write(f"**Usuario:** {user.get('name', 'Usuario')}")
        st.sidebar.write(f"**Email:** {user.get('email', '')}")
        st.sidebar.write(f"**Rol:** {user.get('role', 'user').capitalize()}")
        
        st.sidebar.divider()
        

        # Botón de cerrar sesión
        if st.sidebar.button("🚪 Cerrar Sesión"):
            auth.logout()
    else:
        st.sidebar.title("🌍 PescApp")
        st.sidebar.info("Por favor, inicie sesión para acceder a la aplicación.")

# Función para mostrar un header consistente
def show_header(title, subtitle=None):
    st.title(title)
    
    if subtitle:
        st.markdown(subtitle)
    
    st.divider()

# Función para mostrar el pie de página
def show_footer():
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**PescApp** © 2025")
    
    with col2:
        st.markdown("Desarrollado con Streamlit y Firebase")
    
    with col3:
        st.markdown("Versión 1.0.0")