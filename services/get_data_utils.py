import streamlit as st
import pandas as pd
from services.firebase_service import get_collection
from services.travel_service import get_assigned_users

def load_coords(limit=2000):
    """
    Carga registros directamente de la colección coords
    
    Args:
        limit: Número máximo de registros a cargar
    
    Returns:
        DataFrame con los registros de coordenadas
    """
    try:
        # Obtener referencia a la colección
        coords_collection = get_collection("coords")
        if not coords_collection:
            st.error("No se pudo acceder a la colección 'coords'")
            return None
        
        # Obtener documentos
        coords_docs = list(coords_collection.limit(limit).stream())
        
        if not coords_docs:
            st.warning("No se encontraron registros en la colección 'coords'")
            return None
        
        # Convertir a lista de diccionarios
        coords_data = []
        
        for doc in coords_docs:
            try:
                # Obtener datos del documento
                doc_data = doc.to_dict()
                
                # Añadir ID del documento como travel_id si no existe
                if "travel_id" not in doc_data:
                    doc_data["travel_id"] = doc.id
                
                # Procesar datos de coordenadas anidadas
                if "coords" in doc_data and isinstance(doc_data["coords"], dict):
                    coords_obj = doc_data["coords"]
                    doc_data["lat"] = coords_obj.get("lat")
                    doc_data["lon"] = coords_obj.get("lon")
                
                # Estandarizar el formato de timestamp
                if "timestamp" in doc_data:
                    try:
                        timestamp = pd.to_datetime(doc_data["timestamp"])
                        doc_data["timestamp"] = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        doc_data["timestamp"] = None
                
                coords_data.append(doc_data)
            except Exception as e:
                print(f"Error procesando documento: {str(e)}")
                continue
        
        # Convertir a DataFrame
        df = pd.DataFrame(coords_data)
        
        # Renombrar columnas para consistencia
        column_mapping = {
            'id': 'travel_id',
            'tid': 'travel_id',
            'userId': 'user_id',
            'userEmail': 'user_email'
        }
        df = df.rename(columns=column_mapping)
        
        # Mostrar información de éxito
        st.success(f"Se cargaron {len(df)} registros de coordenadas")
        
        return df
    
    except Exception as e:
        st.error(f"Error al cargar coordenadas: {str(e)}")
        return None

def load_travels(limit=2000):
    """
    Carga registros directamente de la colección travels
    
    Args:
        limit: Número máximo de registros a cargar
    
    Returns:
        DataFrame con los registros de viajes
    """
    try:
        # Obtener referencia a la colección
        travels_collection = get_collection("travels")
        if not travels_collection:
            st.error("No se pudo acceder a la colección 'travels'")
            return None
        
        # Obtener documentos
        travels_docs = list(travels_collection.limit(limit).stream())
        
        if not travels_docs:
            st.warning("No se encontraron registros en la colección 'travels'")
            return None
        
        # Convertir a lista de diccionarios
        travels_data = []
        
        for doc in travels_docs:
            try:
                # Obtener datos del documento
                doc_data = doc.to_dict()
                
                # Añadir ID del documento como travel_id si no existe
                if "travel_id" not in doc_data and "id" not in doc_data:
                    doc_data["travel_id"] = doc.id
                elif "id" in doc_data and "travel_id" not in doc_data:
                    doc_data["travel_id"] = doc_data["id"]
                
                # Estandarizar el formato de timestamp
                for timestamp_field in ["timestamp", "end_timestamp", "created_at"]:
                    if timestamp_field in doc_data:
                        try:
                            timestamp = pd.to_datetime(doc_data[timestamp_field])
                            doc_data[timestamp_field] = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                        except:
                            doc_data[timestamp_field] = None
                
                # Procesar coordenadas si existen
                for coord_field in ["coords", "initial_coords", "final_coords"]:
                    if coord_field in doc_data and isinstance(doc_data[coord_field], dict):
                        coords = doc_data[coord_field]
                        doc_data[f"{coord_field}_lat"] = coords.get("lat")
                        doc_data[f"{coord_field}_lon"] = coords.get("lon")
                
                travels_data.append(doc_data)
            except Exception as e:
                print(f"Error procesando documento: {str(e)}")
                continue
        
        # Convertir a DataFrame
        df = pd.DataFrame(travels_data)
        
        # Renombrar columnas para consistencia
        column_mapping = {
            'id': 'travel_id',
            'userId': 'user_id',
            'userEmail': 'user_email'
        }
        df = df.rename(columns=column_mapping)
        
        # Mostrar información de éxito
        st.success(f"Se cargaron {len(df)} registros de viajes")
        
        return df
    
    except Exception as e:
        st.error(f"Error al cargar viajes: {str(e)}")
        return None

def load_users(limit=2000):
    """
    Carga registros directamente de la colección users
    
    Args:
        limit: Número máximo de registros a cargar
    
    Returns:
        DataFrame con los registros de usuarios
    """
    try:
        # Obtener referencia a la colección
        users_collection = get_collection("users")
        if not users_collection:
            st.error("No se pudo acceder a la colección 'users'")
            return None
        
        # Obtener documentos
        users_docs = list(users_collection.limit(limit).stream())
        
        if not users_docs:
            st.warning("No se encontraron registros en la colección 'users'")
            return None
        
        # Convertir a lista de diccionarios
        users_data = []
        
        for doc in users_docs:
            try:
                # Obtener datos del documento
                doc_data = doc.to_dict()
                
                # Añadir ID del documento como user_id si no existe
                if "id" not in doc_data:
                    doc_data["id"] = doc.id
                
                # Estandarizar el formato de timestamp para createdAt y otros campos de fecha
                timestamp_fields = ["createdAt", "lastLogin", "updatedAt"]
                for field in timestamp_fields:
                    if field in doc_data:
                        try:
                            timestamp = pd.to_datetime(doc_data[field])
                            doc_data[field] = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                        except:
                            doc_data[field] = None
                
                users_data.append(doc_data)
            except Exception as e:
                print(f"Error procesando documento: {str(e)}")
                continue
        
        # Convertir a DataFrame
        df = pd.DataFrame(users_data)
        
        # Renombrar columnas para consistencia
        column_mapping = {
            'id': 'user_id',
            'createdAt': 'created_at',
            'lastLogin': 'last_login',
            'updatedAt': 'updated_at',
            'userRole': 'role'
        }
        df = df.rename(columns=column_mapping)
        
        # Mostrar información de éxito
        st.success(f"Se cargaron {len(df)} registros de usuarios")
        
        return df
    
    except Exception as e:
        st.error(f"Error al cargar usuarios: {str(e)}")
        return None

def filter_data_by_user(users_df, travels_df, coords_df, selected_user_option):
    """Filter data based on selected user"""
    filtered_users_df = users_df.copy()
    filtered_travels_df = travels_df.copy()
    filtered_coords_df = coords_df.copy()
    
    if selected_user_option != "Todos los usuarios":
        # Filtrar usuarios por email seleccionado
        filtered_users_df = users_df[users_df['email'] == selected_user_option]
        
        # Obtener los IDs de usuario filtrados
        filtered_user_ids = filtered_users_df['user_id'].unique().tolist()
        
        # Filtrar viajes por IDs de usuario
        filtered_travels_df = travels_df[travels_df['user_id'].isin(filtered_user_ids)]
        
        # Obtener los IDs de viaje filtrados
        filtered_travel_ids = filtered_travels_df['travel_id'].unique().tolist()
        
        # Filtrar coordenadas por IDs de viaje
        filtered_coords_df = coords_df[coords_df['travel_id'].isin(filtered_travel_ids)]
    
    return filtered_users_df, filtered_travels_df, filtered_coords_df

def filter_by_travel_ids(filtered_travels_df, filtered_coords_df, selected_travel_ids):
    """Filter data based on selected travel IDs"""
    if "Todos los viajes" not in selected_travel_ids and selected_travel_ids:
        # Filtrar viajes por IDs seleccionados
        filtered_travels_df = filtered_travels_df[filtered_travels_df['travel_id'].isin(selected_travel_ids)]
        
        # Filtrar coordenadas por viajes seleccionados
        filtered_coords_df = filtered_coords_df[filtered_coords_df['travel_id'].isin(selected_travel_ids)]
    
    return filtered_travels_df, filtered_coords_df