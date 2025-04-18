import streamlit as st
import folium
from folium import plugins
from streamlit_folium import folium_static
import pandas as pd
from services.travel_service import get_all_travel_coordinates, get_travel
import random

# Función para crear un mapa base
def create_base_map(center=[20, 0], zoom=2):
    # Crear mapa base
    m = folium.Map(location=center, zoom_start=zoom, control_scale=True)
    
    # Añadir control de capas
    folium.LayerControl().add_to(m)
    
    # Añadir plugin de búsqueda de ubicación
    plugins.Geocoder().add_to(m)
    
    # Añadir plugin de medición
    plugins.MeasureControl().add_to(m)
    
    # Añadir plugin de pantalla completa
    plugins.Fullscreen().add_to(m)
    
    return m

# Función para añadir un marcador al mapa
def add_marker(m, lat, lon, popup=None, tooltip=None, icon=None, color='blue'):
    if not icon:
        icon = folium.Icon(color=color, icon='info-sign')
    
    folium.Marker(
        location=[lat, lon],
        popup=popup,
        tooltip=tooltip,
        icon=icon
    ).add_to(m)

# Función para añadir una línea al mapa
def add_line(m, coordinates, popup=None, tooltip=None, color='blue', weight=2):
    folium.PolyLine(
        locations=coordinates,
        popup=popup,
        tooltip=tooltip,
        color=color,
        weight=weight
    ).add_to(m)

# Función para generar un color aleatorio para cada usuario
@st.cache_data
def get_user_color(user_id):
    # Lista de colores para asignar a los usuarios
    colors = [
        'red', 'blue', 'green', 'purple', 'orange', 'darkred',
        'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue',
        'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen',
        'gray', 'black', 'lightgray'
    ]
    
    # Usar un hash simple para asignar un color consistente a cada usuario
    if user_id:
        hash_value = sum(ord(c) for c in str(user_id))
        color_index = hash_value % len(colors)
        return colors[color_index]
    
    # Color por defecto si no hay ID de usuario
    return 'blue'

# Componente para mostrar un mapa con todos los viajes
def travel_map_component(center=None, zoom=None):
    # Obtener todas las coordenadas de viajes
    coordinates = get_all_travel_coordinates()
    
    # Si no hay coordenadas, mostrar un mensaje
    if not coordinates:
        st.warning("No hay viajes disponibles para mostrar.")
        return
    
    # Verificar que tenemos datos válidos
    valid_coordinates = []
    for coord in coordinates:
        try:
            # Asegurarse de que lat y lon son números
            lat = float(coord.get('lat', 0))
            lon = float(coord.get('lon', 0))
            if lat != 0 and lon != 0:  # Filtrar coordenadas no válidas
                valid_coord = coord.copy()
                valid_coord['lat'] = lat
                valid_coord['lon'] = lon
                # Asegurarse de que timestamp es una cadena para evitar problemas
                if 'timestamp' in valid_coord:
                    valid_coord['timestamp'] = str(valid_coord['timestamp'])
                valid_coordinates.append(valid_coord)
        except (ValueError, TypeError) as e:
            # Ignorar coordenadas inválidas
            print(f"Coordenada inválida ignorada: {coord}, Error: {e}")
    
    # Si no quedan coordenadas válidas después del filtrado
    if not valid_coordinates:
        st.warning("No se encontraron coordenadas válidas para mostrar.")
        return
    
    # Convertir coordenadas a DataFrame para facilitar el manejo
    df = pd.DataFrame(valid_coordinates)

# Componente para mostrar un mapa de calor de viajes
def heatmap_component():
    # Obtener todas las coordenadas de viajes
    coordinates = get_all_travel_coordinates()
    
    # Si no hay coordenadas, mostrar un mensaje
    if not coordinates:
        st.warning("No hay viajes disponibles para mostrar en el mapa de calor.")
        return
    
    # Verificar que tenemos datos válidos
    valid_coordinates = []
    for coord in coordinates:
        try:
            # Asegurarse de que lat y lon son números
            lat = float(coord.get('lat', 0))
            lon = float(coord.get('lon', 0))
            if lat != 0 and lon != 0:  # Filtrar coordenadas no válidas
                valid_coord = coord.copy()
                valid_coord['lat'] = lat
                valid_coord['lon'] = lon
                # Asegurarse de que timestamp es una cadena para evitar problemas
                if 'timestamp' in valid_coord:
                    valid_coord['timestamp'] = str(valid_coord['timestamp'])
                valid_coordinates.append(valid_coord)
        except (ValueError, TypeError) as e:
            # Ignorar coordenadas inválidas
            print(f"Coordenada inválida ignorada: {coord}, Error: {e}")
    
    # Si no quedan coordenadas válidas después del filtrado
    if not valid_coordinates:
        st.warning("No se encontraron coordenadas válidas para mostrar.")
        return
    
    # Convertir coordenadas a DataFrame para facilitar el manejo
    df = pd.DataFrame(valid_coordinates)

def create_travel_map(valid_coords):
    """Creates and returns a map with travel data visualization"""
    if len(valid_coords) == 0:
        return None
    
    # Calculate map center
    center = [valid_coords['lat'].mean(), valid_coords['lon'].mean()]
    
    # Create base map
    m = folium.Map(location=center, zoom_start=10, control_scale=True)
    
    # Add map controls
    folium.LayerControl().add_to(m)
    
    # Colors for each trip
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 
            'lightblue', 'darkgreen', 'cadetblue', 'darkpurple', 
            'beige', 'pink', 'gray', 'black', 'lightred', 'lightgreen']
    
    # Get unique travel IDs
    travel_ids = valid_coords['travel_id'].unique()
    
    # Process points for each trip
    for i, travel_id in enumerate(travel_ids):
        # Select color for this trip
        color = colors[i % len(colors)]
        
        # Filter coordinates for this trip
        travel_coords = valid_coords[valid_coords['travel_id'] == travel_id].copy()
        
        # Sort by timestamp if available
        if 'timestamp' in travel_coords.columns:
            try:
                travel_coords['timestamp'] = pd.to_datetime(travel_coords['timestamp'], errors='coerce')
                travel_coords = travel_coords.sort_values('timestamp')
            except:
                pass
        
        # Create coordinate list for the line
        line_coords = []
        
        # Add markers and collect coordinates for the line
        for idx, row in travel_coords.iterrows():
            line_coords.append([row['lat'], row['lon']])
            
            # Create popup text
            popup_text = f"<b>ID de Viaje:</b> {travel_id}<br>"
            
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
            
            # Create marker
            folium.Marker(
                location=[row['lat'], row['lon']],
                popup=folium.Popup(popup_text, max_width=300),
                tooltip=f"Viaje: {travel_id}",
                icon=folium.Icon(color=color, icon='info-sign')
            ).add_to(m)
        
        # Draw dotted line if there are at least 2 points
        if len(line_coords) >= 2:
            folium.PolyLine(
                locations=line_coords,
                color=color,
                weight=3,
                opacity=0.7,
                dash_array='5, 10',
                tooltip=f"Ruta del viaje: {travel_id}"
            ).add_to(m)
        
        # Add accuracy circles if available
        if 'accuracy' in travel_coords.columns:
            for idx, row in travel_coords.iterrows():
                if pd.notna(row['accuracy']) and float(row['accuracy']) > 0:
                    folium.Circle(
                        location=[row['lat'], row['lon']],
                        radius=float(row['accuracy']),
                        color=color,
                        fill=True,
                        fill_opacity=0.1
                    ).add_to(m)
    
    return m

def validate_coordinates(coords_df):
    """Validates and filters coordinate data"""
    if coords_df is None or len(coords_df) == 0:
        return None
        
    # Verify we have valid coordinates to show
    valid_coords = coords_df.dropna(subset=['lat', 'lon']).copy()
    
    if len(valid_coords) == 0:
        return None
        
    # Ensure lat and lon are numeric values
    valid_coords['lat'] = pd.to_numeric(valid_coords['lat'], errors='coerce')
    valid_coords['lon'] = pd.to_numeric(valid_coords['lon'], errors='coerce')
    
    # Remove rows with non-numeric values or out of range
    valid_coords = valid_coords[
        (valid_coords['lat'] >= -90) & 
        (valid_coords['lat'] <= 90) & 
        (valid_coords['lon'] >= -180) & 
        (valid_coords['lon'] <= 180)
    ]
    
    if len(valid_coords) == 0:
        return None
        
    return valid_coords