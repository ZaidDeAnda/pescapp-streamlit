import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from components.auth_class import Authentication
from components.navigation import setup_sidebar, show_header, show_footer
from services.firebase_service import get_collection, query_documents
from services.travel_service import get_assigned_users

# Configurar la página
st.set_page_config(
    page_title="Travel Tracker - Visualizador de Datos",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Crear instancia de autenticación
auth = Authentication()

# Verificar autenticación
if not auth.authenticate():
    st.stop()

# Configurar la barra lateral
setup_sidebar()

# Mostrar header
show_header(
    "🗺️ Mapa de Coordenadas",
    "Visualización geográfica de coordenadas con filtros relacionales."
)

# Función para cargar datos de coordenadas
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
        #st.info(f"Obteniendo hasta {limit} registros de coordenadas...")
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

# Función para cargar datos de viajes
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
        #st.info(f"Obteniendo hasta {limit} registros de viajes...")
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

# Función para cargar datos de usuarios
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
        #st.info(f"Obteniendo hasta {limit} registros de usuarios...")
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

# Función principal
def main():
    # Obtener información del usuario actual
    current_user = auth.get_current_user()
    user_role = current_user.get('role', 'user')
    user_id = current_user.get('id', '')
    user_email = current_user.get('email', '')
    
    # Mostrar información del rol y permisos
    role_messages = {
        'admin': "Como administrador, puedes ver las coordenadas de todos los usuarios.",
        'monitor': "Como monitor, puedes ver las coordenadas de los usuarios asignados a ti.",
        'user': "Puedes ver las coordenadas de tus propios viajes."
    }
    
    #st.info(role_messages.get(user_role, "Rol de usuario no reconocido."))
    
    # Inicializar variable para almacenamiento de datos en session state
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
        st.session_state.users_df = None
        st.session_state.travels_df = None
        st.session_state.coords_df = None
    
    # Cargar los datos cuando se haga clic en el botón
    if st.button("Cargar Datos", use_container_width=True):
        with st.spinner("Cargando datos..."):
            # Obtener usuarios disponibles según el rol
            if user_role == 'admin':
                # Administrador: todos los usuarios
                users_df = load_users(limit=2000)
            elif user_role == 'monitor':
                # Monitor: usuarios asignados
                assigned_users = get_assigned_users(user_id)
                
                # Crear una lista de IDs de usuarios asignados
                assigned_user_ids = []
                for user in assigned_users:
                    if isinstance(user, dict) and 'id' in user:
                        assigned_user_ids.append(user['id'])
                    elif hasattr(user, 'id'):
                        assigned_user_ids.append(user.id)
                
                # Incluir también al propio monitor
                assigned_user_ids.append(user_id)
                
                # Cargar todos los usuarios pero filtrar los asignados
                all_users_df = load_users(limit=2000)
                if all_users_df is not None:
                    users_df = all_users_df[all_users_df['user_id'].isin(assigned_user_ids)]
                else:
                    users_df = None
            else:
                # Usuario normal: solo él mismo
                all_users_df = load_users(limit=2000)
                if all_users_df is not None:
                    users_df = all_users_df[all_users_df['user_id'] == user_id]
                else:
                    users_df = None
            
            # Cargar viajes y filtrar según usuarios disponibles
            travels_df = load_travels(limit=2000)
            if travels_df is not None and users_df is not None:
                # Obtener IDs de usuario disponibles
                available_user_ids = users_df['user_id'].unique().tolist()
                # Filtrar viajes de usuarios disponibles
                travels_df = travels_df[travels_df['user_id'].isin(available_user_ids)]
            
            # Cargar coordenadas y filtrar según viajes disponibles
            coords_df = load_coords(limit=2000)
            if coords_df is not None and travels_df is not None:
                # Obtener IDs de viaje disponibles
                available_travel_ids = travels_df['travel_id'].unique().tolist()
                # Filtrar coordenadas de viajes disponibles
                coords_df = coords_df[coords_df['travel_id'].isin(available_travel_ids)]
            
            # Guardar datos en session state
            st.session_state.users_df = users_df
            st.session_state.travels_df = travels_df
            st.session_state.coords_df = coords_df
            st.session_state.data_loaded = True
    
    # Mostrar las tablas y filtros si los datos están cargados
    if st.session_state.data_loaded:
        users_df = st.session_state.users_df
        travels_df = st.session_state.travels_df
        coords_df = st.session_state.coords_df
        
        # Verificar que todas las tablas tienen datos
        if users_df is None or travels_df is None or coords_df is None:
            st.warning("No se pudieron cargar todos los datos necesarios")
            return
        
        if len(users_df) == 0:
            st.warning("No hay usuarios disponibles según tus permisos.")
            return
            
        # FILTRO GLOBAL: Selección de usuarios (solo mostrar usuarios permitidos)
        st.subheader("🔍 Filtro de Usuarios")
        
        # Asegurar que tenemos la columna de email en usuarios
        if 'email' in users_df.columns:
            # Obtener la lista de emails de usuario
            user_emails = users_df['email'].unique().tolist()
            user_emails.sort()  # Ordenar alfabéticamente
            
            # Para usuario normal, no mostrar selector si solo tiene acceso a sí mismo
            if user_role == 'user' and len(user_emails) == 1:
                st.write(f"**Usuario seleccionado:** {user_emails[0]}")
                selected_user_option = user_emails[0]  # Preseleccionar el único usuario disponible
            else:
                # Añadir opción "Todos los usuarios" solo para admin y monitor
                if user_role in ['admin', 'monitor'] and len(user_emails) > 1:
                    user_options = ["Todos los usuarios"] + user_emails
                    # Selector de usuarios
                    selected_user_option = st.selectbox(
                        "Filtrar por usuario:",
                        options=user_options,
                        index=0
                    )
                else:
                    # Si solo hay un usuario o el rol no lo permite, mostrar selector simple
                    selected_user_option = st.selectbox(
                        "Filtrar por usuario:",
                        options=user_emails,
                        index=0
                    )
            
            # Aplicar filtro de usuarios
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
                
            # Filtro adicional para viajes
            if len(filtered_travels_df) > 0 and 'travel_id' in filtered_travels_df.columns:
                st.subheader("🛣️ Filtro de Viajes")
                
                # Obtener los IDs de viaje después del filtro de usuarios
                travel_ids = filtered_travels_df['travel_id'].unique().tolist()
                
                if travel_ids:
                    # Añadir opción para mostrar todos los viajes
                    travel_options = ["Todos los viajes"] + travel_ids
                    
                    # Multiselect para seleccionar varios viajes
                    selected_travel_ids = st.multiselect(
                        "Seleccionar viajes específicos:",
                        options=travel_options,
                        default=["Todos los viajes"]
                    )
                    
                    # Aplicar filtro de viajes
                    if "Todos los viajes" not in selected_travel_ids and selected_travel_ids:
                        # Filtrar viajes por IDs seleccionados
                        filtered_travels_df = filtered_travels_df[filtered_travels_df['travel_id'].isin(selected_travel_ids)]
                        
                        # Filtrar coordenadas por viajes seleccionados
                        filtered_coords_df = filtered_coords_df[filtered_coords_df['travel_id'].isin(selected_travel_ids)]
            
            # Mostrar resumen del filtrado
            #st.info(f"Mostrando datos de: {len(filtered_users_df)} usuarios, {len(filtered_travels_df)} viajes y {len(filtered_coords_df)} coordenadas.")
        else:
            st.warning("La columna 'email' no está disponible en la tabla de usuarios para filtrar")
            # Usar los datos sin filtrar
            filtered_users_df = users_df
            filtered_travels_df = travels_df
            filtered_coords_df = coords_df
        
        # MAPA DE COORDENADAS (en lugar de tabla)
        if filtered_coords_df is not None:
            st.subheader("🗺️ Mapa de Coordenadas")
            
            # Verificar que tenemos coordenadas válidas para mostrar
            valid_coords = filtered_coords_df.dropna(subset=['lat', 'lon']).copy()
            
            if len(valid_coords) == 0:
                st.warning("No hay coordenadas válidas para mostrar en el mapa.")
            else:
                # Asegurarse de que lat y lon son valores numéricos
                valid_coords['lat'] = pd.to_numeric(valid_coords['lat'], errors='coerce')
                valid_coords['lon'] = pd.to_numeric(valid_coords['lon'], errors='coerce')
                
                # Eliminar filas con valores no numéricos o fuera de rango
                valid_coords = valid_coords[
                    (valid_coords['lat'] >= -90) & 
                    (valid_coords['lat'] <= 90) & 
                    (valid_coords['lon'] >= -180) & 
                    (valid_coords['lon'] <= 180)
                ]
                
                if len(valid_coords) == 0:
                    st.warning("No hay coordenadas válidas para mostrar después de filtrar valores incorrectos.")
                else:
                    # Crear el mapa
                    st.write(f"Mostrando {len(valid_coords)} coordenadas en el mapa.")
                    
                    # Calcular el centro del mapa (promedio de coordenadas)
                    center = [valid_coords['lat'].mean(), valid_coords['lon'].mean()]
                    
                    # Crear mapa base
                    m = folium.Map(location=center, zoom_start=10, control_scale=True)
                    
                    # Añadir controles al mapa
                    folium.LayerControl().add_to(m)
                    
                    # Crear marcadores para cada coordenada
                    for idx, row in valid_coords.iterrows():
                        # Crear texto para el popup
                        popup_text = f"<b>ID de Viaje:</b> {row.get('travel_id', 'N/A')}<br>"
                        
                        if 'user_email' in row and pd.notna(row['user_email']):
                            popup_text += f"<b>Usuario:</b> {row['user_email']}<br>"
                        
                        if 'timestamp' in row and pd.notna(row['timestamp']):
                            popup_text += f"<b>Fecha:</b> {row['timestamp']}<br>"
                        
                        if 'accuracy' in row and pd.notna(row['accuracy']):
                            popup_text += f"<b>Precisión:</b> {row['accuracy']} m<br>"
                        
                        if 'altitude' in row and pd.notna(row['altitude']):
                            popup_text += f"<b>Altitud:</b> {row['altitude']} m<br>"
                        
                        if 'speed' in row and pd.notna(row['speed']):
                            popup_text += f"<b>Velocidad:</b> {row['speed']} km/h<br>"
                        
                        # Crear marcador
                        folium.Marker(
                            location=[row['lat'], row['lon']],
                            popup=folium.Popup(popup_text, max_width=300),
                            tooltip=f"Viaje: {row.get('travel_id', 'N/A')}"
                        ).add_to(m)
                    
                    # Añadir círculos para la precisión si está disponible
                    if 'accuracy' in valid_coords.columns:
                        for idx, row in valid_coords.iterrows():
                            if pd.notna(row['accuracy']) and float(row['accuracy']) > 0:
                                folium.Circle(
                                    location=[row['lat'], row['lon']],
                                    radius=float(row['accuracy']),
                                    color='blue',
                                    fill=True,
                                    fill_opacity=0.1
                                ).add_to(m)
                    
                    # Mostrar el mapa
                    folium_static(m, width=1000, height=600)
            
            # Opción para descargar como CSV
            coords_csv = filtered_coords_df.to_csv(index=False)
            st.download_button(
                label="Descargar Coordenadas como CSV",
                data=coords_csv,
                file_name="coordenadas_filtradas.csv",
                mime="text/csv"
            )
    else:
        st.info("Por favor, haga clic en 'Cargar Datos' para visualizar las coordenadas.")

# Ejecutar la función principal
if __name__ == "__main__":
    main()

# Mostrar pie de página
show_footer()