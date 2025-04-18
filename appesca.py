import streamlit as st

# Configurar la página (DEBE ser la primera llamada a Streamlit)
st.set_page_config(
    page_title="Travel Tracker",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Importaciones
import os
from dotenv import load_dotenv
from components.auth_class import Authentication
from components.navigation import setup_sidebar, show_footer

# Cargar variables de entorno
load_dotenv()

def main():
    """Función principal de la aplicación"""
    
    # Crear instancia de Authentication
    auth = Authentication()
    
    # Verificar autenticación
    if auth.authenticate():
        # Usuario autenticado, mostrar contenido principal
        setup_sidebar()
        show_main_content(auth)
    
    # Mostrar pie de página
    show_footer()

def show_main_content(auth):
    """Mostrar contenido principal para usuarios autenticados"""
    
    # Obtener datos del usuario actual
    user = auth.get_current_user()
    
    # Título de bienvenida
    st.title(f"🌍 Bienvenido a Travel Tracker, {user.get('name', 'Usuario')}")
    
    # Información de la aplicación
    st.write("Selecciona una opción del menú lateral para comenzar.")
    
    # Mostrar resumen de opciones disponibles
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("🗺️ **Mapa de Viajes**\n\nVisualiza todos tus viajes en un mapa interactivo.")
        if st.button("Ver Mapa", use_container_width=True):
            st.switch_page("pages/02_🗺️_Mapa.py")
    
    with col2:
        st.info("📊 **Mis Viajes**\n\nConsulta y analiza tus viajes registrados.")
        if st.button("Ver Mis Viajes", use_container_width=True):
            st.switch_page("pages/03_📊_Estadísticos.py")
    
    with col3:
        # Si es admin, mostrar opción de gestión de usuarios
        if user.get('role') == 'admin':
            st.info("👥 **Gestión de Usuarios**\n\nAdministra los usuarios de la aplicación.")
            if st.button("Gestionar Usuarios", use_container_width=True):
                st.switch_page("pages/05_👥_Usuarios.py")
        else:
            st.info("⚙️ **Configuración**\n\nPersonaliza tu experiencia en la aplicación.")
            if st.button("Configuración", use_container_width=True):
                st.switch_page("pages/06_⚙️_Configuración.py")
    
    # Información sobre la aplicación
    with st.expander("ℹ️ Acerca de Travel Tracker"):
        st.markdown("""
        **Travel Tracker** es una aplicación para rastrear y visualizar tus viajes.
        
        La aplicación te permite:
        - Ver tus viajes en un mapa interactivo
        - Analizar estadísticas de tus viajes
        - Gestionar tu perfil y preferencias
        
        Selecciona una opción del menú lateral para comenzar a explorar.
        """)

if __name__ == "__main__":
    main()