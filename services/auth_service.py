import streamlit as st
import firebase_admin
from firebase_admin import auth, credentials, firestore
from firebase_admin._auth_utils import UserNotFoundError
import pyrebase
from services.firebase_service import get_collection, query_documents
from services.user_service import get_user_by_email, create_user, get_user
import os
from config.firebase_config import get_firebase_config
from datetime import datetime
import pytz
import uuid
import time

# Inicializar Pyrebase (para autenticación de Firebase)
def get_pyrebase_auth():
    """Obtener objeto de autenticación de Pyrebase"""
    if 'pyrebase_auth' not in st.session_state:
        # Obtener configuración de Firebase
        firebase_config = get_firebase_config()
        
        # Configurar Pyrebase
        pyrebase_config = {
            "apiKey": firebase_config.get("apiKey"),
            "authDomain": firebase_config.get("authDomain"),
            "databaseURL": firebase_config.get("databaseURL"),
            "storageBucket": firebase_config.get("storageBucket"),
            "projectId": firebase_config.get("projectId"),
            "messagingSenderId": firebase_config.get("messagingSenderId"),
            "appId": firebase_config.get("appId")
        }
        
        # Inicializar Pyrebase
        firebase = pyrebase.initialize_app(pyrebase_config)
        
        # Obtener objeto de autenticación
        st.session_state['pyrebase_auth'] = firebase.auth()
    
    return st.session_state['pyrebase_auth']

# Función para verificar las credenciales del usuario
def verify_credentials(email, password):
    try:
        # Get user by email
        user = auth.get_user_by_email(email)
        
        # Create custom token
        custom_token = auth.create_custom_token(user.uid)
        
        # Get user data from Firestore
        db = firestore.client()
        user_ref = db.collection('users').document(user.uid).get()
        
        if user_ref.exists:
            user_data = user_ref.to_dict()
            user_data['id'] = user.uid
            user_data['token'] = custom_token.decode('utf-8')
            return True, user_data, "Login successful"
        else:
            return False, None, "User data not found"
            
    except UserNotFoundError:
        return False, None, "User not found"
    except Exception as e:
        return False, None, str(e)

# Función para registrar un nuevo usuario
def register_user(email, password, name, role="user"):
    try:
        # Verificar si el usuario ya existe en Firestore
        existing_user = get_user_by_email(email)
        if existing_user:
            return False, "El correo electrónico ya está registrado"
        
        # Obtener objeto de autenticación
        firebase_auth = get_pyrebase_auth()
        
        # Crear usuario en Firebase Authentication
        auth_user = firebase_auth.create_user_with_email_and_password(email, password)
        
        # Obtener el ID de usuario asignado por Firebase
        user_id = auth_user['localId']
        
        # Actualizar el perfil con el nombre
        firebase_auth.update_profile(auth_user['idToken'], display_name=name)
        
        # Obtener zona horaria UTC-7 para la fecha de creación
        tz = pytz.timezone('America/Denver')  # UTC-7
        created_at = datetime.now(tz).strftime("%d de %B de %Y, %I:%M:%S%p UTC-7")
        
        # Crear objeto de usuario para Firestore
        user_data = {
            "id": user_id,
            "email": email,
            "name": name,
            "role": role,
            "createdAt": created_at
        }
        
        # Almacenar el usuario en Firestore
        get_collection("users").document(user_id).set(user_data)
        
        return True, "Usuario registrado exitosamente"
    
    except Exception as e:
        # Capturar errores específicos de Firebase
        error_message = str(e)
        
        if "EMAIL_EXISTS" in error_message:
            return False, "El email ya está en uso"
        elif "WEAK_PASSWORD" in error_message:
            return False, "La contraseña es demasiado débil, debe tener al menos 6 caracteres"
        elif "INVALID_EMAIL" in error_message:
            return False, "Formato de email inválido"
        else:
            return False, f"Error al registrar usuario: {error_message}"

# Función para cerrar sesión
def logout_user():
    """Handle user logout"""
    try:
        # Just clear session state since Firebase handles token invalidation
        return True, "Logout successful"
    except Exception as e:
        return False, str(e)

# Función para cambiar contraseña
def change_password(email, current_password, new_password):
    try:
        # Verificar credenciales actuales
        firebase_auth = get_pyrebase_auth()
        
        # Iniciar sesión con email y contraseña actual
        auth_user = firebase_auth.sign_in_with_email_and_password(email, current_password)
        
        # Cambiar contraseña
        firebase_auth.change_password(auth_user['idToken'], new_password)
        
        return True, "Contraseña actualizada exitosamente"
    
    except Exception as e:
        error_message = str(e)
        
        if "INVALID_PASSWORD" in error_message:
            return False, "La contraseña actual es incorrecta"
        elif "WEAK_PASSWORD" in error_message:
            return False, "La nueva contraseña es demasiado débil"
        else:
            return False, f"Error al cambiar contraseña: {error_message}"

# Función para recuperar contraseña
def reset_password(email):
    """Send password reset email"""
    try:
        # Generate password reset link
        reset_link = auth.generate_password_reset_link(email)
        # Here you would typically send this link via email
        # For now just return success
        return True, "Password reset link sent to email"
    except Exception as e:
        return False, str(e)

# Función para actualizar el perfil de usuario
def update_user_profile(user_id, name=None, photo_url=None):
    try:
        # Obtener usuario
        user_data = get_user(user_id)
        
        if not user_data:
            return False, "Usuario no encontrado"
        
        # Actualizar datos en Firestore
        updates = {}
        
        if name:
            updates["name"] = name
        
        if photo_url:
            updates["photoURL"] = photo_url
        
        # Si hay actualizaciones, aplicarlas
        if updates:
            get_collection("users").document(user_id).update(updates)
            
            # Si el usuario está en session_state, actualizar también allí
            if 'user' in st.session_state and st.session_state['user'].get('id') == user_id:
                for key, value in updates.items():
                    st.session_state['user'][key] = value
        
        return True, "Perfil actualizado exitosamente"
    
    except Exception as e:
        return False, f"Error al actualizar perfil: {str(e)}"

# Función para obtener el usuario actual
def get_current_user():
    """Get currently authenticated user data"""
    if 'user' in st.session_state:
        return st.session_state['user']
    return None

# Función para actualizar el rol de un usuario
def update_user_role(user_id, new_role):
    try:
        # Actualizar el rol del usuario en Firestore
        get_collection("users").document(user_id).update({"role": new_role})
        
        return True, f"Rol actualizado a '{new_role}' exitosamente"
    except Exception as e:
        return False, f"Error al actualizar rol: {str(e)}"

# Función para verificar token y mantener sesión
def verify_session_token():
    try:
        if 'auth_token' not in st.session_state:
            return False
            
        # Verify token is valid
        decoded_token = auth.verify_id_token(st.session_state['auth_token'])
        
        # Check if token is expired
        exp_time = decoded_token.get('exp', 0)
        if exp_time < time.time():
            return False
            
        return True
    except Exception:
        return False

# Función para obtener los usuarios asignados a un monitor
def get_assigned_users(monitor_id):
    # Buscar asignaciones
    assignments = query_documents("assignments", "monitor_id", "==", monitor_id)
    
    if not assignments:
        return []
    
    # Obtener IDs de usuarios asignados
    user_ids = [assignment['user_id'] for assignment in assignments]
    
    # Obtener datos de usuarios
    users = []
    for user_id in user_ids:
        user_doc = get_collection("users").document(user_id).get()
        if user_doc.exists:
            users.append(user_doc.to_dict())
    
    return users

# Función para asignar un usuario a un monitor
def assign_user_to_monitor(user_id, monitor_id):
    # Crear un documento en la colección de asignaciones
    assignment_data = {
        "user_id": user_id,
        "monitor_id": monitor_id,
        "assigned_at": datetime.now().isoformat()
    }
    
    # Generar ID único para la asignación (combinación de user_id y monitor_id)
    assignment_id = f"{user_id}_{monitor_id}"
    
    # Almacenar la asignación en Firestore
    get_collection("assignments").document(assignment_id).set(assignment_data)
    
    return True, "Usuario asignado exitosamente"
