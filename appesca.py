import streamlit as st

# Configurar la página 
st.set_page_config(
    page_title="PescaApp",
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
    
    # Logos en el encabezado
    logos_col1, logos_col2, logos_col3 = st.columns([1, 1, 1])
    
    with logos_col1:
        try:
            st.image("assets/logo1.png", width=150)
        except:
            st.error("No se pudo cargar logo1.png")
    
    with logos_col2:
        try:
            st.image("assets/logo2.png", width=150)
        except:
            st.error("No se pudo cargar logo2.png")
    
    with logos_col3:
        try:
            st.image("assets/logo3.png", width=150)
        except:
            st.error("No se pudo cargar logo3.png")
    
    # Título de bienvenida
    st.title(f"🌍 Bienvenido a PescApp, {user.get('name', 'Usuario')}")
    st.markdown("Este es un proyecto académico desarrollado por investigadores de **ECOSUR** y de la **UABC** con financiamiento de **CCyTET**." \
    "\n" \
    "La aplicación tiene como objetivo rastrear y visualizar tus viajes de pesca, promover la trazabilidad pesquera, así como proporcionar información valiosa para la toma de decisiones.")
    
    # Mostrar disclaimer solo si no ha sido descartado
    if 'disclaimer_dismissed' not in st.session_state:
        st.session_state.disclaimer_dismissed = False

    if not st.session_state.disclaimer_dismissed:
        col1, col2 = st.columns([0.9, 0.1])
        with col1:
            st.warning("""
                **AVISO IMPORTANTE**
                
                Esta aplicación es un proyecto académico desarrollado con fines de investigación y demostración. Si bien busca 
                promover la trazabilidad de productos pesqueros y proporcionar información valiosa para sus usuarios, no debe 
                considerarse como una herramienta de seguridad o sistema de auxilio en tiempo real.

                El Colegio de la Frontera Sur (ECOSUR) y la Universidad Autónoma de Baja California (UABC) proporcionan esta 
                plataforma en su estado actual, sin garantías específicas sobre su funcionamiento o precisión. Las instituciones 
                mencionadas quedan exentas de cualquier responsabilidad derivada del uso de esta aplicación.
            """)
        with col2:
            if st.button("✕", help="Cerrar aviso"):
                st.session_state.disclaimer_dismissed = True
                st.rerun()

    # Enlaces a documentos legales
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📄 Leer Términos y Condiciones", use_container_width=True):
            st.info("Los términos y condiciones estarán disponibles próximamente.")
    with col2:
        if st.button("🔒 Consultar Aviso de Privacidad", use_container_width=True):
            st.info("El aviso de privacidad estará disponible próximamente.")
    # Información de la aplicación
    st.write("Selecciona una opción del menú lateral para comenzar.")
    
    # Mostrar resumen de opciones disponibles
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.info("🗺️ **Mapa de Viajes**\n\nVisualiza todos tus viajes en un mapa interactivo.")
        if st.button("Ver Mapa", use_container_width=True):
            st.switch_page("pages/02_🗺️_Map.py")
    
    with col2:
        st.info("📊 **Mis Viajes**\n\nConsulta y analiza tus viajes registrados.")
        if st.button("Ver Mis Viajes", use_container_width=True):
            st.switch_page("pages/03_📊_My_Travels.py")
    
    with col3:
        # Si es admin, mostrar opción de gestión de usuarios
        if user.get('role') == 'admin':
            st.info("👥 **Gestión de Usuarios**\n\nAdministra los usuarios de la aplicación.")
            if st.button("Gestionar Usuarios", use_container_width=True):
                st.switch_page("pages/04_👥_Users.py")
        else:
            st.info("⚙️ **Configuración**\n\nPersonaliza tu experiencia en la aplicación.")
            if st.button("Configuración", use_container_width=True):
                st.switch_page("pages/05_⚙️_Settings.py")
    
    with col4:
        st.info("🤖 **PePeBot**\n\nAsistente virtual para resolver tus dudas (próximamente).")
        if st.button("Chatear con PePeBot", use_container_width=True, disabled=True):
            st.info("Funcionalidad en desarrollo. ¡Estará disponible pronto!")
    
    # Información sobre la aplicación
    with st.expander("ℹ️ Acerca de PescApp"):
        st.markdown("""
        **PescApp** es una aplicación para rastrear y visualizar tus viajes.
        
        La aplicación te permite:
        - Ver tus viajes en un mapa interactivo
        - Analizar estadísticas de tus viajes
        - Gestionar tu perfil y preferencias
        
        Selecciona una opción del menú lateral para comenzar a explorar.
        """)
    
    # Información de contacto con desarrolladores
    st.divider()
    st.subheader("Contacto con Desarrolladores")
    
      
  
    st.markdown("""
        ### Soporte Técnico
        - **Email:** cavieses@uabcs.mx
        
        """)
    

    
    st.write("Para reportar problemas o sugerir mejoras, por favor contacta al equipo de soporte técnico.")

if __name__ == "__main__":
    main()