from services.firebase_service import get_collection, query_documents, get_document
from models.user import User, UserAssignment
import streamlit as st
from datetime import datetime
import pytz
import uuid

# Función para obtener un usuario por ID
def get_user(user_id):
    user_doc = get_document("users", user_id)
    if user_doc.exists:
        return User.from_dict(user_doc.to_dict())
    return None

# Función para obtener un usuario por email
def get_user_by_email(email):
    users = query_documents("users", "email", "==", email)
    if users:
        return User.from_dict(users[0])
    return None

# Función para obtener todos los usuarios
def get_all_users():
    users_docs = get_collection("users").stream()
    return [User.from_dict(doc.to_dict()) for doc in users_docs]

# Función para obtener usuarios por rol
def get_users_by_role(role):
    users = query_documents("users", "role", "==", role)
    return [User.from_dict(user) for user in users]

# Función para crear un nuevo usuario
def create_user(email, name, role="user"):
    # Verificar si el usuario ya existe
    existing_user = get_user_by_email(email)
    if existing_user:
        return False, "El correo electrónico ya está registrado"
    
    # Generar un ID único para el usuario
    user_id = str(uuid.uuid4())
    
    # Obtener zona horaria UTC-7 para la fecha de creación
    tz = pytz.timezone('America/Denver')  # UTC-7
    created_at = datetime.now(tz).strftime("%d de %B de %Y, %I:%M:%S%p UTC-7")
    
    # Crear objeto de usuario
    user = User(
        id=user_id,
        email=email,
        name=name,
        role=role,
        createdAt=created_at
    )
    
    # Almacenar el usuario en Firestore
    get_collection("users").document(user_id).set(user.to_dict())
    
    return True, user_id

# Función para actualizar un usuario
def update_user(user_id, data):
    # Obtener el usuario actual
    user = get_user(user_id)
    if not user:
        return False, "Usuario no encontrado"
    
    # Actualizar campos
    if "name" in data:
        user.name = data["name"]
    if "role" in data:
        user.role = data["role"]
    
    # Actualizar en Firestore
    get_collection("users").document(user_id).update(data)
    
    return True, "Usuario actualizado correctamente"

# Función para eliminar un usuario
def delete_user(user_id):
    # Verificar si el usuario existe
    user = get_user(user_id)
    if not user:
        return False, "Usuario no encontrado"
    
    # Eliminar de Firestore
    get_collection("users").document(user_id).delete()
    
    return True, "Usuario eliminado correctamente"

# Función para asignar un usuario a un monitor
def assign_user_to_monitor(user_id, monitor_id, assigned_by=None):
    # Verificar si el usuario existe
    user = get_user(user_id)
    if not user:
        return False, "Usuario no encontrado"
    
    # Verificar si el monitor existe y tiene rol de monitor
    monitor = get_user(monitor_id)
    if not monitor:
        return False, "Monitor no encontrado"
    
    if monitor.role != "monitor":
        return False, "El usuario asignado debe tener rol de monitor"
    
    # Crear la asignación
    assignment_id = f"{user_id}_{monitor_id}"
    
    # Obtener fecha actual
    tz = pytz.timezone('America/Denver')  # UTC-7
    assigned_at = datetime.now(tz).isoformat()
    
    # Crear objeto de asignación
    assignment = UserAssignment(
        user_id=user_id,
        monitor_id=monitor_id,
        assigned_at=assigned_at,
        assigned_by=assigned_by
    )
    
    # Almacenar en Firestore
    get_collection("assignments").document(assignment_id).set(assignment.to_dict())
    
    return True, "Usuario asignado correctamente al monitor"

# Función para obtener las asignaciones de un monitor
def get_monitor_assignments(monitor_id):
    assignments = query_documents("assignments", "monitor_id", "==", monitor_id)
    return [UserAssignment.from_dict(assignment) for assignment in assignments]

# Función para obtener los usuarios asignados a un monitor
def get_assigned_users(monitor_id):
    # Obtener asignaciones
    assignments = get_monitor_assignments(monitor_id)
    
    # Obtener IDs de usuarios asignados
    user_ids = [assignment.user_id for assignment in assignments]
    
    # Obtener datos de los usuarios
    users = []
    for user_id in user_ids:
        user = get_user(user_id)
        if user:
            users.append(user)
    
    return users

# Función para verificar si un usuario está asignado a un monitor
def is_user_assigned_to_monitor(user_id, monitor_id):
    assignment_id = f"{user_id}_{monitor_id}"
    assignment_doc = get_document("assignments", assignment_id)
    return assignment_doc.exists

# Función para eliminar una asignación
def remove_assignment(user_id, monitor_id):
    assignment_id = f"{user_id}_{monitor_id}"
    get_collection("assignments").document(assignment_id).delete()
    return True, "Asignación eliminada correctamente"