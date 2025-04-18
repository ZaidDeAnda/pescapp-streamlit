import streamlit as st
import time
from services.auth_service import verify_credentials, get_current_user, logout_user, verify_session_token, reset_password

def login_user(email, password):
    try:
        # Verify credentials and get tokens
        success, user, message = verify_credentials(email, password)
        
        if success and user:
            # Store tokens and user data in session state
            st.session_state["authenticated"] = True
            st.session_state["user"] = user
            st.session_state["auth_token"] = user.get("token")
            st.session_state["token_timestamp"] = int(time.time())
            return True, "Inicio de sesión exitoso"
        else:
            return False, message
    except Exception as e:
        return False, f"Error durante el inicio de sesión: {str(e)}"

def logout_user_component():
    # Clear all authentication state
    if "authenticated" in st.session_state:
        del st.session_state["authenticated"]
    if "user" in st.session_state:
        del st.session_state["user"]
    if "auth_token" in st.session_state:
        del st.session_state["auth_token"]
    if "token_timestamp" in st.session_state:
        del st.session_state["token_timestamp"]
    
    # Call auth service logout
    success, message = logout_user()
    return success

def check_authentication():
    # Verify if user is authenticated in session_state
    if st.session_state.get("authenticated", False):
        # Verify token validity
        current_time = int(time.time())
        token_age = current_time - st.session_state.get("token_timestamp", 0)
        
        # Check if token needs verification (every 30 minutes)
        if token_age > 1800:  # 30 minutes
            if verify_session_token():
                # Update token timestamp
                st.session_state["token_timestamp"] = current_time
                return True
            else:
                # Clear session if token verification fails
                logout_user_component()
                return False
        return True
    return False

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