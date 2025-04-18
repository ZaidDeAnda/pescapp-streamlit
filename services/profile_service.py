from services.firebase_service import get_collection, query_documents, get_document
from datetime import datetime
import pytz
import streamlit as st

# Función para obtener un perfil por ID de usuario
def get_profile(user_id):
    """
    Obtiene el perfil de un usuario específico
    
    Args:
        user_id (str): ID del usuario
    
    Returns:
        dict: Datos del perfil o None si no existe
    """
    profile_doc = get_document("profiles", user_id)
    if profile_doc and hasattr(profile_doc, 'exists') and profile_doc.exists:
        return profile_doc.to_dict()
    return None

# Función para crear o actualizar un perfil
def update_profile(user_id, profile_data):
    """
    Actualiza el perfil de un usuario o lo crea si no existe
    
    Args:
        user_id (str): ID del usuario
        profile_data (dict): Datos del perfil a guardar
    
    Returns:
        tuple: (éxito, mensaje)
    """
    try:
        # Añadir metadata
        profile_data["id_user"] = user_id
        profile_data["updated_at"] = datetime.now(pytz.timezone('America/Denver')).isoformat()
        
        # Verificar si existe un perfil previo para mantener la fecha de creación
        existing_profile = get_profile(user_id)
        if existing_profile and "created_at" in existing_profile:
            profile_data["created_at"] = existing_profile["created_at"]
        else:
            profile_data["created_at"] = profile_data["updated_at"]
        
        # Guardar en Firestore
        get_collection("profiles").document(user_id).set(profile_data)
        return True, "Perfil actualizado correctamente"
    except Exception as e:
        return False, f"Error al actualizar perfil: {str(e)}"

# Función para obtener perfiles por tipo de organización
def get_profiles_by_organization_type(organization_type):
    """
    Obtiene todos los perfiles de un tipo de organización específico
    
    Args:
        organization_type (str): Tipo de organización (Cooperativa, Permisionario/Armador, etc.)
    
    Returns:
        list: Lista de perfiles
    """
    return query_documents("profiles", "tipo_organizacion", "==", organization_type)

# Función para obtener perfiles por especie capturada
def get_profiles_by_species(species):
    """
    Obtiene perfiles que mencionan una especie específica
    
    Args:
        species (str): Nombre de la especie a buscar
    
    Returns:
        list: Lista de perfiles
    """
    # Nota: Esta es una implementación simple, para búsquedas más avanzadas
    # sería necesario implementar índices compuestos en Firestore o usar
    # Cloud Functions para consultas más complejas
    
    all_profiles = get_collection("profiles").stream()
    matching_profiles = []
    
    for profile in all_profiles:
        profile_data = profile.to_dict()
        especies = profile_data.get("especies_captura", "").lower()
        
        if species.lower() in especies:
            matching_profiles.append(profile_data)
    
    return matching_profiles

# Función para eliminar un perfil
def delete_profile(user_id):
    """
    Elimina el perfil de un usuario
    
    Args:
        user_id (str): ID del usuario
    
    Returns:
        tuple: (éxito, mensaje)
    """
    try:
        # Verificar si existe el perfil
        profile = get_profile(user_id)
        if not profile:
            return False, "Perfil no encontrado"
        
        # Eliminar de Firestore
        get_collection("profiles").document(user_id).delete()
        return True, "Perfil eliminado correctamente"
    except Exception as e:
        return False, f"Error al eliminar perfil: {str(e)}"

# Función para verificar si un usuario tiene perfil completo
def has_complete_profile(user_id):
    """
    Verifica si un usuario tiene su perfil completo con los campos requeridos
    
    Args:
        user_id (str): ID del usuario
    
    Returns:
        bool: True si el perfil está completo, False en caso contrario
    """
    profile = get_profile(user_id)
    
    if not profile:
        return False
    
    # Campos requeridos
    required_fields = [
        "embarcacion", 
        "potencia_motor",
        "especies_captura", 
        "nombre_contacto", 
        "telefono_contacto",
        "tipo_organizacion"
    ]
    
    # Verificar que todos los campos requeridos tengan valor
    for field in required_fields:
        if field not in profile or not profile[field]:
            return False
    
    return True