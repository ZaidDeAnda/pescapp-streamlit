import streamlit as st
from components.auth_class import Authentication
from components.navigation import setup_sidebar, show_header, show_footer
from firebase_admin import auth, firestore

# Configurar la página
st.set_page_config(
    page_title="Travel Tracker - Configuración",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Crear instancia de autenticación
auth_instance = Authentication()

# Verificar autenticación
if not auth_instance.authenticate():
    st.stop()

# Configurar la barra lateral
setup_sidebar()

# Obtener información del usuario
user = auth_instance.get_current_user()

# Mostrar header
show_header(
    "⚙️ Configuración",
    "Personaliza tu experiencia en la aplicación."
)

# Función principal
def main():
    # Obtener datos del usuario
    user_id = user.get("id")
    user_name = user.get("name", "")
    user_email = user.get("email", "")
    user_role = user.get("role", "user")
    
    # Mostrar información del perfil
    st.subheader("👤 Perfil de Usuario")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**ID:** {user_id}")
        st.write(f"**Email:** {user_email}")
        st.write(f"**Rol:** {user_role.capitalize()}")
    
    with col2:
        # Formulario para actualizar nombre
        with st.form("actualizar_perfil"):
            nuevo_nombre = st.text_input("Nombre", value=user_name)
            submitted = st.form_submit_button("Actualizar Perfil")
            
            if submitted and nuevo_nombre and nuevo_nombre != user_name:
                try:
                    # Actualizar nombre en Firebase Authentication
                    auth.update_user(
                        user_id,
                        display_name=nuevo_nombre
                    )
                    
                    # Actualizar en Firestore
                    db = firestore.client()
                    db.collection('users').document(user_id).update({
                        'name': nuevo_nombre
                    })
                    
                    # Actualizar en session_state
                    st.session_state['user']['name'] = nuevo_nombre
                    
                    st.success("Perfil actualizado exitosamente")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al actualizar perfil: {e}")
    
    # Preferencias de visualización
    st.divider()
    st.subheader("🖥️ Preferencias de Visualización")
    
    # Tema de la aplicación
    tema = st.radio(
        "Tema de la aplicación:",
        options=["Claro", "Oscuro", "Sistema"],
        horizontal=True,
        index=2  # Por defecto usar el del sistema
    )
    
    # Opciones del mapa
    st.write("#### Opciones del Mapa")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Color de marcadores
        color_marcador = st.color_picker(
            "Color de marcadores:",
            "#1E88E5"
        )
        
        # Tamaño de marcadores
        tamaño_marcador = st.slider(
            "Tamaño de marcadores:",
            min_value=1,
            max_value=10,
            value=5
        )
    
    with col2:
        # Tipo de mapa
        tipo_mapa = st.selectbox(
            "Tipo de mapa por defecto:",
            options=["OpenStreetMap", "Stamen Terrain", "Stamen Toner", "CartoDB positron"]
        )
        
        # Nivel de zoom
        zoom_defecto = st.slider(
            "Nivel de zoom por defecto:",
            min_value=1,
            max_value=18,
            value=10
        )
    
    # Botón para guardar preferencias
    if st.button("Guardar Preferencias", use_container_width=True):
        try:
            # Preparar datos de preferencias
            preferencias = {
                "theme": tema.lower(),
                "map": {
                    "marker_color": color_marcador,
                    "marker_size": tamaño_marcador,
                    "map_type": tipo_mapa,
                    "zoom_level": zoom_defecto
                }
            }
            
            # Guardar en Firestore
            db = firestore.client()
            preferences_doc = f"preferences_{user_id}"
            db.collection("preferences").document(preferences_doc).set(preferencias)
            
            st.success("Preferencias guardadas exitosamente")
        except Exception as e:
            st.error(f"Error al guardar preferencias: {e}")
    
    # Opciones de privacidad
    st.divider()
    st.subheader("🔒 Privacidad")
    
    # Opciones de visibilidad
    st.write("#### Opciones de Visibilidad")
    
    compartir_ubicacion = st.checkbox(
        "Permitir compartir mi ubicación con monitores",
        value=True
    )
    
    compartir_estadisticas = st.checkbox(
        "Permitir incluir mis viajes en estadísticas globales",
        value=True
    )
    
    # Cambio de contraseña
    st.divider()
    st.subheader("🔑 Cambiar Contraseña")
    
    with st.form("cambiar_contraseña"):
        contraseña_actual = st.text_input(
            "Contraseña actual",
            type="password"
        )
        
        nueva_contraseña = st.text_input(
            "Nueva contraseña",
            type="password"
        )
        
        confirmar_contraseña = st.text_input(
            "Confirmar nueva contraseña",
            type="password"
        )
        
        submitted = st.form_submit_button("Cambiar Contraseña")
        
        if submitted:
            if not contraseña_actual or not nueva_contraseña or not confirmar_contraseña:
                st.error("Todos los campos son obligatorios")
            elif nueva_contraseña != confirmar_contraseña:
                st.error("Las contraseñas no coinciden")
            elif len(nueva_contraseña) < 6:
                st.error("La nueva contraseña debe tener al menos 6 caracteres")
            else:
                st.warning("La funcionalidad de cambio de contraseña no está disponible actualmente a través de la API de administración de Firebase.")
                st.info("Por favor, utiliza la opción de 'Olvidé mi contraseña' en la página de inicio de sesión para restablecer tu contraseña.")
    
    # Información adicional
    st.divider()
    with st.expander("ℹ️ Acerca de Travel Tracker", expanded=False):
        st.markdown("""
        **Travel Tracker** v1.0.0
        
        Aplicación desarrollada con:
        - Streamlit
        - Firebase Authentication
        - Firestore
        - Python
        
        © 2025 Travel Tracker
        """)

# Ejecutar la función principal
if __name__ == "__main__":
    main()

# Mostrar pie de página
show_footer()