import streamlit as st
import pandas as pd
from components.auth_class import Authentication
from components.navigation import setup_sidebar, show_header, show_footer
from services.firebase_service import get_collection, get_document, set_document
from components.utils import flash_message
import datetime
import pytz

# Configurar la página
st.set_page_config(
    page_title="Travel Tracker - Perfil de Usuario",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Crear instancia de autenticación
auth = Authentication()

# Verificar autenticación
if not auth.authenticate():
    st.stop()

# Configurar la barra lateral
setup_sidebar()

# Obtener información del usuario
user = auth.get_current_user()

# Mostrar header
show_header(
    "👤 Perfil de Usuario",
    "Completa tu perfil para una mejor experiencia en la aplicación."
)

# Función para cargar perfil de usuario
def load_user_profile(user_id):
    try:
        # Verificar si existe un perfil previo
        profile_doc = get_document("profiles", user_id)
        
        if profile_doc and hasattr(profile_doc, 'exists') and profile_doc.exists:
            return profile_doc.to_dict()
        return None
    except Exception as e:
        st.error(f"Error al cargar perfil: {str(e)}")
        return None

# Función para guardar perfil de usuario
def save_user_profile(user_id, profile_data):
    try:
        # Añadir metadatos
        profile_data["id_user"] = user_id
        profile_data["updated_at"] = datetime.datetime.now(pytz.timezone('America/Denver')).isoformat()
        
        if not profile_data.get("created_at"):
            profile_data["created_at"] = profile_data["updated_at"]
            
        # Guardar en Firestore
        set_document("profiles", user_id, profile_data)
        return True, "Perfil guardado exitosamente"
    except Exception as e:
        return False, f"Error al guardar perfil: {str(e)}"

# Función principal
def main():
    if not user:
        st.error("No se pudo obtener información del usuario")
        return
    
    user_id = user.get("id")
    
    # Cargar perfil existente (si hay)
    existing_profile = load_user_profile(user_id)
    
    st.write("### Datos personales")
    st.write(f"**Nombre:** {user.get('name', 'No especificado')}")
    st.write(f"**Correo:** {user.get('email', 'No especificado')}")
    st.write(f"**Rol:** {user.get('role', 'user').capitalize()}")
    
    st.divider()
    
    # Formulario para perfil de pescador
    st.write("### Información laboral")
    st.write("Complete la siguiente información para mejorar su experiencia con la aplicación.")
    
    with st.form("perfil_form"):
        # Embarcación
        embarcacion = st.text_input(
            "Embarcación en la que trabaja",
            value=existing_profile.get("embarcacion", "") if existing_profile else "",
            help="Nombre o identificador de la embarcación que utiliza habitualmente."
        )
        
        # Potencia del motor
        col1, col2 = st.columns(2)
        with col1:
            potencia_motor = st.number_input(
                "Potencia del motor",
                min_value=0.0,
                value=float(existing_profile.get("potencia_motor", 0)) if existing_profile else 0.0,
                step=0.5,
                help="Potencia del motor de la embarcación en HP (caballos de fuerza)."
            )
        
        with col2:
            unidad_potencia = st.selectbox(
                "Unidad de potencia",
                options=["HP", "kW"],
                index=0 if existing_profile and existing_profile.get("unidad_potencia") != "kW" else 1,
                help="Unidad de medida de la potencia del motor."
            )
        
        # Especies que captura
        especies_captura = st.text_area(
            "Especies que suele capturar",
            value=existing_profile.get("especies_captura", "") if existing_profile else "",
            help="Liste las especies que captura habitualmente, separadas por comas."
        )
        
        st.write("### Contacto de emergencia")
        
        # Contacto de emergencia
        nombre_contacto = st.text_input(
            "Nombre de contacto de emergencia",
            value=existing_profile.get("nombre_contacto", "") if existing_profile else "",
            help="Nombre completo de la persona a contactar en caso de emergencia."
        )
        
        telefono_contacto = st.text_input(
            "Teléfono de contacto de emergencia",
            value=existing_profile.get("telefono_contacto", "") if existing_profile else "",
            help="Número telefónico de la persona a contactar en caso de emergencia."
        )
        
        relacion_contacto = st.text_input(
            "Relación con el contacto de emergencia",
            value=existing_profile.get("relacion_contacto", "") if existing_profile else "",
            help="Por ejemplo: familiar, cónyuge, amigo, etc."
        )
        
        # Tipo de organización
        st.write("### Información organizacional")
        
        tipo_organizacion = st.radio(
            "Tipo de organización",
            options=["Cooperativa", "Permisionario/Armador", "Renta permiso", "Empleado"],
            index=["Cooperativa", "Permisionario/Armador", "Renta permiso", "Empleado"].index(existing_profile.get("tipo_organizacion", "Cooperativa")) if existing_profile and existing_profile.get("tipo_organizacion") in ["Cooperativa", "Permisionario/Armador", "Renta permiso", "Empleado"] else 0,
            help="Seleccione el tipo de organización a la que pertenece."
        )
        
        nombre_organizacion = st.text_input(
            "Nombre de la organización",
            value=existing_profile.get("nombre_organizacion", "") if existing_profile else "",
            help="Nombre de la cooperativa, permisionario o empresa donde trabaja."
        )
        
        # Información adicional opcional
        st.write("### Información adicional (opcional)")
        
        experiencia_anos = st.number_input(
            "Años de experiencia en pesca",
            min_value=0,
            value=int(existing_profile.get("experiencia_anos", 0)) if existing_profile else 0,
            step=1,
            help="Cantidad de años de experiencia en la actividad pesquera."
        )
        
        observaciones = st.text_area(
            "Observaciones",
            value=existing_profile.get("observaciones", "") if existing_profile else "",
            help="Cualquier información adicional que considere relevante."
        )
        
        # Consentimiento de uso de datos
        st.write("### Consentimiento")
        
        consentimiento = st.checkbox(
            "Doy mi consentimiento para el uso de estos datos en la aplicación Travel Tracker",
            value=existing_profile.get("consentimiento", False) if existing_profile else False
        )
        
        # Botón de guardar
        submitted = st.form_submit_button("Guardar Perfil")
        
        if submitted:
            if not consentimiento:
                st.error("Debe dar su consentimiento para guardar el perfil.")
                return
            
            # Preparar datos para guardar
            profile_data = {
                "embarcacion": embarcacion,
                "potencia_motor": potencia_motor,
                "unidad_potencia": unidad_potencia,
                "especies_captura": especies_captura,
                "nombre_contacto": nombre_contacto,
                "telefono_contacto": telefono_contacto,
                "relacion_contacto": relacion_contacto,
                "tipo_organizacion": tipo_organizacion,
                "nombre_organizacion": nombre_organizacion,
                "experiencia_anos": experiencia_anos,
                "observaciones": observaciones,
                "consentimiento": consentimiento
            }
            
            # Mantener fecha de creación si ya existe
            if existing_profile and existing_profile.get("created_at"):
                profile_data["created_at"] = existing_profile.get("created_at")
            
            # Guardar perfil
            success, message = save_user_profile(user_id, profile_data)
            
            if success:
                flash_message(message, "success")
            else:
                flash_message(message, "error")

# Ejecutar la función principal
if __name__ == "__main__":
    main()

# Mostrar pie de página
show_footer()