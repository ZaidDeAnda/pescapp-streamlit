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
    travel = get_travel(travel_id)
    
    if not travel:
        return None
    
    # Verificar si es un viaje de "tracking" o un viaje completo
    if travel.get("type") == "tracking":
        # Si es un viaje de tracking, devolver las coordenadas directas
        lat = travel.get("coords", {}).get("lat")
        lon = travel.get("coords", {}).get("lon")
        
        if lat and lon:
            return [{
                "lat": lat,
                "lon": lon,
                "timestamp": normalize_timestamp(travel.get("timestamp"))
            }]
        return []
    
    # Si es un viaje completo, obtener las coordenadas iniciales y finales
    initial_coords = travel.get("initial_coords", {})
    final_coords = travel.get("final_coords", {})
    
    coordinates = []
    
    # Añadir coordenadas iniciales si existen
    if initial_coords and "lat" in initial_coords and "lon" in initial_coords:
        coordinates.append({
            "lat": initial_coords["lat"],
            "lon": initial_coords["lon"],
            "timestamp": normalize_timestamp(travel.get("timestamp"))
        })
    
    # Añadir coordenadas finales si existen y son diferentes de las iniciales
    if final_coords and "lat" in final_coords and "lon" in final_coords:
        # Verificar si las coordenadas finales son diferentes de las iniciales
        if not coordinates or (
            final_coords["lat"] != coordinates[0]["lat"] or 
            final_coords["lon"] != coordinates[0]["lon"]
        ):
            coordinates.append({
                "lat": final_coords["lat"],
                "lon": final_coords["lon"],
                "timestamp": normalize_timestamp(travel.get("end_timestamp"))
            })
    
    return coordinates

# Función para obtener todos los puntos de coordenadas de todos los viajes disponibles
def get_all_travel_coordinates():
    travels = get_available_travels()
    
    all_coordinates = []
    for travel in travels:
        travel_id = travel.get("id") or travel.get("travel_id")
        if travel_id:
            try:
                coordinates = get_travel_coordinates(travel_id)
                if coordinates:
                    # Añadir información del viaje a cada punto
                    for coord in coordinates:
                        coord["travel_id"] = travel_id
                        # Si hay información de usuario en el viaje, añadirla
                        if "user_id" in travel:
                            coord["user_id"] = travel["user_id"]
                        if "user_email" in travel:
                            coord["user_email"] = travel["user_email"]
                    
                    all_coordinates.extend(coordinates)
            except Exception as e:
                print(f"Error al procesar coordenadas del viaje {travel_id}: {e}")
    
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