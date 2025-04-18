import streamlit as st
import pandas as pd
from components.auth_class import Authentication
from components.navigation import setup_sidebar, show_header, show_footer
from services.firebase_service import get_collection

# Configurar la página
st.set_page_config(
    page_title="Visualizador de Datos",
    page_icon="📍",
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
    "📍 Visualizador de datos",
    "Consulta directa de las colecciones de datos de coordenadas, viajes y usuarios con filtro relacional."
)

# Función para cargar datos de coordenadas
def load_coords(limit=500):
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
        st.info(f"Obteniendo hasta {limit} registros de coordenadas...")
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
def load_travels(limit=500):
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
        st.info(f"Obteniendo hasta {limit} registros de viajes...")
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
def load_users(limit=500):
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
        st.info(f"Obteniendo hasta {limit} registros de usuarios...")
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
    # Control para limitar la cantidad de registros
    limit = st.slider(
        "Número máximo de registros a cargar por colección:",
        min_value=10,
        max_value=2000,
        value=500,
        step=50
    )
    
    # Opciones para mostrar tablas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        show_coords = st.checkbox("Mostrar tabla de coordenadas", value=True)
    
    with col2:
        show_travels = st.checkbox("Mostrar tabla de viajes", value=True)
    
    with col3:
        show_users = st.checkbox("Mostrar tabla de usuarios", value=True)
    
    # Inicializar variable para almacenamiento de datos en session state
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
        st.session_state.users_df = None
        st.session_state.travels_df = None
        st.session_state.coords_df = None
    
    # Cargar los datos cuando se haga clic en el botón
    if st.button("Cargar Datos", use_container_width=True):
        with st.spinner("Cargando datos..."):
            # Cargar todos los datos primero
            users_df = load_users(limit=limit)
            travels_df = load_travels(limit=limit)
            coords_df = load_coords(limit=limit)
            
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
            
        # FILTRO GLOBAL: Selección de usuarios
        st.subheader("🔍 Filtro de Usuarios")
        
        # Asegurar que tenemos la columna de email en usuarios
        if 'email' in users_df.columns:
            # Obtener la lista de emails de usuario
            user_emails = users_df['email'].unique().tolist()
            user_emails.sort()  # Ordenar alfabéticamente
            
            # Añadir opción "Todos los usuarios" al principio de la lista
            user_options = ["Todos los usuarios"] + user_emails
            
            # Selector de usuarios
            selected_user_option = st.selectbox(
                "Filtrar por usuario:",
                options=user_options,
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
            st.info(f"Mostrando datos de: {len(filtered_users_df)} usuarios, {len(filtered_travels_df)} viajes y {len(filtered_coords_df)} coordenadas.")
        else:
            st.warning("La columna 'email' no está disponible en la tabla de usuarios para filtrar")
            # Usar los datos sin filtrar
            filtered_users_df = users_df
            filtered_travels_df = travels_df
            filtered_coords_df = coords_df
        
        # TABLA 1: Usuarios
        if show_users and filtered_users_df is not None:
            st.subheader("👤 Tabla de Usuarios")
            
            # Columnas a mostrar para usuarios
            users_columns = [
                'user_id', 'email', 'name', 'role', 'created_at',
                'last_login', 'updated_at'
            ]
            
            # Filtrar solo las columnas que existen
            existing_users_columns = [col for col in users_columns if col in filtered_users_df.columns]
            
            # Mostrar tabla
            st.dataframe(filtered_users_df[existing_users_columns], use_container_width=True)
            
            # Se ha eliminado el resumen por rol
            
            # Opción para descargar como CSV
            users_csv = filtered_users_df[existing_users_columns].to_csv(index=False)
            st.download_button(
                label="Descargar Usuarios como CSV",
                data=users_csv,
                file_name="usuarios_filtrados.csv",
                mime="text/csv"
            )
        
        # TABLA 2: Viajes
        if show_travels and filtered_travels_df is not None:
            st.subheader("🧭 Tabla de Viajes")
            
            # Columnas a mostrar para viajes
            travels_columns = [
                'timestamp', 'end_timestamp', 'travel_id', 'user_id', 'user_email',
                'type', 'coords_lat', 'coords_lon', 'initial_coords_lat', 'initial_coords_lon',
                'final_coords_lat', 'final_coords_lon', 'distance', 'duration'
            ]
            
            # Filtrar solo las columnas que existen
            existing_travels_columns = [col for col in travels_columns if col in filtered_travels_df.columns]
            
            # Mostrar tabla
            st.dataframe(filtered_travels_df[existing_travels_columns], use_container_width=True)
            
            # Se ha eliminado el resumen estadístico
            
            # Opción para descargar como CSV
            travels_csv = filtered_travels_df[existing_travels_columns].to_csv(index=False)
            st.download_button(
                label="Descargar Viajes como CSV",
                data=travels_csv,
                file_name="viajes_filtrados.csv",
                mime="text/csv"
            )
        
        # TABLA 3: Coordenadas
        if show_coords and filtered_coords_df is not None:
            st.subheader("📍 Tabla de Coordenadas")
            
            # Columnas a mostrar para coordenadas
            coords_columns = [
                'timestamp', 'travel_id', 'user_id', 'user_email',
                'lat', 'lon', 'accuracy', 'altitude', 'speed'
            ]
            
            # Filtrar solo las columnas que existen
            existing_coords_columns = [col for col in coords_columns if col in filtered_coords_df.columns]
            
            # Mostrar tabla
            st.dataframe(filtered_coords_df[existing_coords_columns], use_container_width=True)
            
            # Se ha eliminado el resumen estadístico
            
            # Opción para descargar como CSV
            coords_csv = filtered_coords_df[existing_coords_columns].to_csv(index=False)
            st.download_button(
                label="Descargar Coordenadas como CSV",
                data=coords_csv,
                file_name="coordenadas_filtradas.csv",
                mime="text/csv"
            )
    else:
        st.info("Por favor, haga clic en 'Cargar Datos' para visualizar las tablas.")

# Ejecutar la función principal
if __name__ == "__main__":
    main()

# Mostrar pie de página
show_footer()