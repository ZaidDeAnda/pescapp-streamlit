from services.firebase_service import get_collection, query_documents, get_document
import streamlit as st
from datetime import datetime

# Función para normalizar timestamps para comparaciones
def normalize_timestamp(timestamp_value):
    """
    Convierte diferentes formatos de timestamp a un formato comparable
    - DatetimeWithNanoseconds se convierte a string ISO
    - Strings se mantienen como están
    - Si no hay timestamp, devuelve una cadena vacía para facilitar ordenamiento
    """
    if timestamp_value is None:
        return ""
    
    # Si es objeto de Firebase DatetimeWithNanoseconds
    if hasattr(timestamp_value, 'seconds'):
        # Convertir a datetime de Python
        dt = datetime.fromtimestamp(timestamp_value.seconds)
        return dt.isoformat()
    
    # Para objetos de Firestore
    if hasattr(timestamp_value, 'timestamp_value'):
        return timestamp_value.timestamp_value.isoformat()
    
    # Para el resto de casos, devolver el valor como string
    return str(timestamp_value)

# Función para obtener todos los viajes de un usuario
def get_user_travels(user_id):
    # Buscar los viajes por user_id
    travels = query_documents("travels", "user_id", "==", user_id)
    
    # Ordenar por timestamp (más reciente primero)
    travels.sort(key=lambda x: normalize_timestamp(x.get("timestamp", "")), reverse=True)
    
    return travels

# Función para obtener un viaje específico
def get_travel(travel_id):
    travel_doc = get_document("travels", travel_id)
    if travel_doc and hasattr(travel_doc, 'exists') and travel_doc.exists:
        return travel_doc.to_dict()
    return None

# Función para obtener todos los viajes disponibles según el rol del usuario
def get_available_travels():
    # Obtener usuario de session_state
    if 'user' not in st.session_state:
        return []
    
    user = st.session_state['user']
    
    if not user:
        return []
    
    role = user.get("role", "user")
    user_id = user.get("id")
    
    # Si es admin, obtener todos los viajes
    if role == "admin":
        # Obtener todos los documentos de la colección "travels"
        all_travels = []
        travels_ref = get_collection("travels")
        if travels_ref:
            travels = travels_ref.stream()
            for doc in travels:
                travel_data = doc.to_dict()
                # Añadir el ID del documento si no está presente
                if "id" not in travel_data:
                    travel_data["id"] = doc.id
                all_travels.append(travel_data)
        
        # Ordenar por timestamp (más reciente primero)
        all_travels.sort(key=lambda x: normalize_timestamp(x.get("timestamp", "")), reverse=True)
        return all_travels
    
    # Si es monitor, obtener sus viajes y los de los usuarios asignados
    elif role == "monitor":
        # Obtener los usuarios asignados a este monitor
        assigned_users = get_assigned_users(user_id)
        assigned_user_ids = [u.get("id") for u in assigned_users]
        
        # Añadir el ID del monitor a la lista
        user_ids = [user_id] + assigned_user_ids
        
        # Obtener los viajes de todos estos usuarios
        all_travels = []
        for uid in user_ids:
            travels = get_user_travels(uid)
            all_travels.extend(travels)
        
        # Ordenar por timestamp (más reciente primero)
        all_travels.sort(key=lambda x: normalize_timestamp(x.get("timestamp", "")), reverse=True)
        return all_travels
    
    # Si es usuario normal, solo obtener sus viajes
    else:
        return get_user_travels(user_id)

# Función para obtener las coordenadas de un viaje
def get_travel_coordinates(travel_id):
    """
    Obtiene las coordenadas geográficas de un viaje específico desde la colección coords.
    
    Args:
        travel_id (str): ID del viaje
        
    Returns:
        list: Lista de diccionarios con coordenadas o lista vacía si no hay coordenadas
    """
    # Verificar que el travel_id no sea None o vacío
    if not travel_id:
        print(f"ID de viaje inválido: {travel_id}")
        return []
    
    # Consultar la colección coords para obtener todas las coordenadas asociadas a este viaje
    coord_docs = query_documents("coords", "travel_id", "==", travel_id)
    
    # Si no hay documentos de coordenadas, devolver lista vacía
    if not coord_docs:
        print(f"No se encontraron coordenadas para el viaje con ID: {travel_id}")
        return []
    
    # Procesar cada documento de coordenadas
    coordinates = []
    for coord in coord_docs:
        # Verificar que tenemos lat y lon válidos
        lat = coord.get("lat")
        lon = coord.get("lon")
        
        if lat is not None and lon is not None:
            # Crear diccionario con la información de la coordenada
            coord_data = {
                "lat": lat,
                "lon": lon,
                "timestamp": normalize_timestamp(coord.get("timestamp")),
                "travel_id": travel_id
            }
            
            # Añadir campos adicionales si existen
            for field in ["accuracy", "altitude", "speed", "user_id", "user_email"]:
                if field in coord:
                    coord_data[field] = coord.get(field)
            
            coordinates.append(coord_data)
    
    # Ordenar por timestamp si es posible
    try:
        coordinates.sort(key=lambda x: x.get("timestamp", ""))
    except Exception as e:
        print(f"Error al ordenar coordenadas: {e}")
    
    return coordinates

# Función actualizada para obtener todos los puntos de coordenadas de todos los viajes disponibles
def get_all_travel_coordinates():
    """
    Obtiene todas las coordenadas de todos los viajes disponibles para el usuario actual.
    
    Returns:
        list: Lista de diccionarios con todas las coordenadas de los viajes disponibles
    """
    # Obtener todos los viajes disponibles según el rol del usuario
    travels = get_available_travels()
    
    if not travels:
        return []
    
    all_coordinates = []
    for travel in travels:
        # Extraer el ID del viaje
        travel_id = travel.get("id") or travel.get("travel_id")
        if not travel_id:
            continue
        
        try:
            # Obtener coordenadas para este viaje
            coordinates = get_travel_coordinates(travel_id)
            
            # Verificar que tenemos coordenadas (nunca debería ser None, pero por si acaso)
            if coordinates is None:
                print(f"get_travel_coordinates devolvió None para el viaje {travel_id}")
                continue
                
            if not coordinates:  # Lista vacía
                continue
                
            # Añadir información del viaje a cada punto
            for coord in coordinates:
                # Asegurarse de que el travel_id esté en la coordenada
                coord["travel_id"] = travel_id
                
                # Si hay información de usuario en el viaje, añadirla
                if "user_id" in travel and "user_id" not in coord:
                    coord["user_id"] = travel["user_id"]
                if "user_email" in travel and "user_email" not in coord:
                    coord["user_email"] = travel["user_email"]
                
                # Añadir información del tipo de viaje si está disponible
                if "type" in travel and "travel_type" not in coord:
                    coord["travel_type"] = travel["type"]
            
            # Añadir las coordenadas al conjunto total
            all_coordinates.extend(coordinates)
            
        except Exception as e:
            print(f"Error al procesar coordenadas del viaje {travel_id}: {str(e)}")
            # Continuar con el siguiente viaje en caso de error
    
    return all_coordinates

# Función para obtener usuarios asignados a un monitor
def get_assigned_users(monitor_id):
    # Consultar asignaciones en Firestore
    assignments = query_documents("assignments", "monitor_id", "==", monitor_id)
    
    # Obtener IDs de usuarios asignados
    user_ids = [assignment.get("user_id") for assignment in assignments]
    
    # Obtener datos de usuarios
    users = []
    for user_id in user_ids:
        user_doc = get_document("users", user_id)
        if user_doc and hasattr(user_doc, 'exists') and user_doc.exists:
            user_data = user_doc.to_dict()
            # Añadir ID si no está presente
            if "id" not in user_data:
                user_data["id"] = user_id
            users.append(user_data)
    
    return users