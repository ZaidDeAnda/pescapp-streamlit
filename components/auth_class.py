import streamlit as st
import firebase_admin
from firebase_admin import auth, credentials, firestore
from firebase_admin._auth_utils import UserNotFoundError
import time

class Authentication:
    def __init__(self):
        # Initialize Firebase Admin SDK if not already initialized
        try:
            firebase_admin.get_app()
        except ValueError:
            try:
                creds = credentials.Certificate("creds.json")
                firebase_admin.initialize_app(creds)
                print("✅ Firebase inicializado correctamente con credenciales.")
            except Exception as e:
                print(f"❌ Error al inicializar Firebase: {e}")
        
        # Obtain Firestore client
        self.db = firestore.client()
        
        # Add token refresh interval (30 minutes)
        self.token_refresh_interval = 1800

    def login(self):
        """
        Handle user login process
        """
        st.title("🌍 Travel Tracker - Iniciar Sesión")
        
        with st.form("login_form"):
            email = st.text_input("Correo Electrónico")
            password = st.text_input("Contraseña", type="password")
            submit_login = st.form_submit_button("Iniciar Sesión")
            
            if submit_login:
                if not email or not password:
                    st.error("Por favor, complete todos los campos")
                    return
                
                try:
                    # Verify user exists and get custom token
                    user = auth.get_user_by_email(email)
                    custom_token = auth.create_custom_token(user.uid)
                    
                    # Retrieve user data from Firestore
                    user_ref = self.db.collection('users').document(user.uid).get()
                    
                    if not user_ref.exists:
                        # Create user document if it doesn't exist
                        self.db.collection('users').document(user.uid).set({
                            'email': email,
                            'role': 'user',
                            'name': user.display_name or email.split('@')[0],
                            'createdAt': firestore.SERVER_TIMESTAMP
                        })
                        user_data = {
                            'email': email,
                            'role': 'user',
                            'name': user.display_name or email.split('@')[0],
                            'id': user.uid
                        }
                    else:
                        user_data = user_ref.to_dict()
                        user_data['id'] = user.uid
                    
                    # Store tokens and user data in session state
                    st.session_state['authenticated'] = True
                    st.session_state['user'] = user_data
                    st.session_state['auth_token'] = custom_token.decode('utf-8')
                    st.session_state['token_timestamp'] = int(time.time())
                    
                    st.success("Inicio de sesión exitoso")
                    st.rerun()
                
                except UserNotFoundError:
                    st.error("Usuario no encontrado. Por favor, verifique sus credenciales.")
                except Exception as e:
                    st.error(f"Error de inicio de sesión: {e}")
        
        # Recuperación de contraseña
        with st.expander("¿Olvidó su contraseña?"):
            reset_email = st.text_input("Correo Electrónico", key="reset_email")
            reset_button = st.button("Enviar correo de recuperación")
            
            if reset_button and reset_email:
                try:
                    # Firebase Admin SDK doesn't support password reset
                    # We need to use Firebase Auth REST API
                    st.warning("La funcionalidad de recuperación de contraseña no está disponible actualmente.")
                    st.info("Por favor, contacte al administrador para restablecer su contraseña.")
                except Exception as e:
                    st.error(f"Error al enviar correo de recuperación: {e}")
        
        # Opción para registrarse
        st.markdown("---")
        st.write("¿No tienes cuenta?")
        register_button = st.button("Registrarse", key="register_button")
        
        if register_button:
            st.session_state['show_register'] = True
            st.rerun()

    def register(self):
        """
        Handle user registration process
        """
        st.title("🌍 Travel Tracker - Registro")
        
        with st.form("registration_form"):
            name = st.text_input("Nombre completo")
            email = st.text_input("Correo Electrónico")
            password = st.text_input("Contraseña", type="password")
            confirm_password = st.text_input("Confirmar Contraseña", type="password")
            submit_register = st.form_submit_button("Registrarse")
            
            if submit_register:
                # Validate inputs
                if not name or not email or not password:
                    st.error("Por favor, complete todos los campos")
                    return
                
                if password != confirm_password:
                    st.error("Las contraseñas no coinciden")
                    return
                
                if len(password) < 6:
                    st.error("La contraseña debe tener al menos 6 caracteres")
                    return
                
                try:
                    # Create user in Firebase Authentication
                    user = auth.create_user(
                        email=email,
                        password=password,
                        display_name=name
                    )
                    
                    # Store user info in Firestore with default 'user' role
                    self.db.collection('users').document(user.uid).set({
                        'email': email,
                        'name': name,
                        'role': 'user',
                        'createdAt': firestore.SERVER_TIMESTAMP
                    })
                    
                    st.success("Registro exitoso. Por favor, inicie sesión.")
                    st.session_state['show_register'] = False
                    st.rerun()
                
                except Exception as e:
                    if "EMAIL_EXISTS" in str(e):
                        st.error("Este correo electrónico ya está registrado")
                    else:
                        st.error(f"Error de registro: {e}")
        
        # Volver al login
        if st.button("Volver al inicio de sesión"):
            st.session_state['show_register'] = False
            st.rerun()

    def verify_token(self):
        """
        Verify and refresh authentication token if needed
        """
        try:
            if 'auth_token' not in st.session_state:
                return False
            
            current_time = int(time.time())
            token_age = current_time - st.session_state.get('token_timestamp', 0)
            
            # Check if token needs refresh
            if token_age > self.token_refresh_interval:
                if 'user' in st.session_state and 'id' in st.session_state['user']:
                    # Generate new token
                    new_token = auth.create_custom_token(st.session_state['user']['id'])
                    st.session_state['auth_token'] = new_token.decode('utf-8')
                    st.session_state['token_timestamp'] = current_time
                else:
                    return False
            
            return True
        except Exception:
            return False

    def logout(self):
        """
        Handle user logout
        """
        # Clear all authentication state
        if "authenticated" in st.session_state:
            del st.session_state["authenticated"]
        if "user" in st.session_state:
            del st.session_state["user"]
        if "auth_token" in st.session_state:
            del st.session_state["auth_token"]
        if "token_timestamp" in st.session_state:
            del st.session_state["token_timestamp"]
        
        # Redirect to login page
        st.rerun()

    def authenticate(self):
        """
        Main authentication flow
        Returns True if user is authenticated, False otherwise
        """
        # First check if user has valid token
        if ('authenticated' in st.session_state and 
            st.session_state['authenticated'] and 
            self.verify_token()):
            return True
            
        # If not authenticated or token invalid, show login/register
        if st.session_state.get('show_register', False):
            self.register()
        else:
            self.login()
        return False

    def get_current_user(self):
        """
        Get current authenticated user data
        """
        if 'authenticated' in st.session_state and st.session_state['authenticated']:
            return st.session_state.get('user', {})
        return None
    
    def require_role(self, required_roles):
        """
        Check if current user has required role
        """
        user = self.get_current_user()
        
        if not user:
            return False
        
        user_role = user.get('role', 'user')
        
        if isinstance(required_roles, str):
            required_roles = [required_roles]
        
        return user_role in required_roles