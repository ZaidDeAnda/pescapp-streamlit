import streamlit as st
import firebase_admin
from firebase_admin import auth, credentials, firestore
from firebase_admin._auth_utils import UserNotFoundError
from utils.database import obtain_firestore_client, manage_user_roles

class Authentication:
    def __init__(self):
        # Initialize Firebase Admin SDK if not already initialized
        try:
            firebase_admin.get_app()
        except ValueError:
            creds = credentials.Certificate("creds.json")
            firebase_admin.initialize_app(creds)
        
        # Obtain Firestore client
        self.db = obtain_firestore_client()

    def login(self):
        """
        Handle user login process
        """
        st.title("Pescapp 🎣 - Iniciar Sesión")
        
        with st.form("login_form"):
            email = st.text_input("Correo Electrónico")
            password = st.text_input("Contraseña", type="password")
            submit_login = st.form_submit_button("Iniciar Sesión")
            
            if submit_login:
                try:
                    # Verify user credentials
                    user = auth.get_user_by_email(email)
                    
                    # Retrieve user role from Firestore
                    user_ref = self.db.collection('users').where('email', '==', email).limit(1)
                    users = list(user_ref.stream())
                    
                    if not users:
                        st.error("Usuario no encontrado en la base de datos.")
                        return
                    
                    user_doc = users[0].to_dict()
                    user_role = user_doc.get('role', 'user')
                    
                    # Set session state
                    st.session_state['authenticated'] = True
                    st.session_state['user_email'] = email
                    st.session_state['user_role'] = user_role
                    st.session_state['show_user_management'] = False
                    
                    # Redirect based on role
                    st.rerun()
                
                except UserNotFoundError as e:
                    st.error(f"Error de autenticación: {e}")
                except Exception as e:
                    st.error(f"Un error inesperado ocurrió: {e}")
        
        # Option to register
        st.markdown("---")
        st.write("¿No tienes cuenta?")
        if st.button("Registrarse", key="register_button"):
            self.register()

    def register(self):
        """
        Handle user registration process
        """
        st.title("Pescapp 🎣 - Registro")
        
        with st.form("registration_form"):
            email = st.text_input("Correo Electrónico")
            password = st.text_input("Contraseña", type="password")
            confirm_password = st.text_input("Confirmar Contraseña", type="password")
            submit_register = st.form_submit_button("Registrarse")
            
            if submit_register:
                # Validate inputs
                if not email or not password:
                    st.error("Por favor, complete todos los campos")
                    return
                
                if password != confirm_password:
                    st.error("Las contraseñas no coinciden")
                    return
                
                try:
                    # Create user in Firebase Authentication
                    user = auth.create_user(
                        email=email,
                        password=password
                    )
                    
                    # Store user info in Firestore with default 'user' role
                    self.db.collection('users').document(user.uid).set({
                        'email': email,
                        'role': 'user',
                        'registered_at': firestore.SERVER_TIMESTAMP
                    })
                    
                    st.success("Registro exitoso. Por favor, inicie sesión.")
                    # Switch back to login
                    self.login()
                
                except UserNotFoundError as e:
                    st.error(f"Error de registro: {e}")
                except Exception as e:
                    st.error(f"Un error inesperado ocurrió: {e}")

    def logout(self):
        """
        Handle user logout
        """
        # Clear all session state variables
        keys_to_remove = ['authenticated', 'user_email', 'user_role', 'show_user_management']
        for key in keys_to_remove:
            if key in st.session_state:
                del st.session_state[key]
        
        # Redirect to login page
        st.rerun()

    def authenticate(self):
        """
        Main authentication flow
        """
        # Check if user is already authenticated
        if 'authenticated' not in st.session_state or not st.session_state['authenticated']:
            # Hide sidebar during login
            no_sidebar_style = """
            <style>
                [data-testid="stSidebar"] {display: none;}
            </style>
            """
            st.markdown(no_sidebar_style, unsafe_allow_html=True)
            
            self.login()
            return False
        
        return True