import streamlit as st
from components.authentication import require_authentication
from components.navigation import setup_sidebar, show_header, show_footer
from services.travel_service import get_available_travels
import pandas as pd

# Configurar la página
st.set_page_config(
    page_title="PescApp",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurar la barra lateral
setup_sidebar()

# Verificar autenticación
user = require_authentication()

# Mostrar header
show_header(
    "🏠 Bienvenido a PescApp",
    f"Hola, {user.get('name', 'Usuario')}! Aquí puedes ver un resumen de tus viajes y actividad."
)

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

# Obtener datos de viajes
travels = get_available_travels()

def main():
    # Métricas principales
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Total de Viajes", 
            value=len(travels),
            delta=None
        )
    
    with col2:
        total_distance = sum(travel.get("distance", 0) for travel in travels)
        st.metric(
            label="Distancia Total", 
            value=f"{total_distance} km",
            delta=None
        )
    
    with col3:
        role = user.get("role", "user")
        st.metric(
            label="Nivel de Acceso", 
            value=role.capitalize(),
            delta=None
        )

    # Sección de accesos rápidos
    st.subheader("⚡ Accesos Rápidos")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🗺️ Ver Mapa de Viajes", use_container_width=True):
            st.switch_page("pages/02_🗺️_Mapa.py")
    
    with col2:
        if st.button("📊 Ver Mis Viajes", use_container_width=True):
            st.switch_page("pages/03_📊_Estadísticos.py")
    
    with col3:
        if user.get("role") == "admin":
            if st.button("👥 Gestionar Usuarios", use_container_width=True):
                st.switch_page("pages/05_👥_Usuarios.py")
        else:
            if st.button("⚙️ Configuración", use_container_width=True):
                st.switch_page("pages/07_⚙️_Configuración.py")

    # Sección de últimos viajes
    st.subheader("📋 Últimos Viajes")
    
    if travels:
        df = pd.DataFrame(travels)
        columns_to_show = ["travel_id", "timestamp", "user_email"]
        available_columns = [col for col in columns_to_show if col in df.columns]
        
        if available_columns:
            st.dataframe(
                df[available_columns].head(5),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No hay datos de viajes disponibles para mostrar.")
    else:
        st.info("No hay viajes disponibles. ¡Comienza a registrar tus viajes!")
    
    # Información de la aplicación
    with st.expander("ℹ️ Acerca de PescApp"):
        st.markdown("""
        **PescApp** es una aplicación diseñada para rastrear y visualizar tus viajes.
        
        La aplicación te permite:
        
        - Visualizar tus viajes en un mapa interactivo
        - Ver estadísticas de tus viajes
        - Administrar usuarios y roles (solo administradores)
        
        Para comenzar, selecciona una de las opciones del menú lateral.
        """)

if __name__ == "__main__":
    main()

# Mostrar pie de página
show_footer()