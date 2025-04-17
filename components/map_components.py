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