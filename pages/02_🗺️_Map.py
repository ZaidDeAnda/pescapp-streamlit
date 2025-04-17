import streamlit as st
import pandas as pd
import folium
from folium import plugins
from streamlit_folium import folium_static
from components.auth_class import Authentication
from components.navigation import setup_sidebar, show_header, show_footer
from services.travel_service import get_travel_coordinates, get_user_travels, get_travel
from services.user_service import get_all_users, get_assigned_users
from models.user import User
import json

# Configurar la página
st.set_page_config(
    page_title="Travel Tracker - Mapa",
    page_icon="🗺️",
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

# Obtener información del usuario actual
current_user = auth.get_current_user()
user_role = current_user.get('role', 'user')
user_id = current_user.get('id')

# Mostrar header
show_header(
    "🗺️ Mapa de Viajes",
    "Visualiza los viajes registrados en el mapa interactivo."
)

# Función para obtener usuarios visibles según el rol
def get_visible_users():
    if user_role == 'admin':
        # Administrador puede ver todos los usuarios
        users = get_all_users()
        # Convertir objetos User a diccionarios
        return [user.to_dict() if hasattr(user, 'to_dict') else user for user in users]
    elif user_role == 'monitor':
        # Monitor puede verse a sí mismo y a usuarios asignados
        assigned_users = get_assigned_users(user_id)
        # Convertir objetos User a diccionarios
        users_dict = [user.to_dict() if hasattr(user, 'to_dict') else user for user in assigned_users]
        # Agregar al monitor actual a la lista
        users_dict.append(current_user)
        return users_dict
    else:
        # Usuario normal solo puede verse a sí mismo
        return [current_user]

# Función para procesar viaje y extraer coordenadas
def process_travel_coordinates(travel_id):
    try:
        # Verificar primero si el viaje existe
        travel_data = get_travel(travel_id)
        if travel_data is None:
            st.warning(f"Viaje no encontrado: {travel_id}")
            return []
        
        # Obtener coordenadas para este viaje
        coordinates = get_travel_coordinates(travel_id)
        
        # Verificar si se obtuvieron coordenadas (la función actualizada siempre devuelve lista, nunca None)
        if not coordinates:
            return []
        
        # Procesar coordenadas
        valid_coords = []
        for coord in coordinates:
            if isinstance(coord, dict):
                # Validar lat/lon
                try:
                    lat = float(coord.get('lat', 0))
                    lon = float(coord.get('lon', 0))
                    
                    if lat != 0 and lon != 0:
                        # Crear copia para no modificar original
                        valid_coord = {
                            'lat': lat,
                            'lon': lon,
                            'travel_id': travel_id,
                            'timestamp': str(coord.get('timestamp', ''))
                        }
                        
                        # Añadir datos adicionales si existen
                        if 'user_id' in coord:
                            valid_coord['user_id'] = str(coord.get('user_id', ''))
                        if 'user_email' in coord:
                            valid_coord['user_email'] = str(coord.get('user_email', ''))
                        if 'accuracy' in coord:
                            valid_coord['accuracy'] = coord.get('accuracy')
                        if 'altitude' in coord:
                            valid_coord['altitude'] = coord.get('altitude')
                        if 'speed' in coord:
                            valid_coord['speed'] = coord.get('speed')
                        
                        valid_coords.append(valid_coord)
                except Exception as e:
                    continue  # Ignorar coordenadas inválidas
        
        return valid_coords
    except Exception as e:
        st.warning(f"Error al procesar coordenadas del viaje {travel_id}: {str(e)}")
        return []

# Función para depurar un viaje
def debug_travel(travel_id):
    st.subheader(f"Depuración del viaje: {travel_id}")
    
    # Obtener datos del viaje
    travel_data = get_travel(travel_id)
    
    if travel_data is None:
        st.error(f"No se encontró el viaje con ID: {travel_id}")
        return
    
    # Mostrar información del viaje
    st.write("Datos del viaje:")
    
    # Convertir a diccionario si es un objeto
    if hasattr(travel_data, 'to_dict'):
        travel_dict = travel_data.to_dict()
    else:
        travel_dict = travel_data
    
    # Mostrar datos en formato JSON
    st.json(travel_dict)
    
    # Intentar obtener coordenadas
    st.write("Intentando obtener coordenadas:")
    try:
        coords = get_travel_coordinates(travel_id)
        if coords:
            st.success(f"Se encontraron {len(coords)} coordenadas.")
            st.json(coords)
        else:
            st.warning("No se encontraron coordenadas para este viaje.")
    except Exception as e:
        st.error(f"Error al obtener coordenadas: {str(e)}")

# Función principal
def main():
    # Inicializar estados en la sesión si no existen
    if 'step' not in st.session_state:
        st.session_state.step = 1
    
    # PASO 1: Seleccionar usuarios
    if st.session_state.step == 1:
        st.subheader("Paso 1: Selecciona usuarios")
        
        # Obtener usuarios visibles
        visible_users = get_visible_users()
        
        if not visible_users:
            st.warning("No se encontraron usuarios disponibles.")
            return
        
        # Crear opciones de usuarios para la selección
        user_options = {}
        for user in visible_users:
            # Verificar si es un objeto User o un diccionario
            if isinstance(user, dict):
                user_id = user.get('id')
                user_name = user.get('name', 'Usuario')
                user_email = user.get('email', '')
            elif isinstance(user, User):
                user_id = user.id
                user_name = user.name
                user_email = user.email
            else:
                continue  # Saltar si no es un formato reconocido
                
            user_options[user_id] = f"{user_name} ({user_email})"
        
        # Selección de usuarios
        selected_user_ids = st.multiselect(
            "Selecciona los usuarios que deseas ver:",
            options=list(user_options.keys()),
            default=[current_user.get('id')],
            format_func=lambda x: user_options.get(x, x)
        )
        
        # Botón para continuar
        if st.button("Continuar al paso 2"):
            if selected_user_ids:
                st.session_state.selected_user_ids = selected_user_ids
                st.session_state.step = 2
                st.rerun()
            else:
                st.error("Debes seleccionar al menos un usuario.")
    
    # PASO 2: Seleccionar viajes
    elif st.session_state.step == 2:
        st.subheader("Paso 2: Selecciona viajes")
        
        # Mostrar usuarios seleccionados
        selected_user_ids = st.session_state.selected_user_ids
        
        # Obtener viajes de los usuarios seleccionados
        all_travels = []
        for uid in selected_user_ids:
            try:
                user_travels = get_user_travels(uid)
                if user_travels:
                    # Verificar si recibimos una lista de diccionarios o de objetos
                    for travel in user_travels:
                        if hasattr(travel, 'to_dict'):
                            # Si es un objeto con método to_dict, convertirlo
                            all_travels.append(travel.to_dict())
                        else:
                            # Si ya es un diccionario, usar tal cual
                            all_travels.append(travel)
            except Exception as e:
                st.warning(f"Error al obtener viajes del usuario {uid}: {str(e)}")
        
        if not all_travels:
            st.warning("No se encontraron viajes para los usuarios seleccionados.")
            
            # Botón para volver al paso 1
            if st.button("Volver al paso 1"):
                st.session_state.step = 1
                st.rerun()
            return
        
        # Formatear opciones de viajes para la selección
        travel_options = {}
        for travel in all_travels:
            travel_id = travel.get('id') or travel.get('travel_id')
            if travel_id:
                # Obtener información para mostrar
                user_email = travel.get('user_email', 'Usuario')
                timestamp = str(travel.get('timestamp', 'Sin fecha'))
                travel_type = travel.get('type', 'viaje')
                
                # Crear ID corto para mostrar
                travel_id_str = str(travel_id)
                short_id = travel_id_str[:8] + "..." if len(travel_id_str) > 8 else travel_id_str
                
                # Crear timestamp corto
                short_timestamp = timestamp[:10] if len(timestamp) > 10 else timestamp
                
                travel_options[travel_id] = f"Viaje {short_id} | {user_email} | {short_timestamp} | {travel_type}"
        
        # Selección de viajes
        selected_travel_ids = st.multiselect(
            "Selecciona los viajes a mostrar en el mapa:",
            options=list(travel_options.keys()),
            default=list(travel_options.keys()),
            format_func=lambda x: travel_options.get(x, x)
        )
        
        # Botones de navegación
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Volver al paso 1"):
                st.session_state.step = 1
                st.rerun()
        
        with col2:
            if st.button("Ver mapa"):
                if selected_travel_ids:
                    st.session_state.selected_travel_ids = selected_travel_ids
                    st.session_state.step = 3
                    st.rerun()
                else:
                    st.error("Debes seleccionar al menos un viaje.")
    
    # PASO 3: Mostrar mapa
    elif st.session_state.step == 3:
        st.subheader("Mapa de Viajes")
        
        # Obtener viajes seleccionados
        selected_travel_ids = st.session_state.selected_travel_ids
        
        # Añadir modo de depuración
        debug_mode = st.checkbox("Modo de depuración", value=False)
        
        if debug_mode:
            # Permitir seleccionar un viaje específico para depurar
            debug_travel_id = st.selectbox(
                "Seleccionar viaje para depurar:",
                options=selected_travel_ids
            )
            
            if debug_travel_id:
                debug_travel(debug_travel_id)
                st.divider()
        
        # Procesar coordenadas de cada viaje
        all_coordinates = []
        problematic_travels = []
        
        with st.spinner("Procesando coordenadas de viajes..."):
            progress_bar = st.progress(0)
            
            for i, travel_id in enumerate(selected_travel_ids):
                # Actualizar barra de progreso
                progress = (i + 1) / len(selected_travel_ids)
                progress_bar.progress(progress)
                
                # Intentar obtener coordenadas
                try:
                    coords = process_travel_coordinates(travel_id)
                    if coords:
                        all_coordinates.extend(coords)
                    else:
                        problematic_travels.append(travel_id)
                except Exception as e:
                    st.error(f"Error al procesar el viaje {travel_id}: {str(e)}")
                    problematic_travels.append(travel_id)
            
            # Ocultar barra de progreso
            progress_bar.empty()
        
        # Mostrar viajes con problemas
        if problematic_travels:
            with st.expander(f"Viajes sin coordenadas válidas ({len(problematic_travels)})"):
                for travel_id in problematic_travels:
                    st.write(f"- Viaje: {travel_id}")
        
        if not all_coordinates:
            st.warning("No se encontraron coordenadas válidas para los viajes seleccionados.")
            
            # Botón para volver al paso 2
            if st.button("Volver a seleccionar viajes"):
                st.session_state.step = 2
                st.rerun()
            return
        
        # Crear DataFrame
        df = pd.DataFrame(all_coordinates)
        
        # Mostrar información sobre los datos
        st.success(f"Se encontraron {len(df)} coordenadas para mostrar en el mapa.")
        
        # Opciones del mapa
        col1, col2 = st.columns([3, 1])
        
        with col2:
            st.write("#### Opciones del Mapa")
            
            map_style = st.selectbox(
                "Estilo del Mapa:",
                options=["OpenStreetMap", "Stamen Terrain", "Stamen Toner", "CartoDB positron"],
                index=0
            )
            
            show_lines = st.checkbox("Mostrar líneas entre puntos", value=True)
            show_popup = st.checkbox("Mostrar información al hacer clic", value=True)
            
            # Mostrar mini resumen
            st.write("#### Resumen")
            st.write(f"Total puntos: {len(df)}")
            st.write(f"Viajes mostrados: {len(df['travel_id'].unique())}")
            
            # Botón para volver
            if st.button("Volver a seleccionar viajes"):
                st.session_state.step = 2
                st.rerun()
        
        with col1:
            # Verificar si hay datos para mostrar
            if df.empty:
                st.warning("No hay datos para mostrar en el mapa.")
                return
                
            # Calcular el centro del mapa
            center = [df['lat'].mean(), df['lon'].mean()]
            
            # Crear mapa base
            m = folium.Map(location=center, zoom_start=10, tiles=map_style)
            
            # Añadir controles
            folium.LayerControl().add_to(m)
            plugins.Fullscreen().add_to(m)
            plugins.MousePosition().add_to(m)
            plugins.MeasureControl().add_to(m)
            
            # Colores para diferentes viajes
            colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightblue', 'darkgreen', 'cadetblue', 'darkpurple']
            
            # Añadir marcadores y líneas
            for i, travel_id in enumerate(df['travel_id'].unique()):
                # Seleccionar color para este viaje
                color = colors[i % len(colors)]
                
                # Filtrar puntos de este viaje
                travel_points = df[df['travel_id'] == travel_id]
                
                # Añadir marcadores
                for idx, row in travel_points.iterrows():
                    # Crear popup personalizado si está habilitado
                    if show_popup:
                        popup_html = f"""
                        <div style="width: 200px;">
                            <h4>Información del Punto</h4>
                            <b>Viaje:</b> {row['travel_id']}<br>
                        """
                        
                        # Añadir campos adicionales si existen
                        if 'user_email' in row:
                            popup_html += f"<b>Usuario:</b> {row['user_email']}<br>"
                        if 'timestamp' in row:
                            popup_html += f"<b>Fecha:</b> {row['timestamp']}<br>"
                        if 'accuracy' in row:
                            popup_html += f"<b>Precisión:</b> {row['accuracy']} m<br>"
                        if 'altitude' in row:
                            popup_html += f"<b>Altitud:</b> {row['altitude']} m<br>"
                        if 'speed' in row:
                            popup_html += f"<b>Velocidad:</b> {row['speed']} m/s<br>"
                        
                        popup_html += f"""
                            <b>Latitud:</b> {row['lat']:.6f}<br>
                            <b>Longitud:</b> {row['lon']:.6f}<br>
                        </div>
                        """
                        
                        popup = folium.Popup(folium.Html(popup_html, script=True), max_width=300)
                    else:
                        popup = None
                    
                    # Crear tooltip (etiqueta al pasar el mouse)
                    travel_id_str = str(row['travel_id'])
                    short_id = travel_id_str[:8] + "..." if len(travel_id_str) > 8 else travel_id_str
                    tooltip = f"Viaje: {short_id}"
                    
                    # Añadir marcador al mapa
                    folium.Marker(
                        location=[row['lat'], row['lon']],
                        popup=popup,
                        tooltip=tooltip,
                        icon=folium.Icon(color=color, icon='info-sign')
                    ).add_to(m)
                
                # Añadir líneas si está activado y hay más de un punto
                if show_lines and len(travel_points) >= 2:
                    # Crear lista de coordenadas
                    line_coords = [[row['lat'], row['lon']] for idx, row in travel_points.iterrows()]
                    
                    # Añadir línea
                    folium.PolyLine(
                        locations=line_coords,
                        color=color,
                        weight=2.5,
                        opacity=0.7,
                        tooltip=f"Ruta viaje: {short_id}"
                    ).add_to(m)
            
            # Mostrar mapa
            folium_static(m, width=800, height=600)

# Ejecutar la función principal
if __name__ == "__main__":
    main()

# Mostrar pie de página
show_footer()