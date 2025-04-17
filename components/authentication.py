import streamlit as st
from services.auth_service import verify_credentials, get_current_user, logout_user, verify_session_token, reset_password

# Función para iniciar sesión
def login_user(email, password):
    try:
        # Verificar credenciales
        success, user, message = verify_credentials(email, password)
        
        if success and user:
            # Guardar información del usuario en session_state
            st.session_state["authenticated"] = True
            st.session_state["user"] = user
            return True, "Inicio de sesión exitoso"
        else:
            return False, message
    except Exception as e:
        return False, f"Error durante el inicio de sesión: {str(e)}"

# Función para cerrar sesión
def logout_user_component():
    # Usar la función de logout de auth_service
    success, message = logout_user()
    
    return success

# Función para verificar si el usuario está autenticado
def check_authentication():
    # Verificar si el usuario está autenticado en session_state
    if st.session_state.get("authenticated", False):
        # Verificar validez del token si está disponible
        if verify_session_token():
            return True
        else:
            # Si el token no es válido, limpiar datos de sesión
            if "authenticated" in st.session_state:
                del st.session_state["authenticated"]
            if "user" in st.session_state:
                del st.session_state["user"]
    
    return False

# Función para requerir autenticación
def require_authentication():
    # Si el usuario no está autenticado, redirigir a la página de inicio
    if not check_authentication():
        st.warning("Debe iniciar sesión para acceder a esta página.")
        st.markdown(
            """
            <meta http-equiv="refresh" content="3;url=/">
            """,
            unsafe_allow_html=True
        )
        st.stop()
    
    return get_current_user()

# Función para requerir rol específico
def require_role(required_roles):
    # Primero verificar autenticación
    user = require_authentication()
    
    # Obtener rol del usuario
    user_role = user.get("role", "user")
    
    # Verificar si el rol del usuario está en los roles requeridos
    if isinstance(required_roles, str):
        required_roles = [required_roles]
    
    if user_role not in required_roles:
        st.error(f"No tiene permisos para acceder a esta página. Se requiere rol: {', '.join(required_roles)}")
        st.markdown(
            """
            <meta http-equiv="refresh" content="3;url=/">
            """,
            unsafe_allow_html=True
        )
        st.stop()
    
    return user

# Componente para mostrar información del usuario actual
def user_info_component():
    if check_authentication():
        user = get_current_user()
        
        with st.sidebar:
            st.write(f"**Usuario:** {user.get('name', 'Usuario')}")
            st.write(f"**Email:** {user.get('email', '')}")
            st.write(f"**Rol:** {user.get('role', 'user').capitalize()}")
            
            if st.button("Cerrar Sesión"):
                if logout_user_component():
                    st.rerun()

# Componente para recuperar contraseña
def password_reset_component():
    with st.expander("¿Olvidó su contraseña?"):
        email = st.text_input("Correo electrónico", key="reset_email")
        
        if st.button("Enviar correo de recuperación", key="reset_button"):
            if email:
                success, message = reset_password(email)
                if success:
                    st.success(message)
                else:
                    st.error(message)
            else:
                st.warning("Ingrese su correo electrónico")