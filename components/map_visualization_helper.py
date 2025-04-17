import streamlit as st
import pandas as pd
import folium
from folium import plugins
from streamlit_folium import folium_static
from services.travel_service import get_travel_coordinates, get_coords_from_collection, get_all_travel_coordinates

def show_direct_coords_map():
    """
    Muestra un mapa con coordenadas cargadas directamente de la colección 'coords'
    Útil para depurar problemas con las coordenadas
    """
    st.subheader("Mapa de Coordenadas Directas")
    
    # Cargar coordenadas directamente de la colección
    with st.spinner("Cargando coordenadas directamente de la base de datos..."):
        coords = get_coords_from_collection(limit=500)  # Limitar a 500 para rendimiento
    
    if not coords:
        st.warning("No se encontraron coordenadas en la colección 'coords'")
        return
    
    # Convertir a DataFrame
    try:
        df = pd.DataFrame(coords)
        
        # Verificar que contiene las columnas necesarias
        required_columns = ['lat', 'lon']
        if not all(col in df.columns for col in required_columns):
            st.error("Los datos no contienen las columnas requeridas (lat, lon)")
            st.write("Columnas disponibles:", df.columns.tolist())
            return
        
        # Asegurar que lat/lon son numéricos
        df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
        df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
        
        # Eliminar filas con valores NaN
        df = df.dropna(subset=['lat', 'lon'])
        
        # Añadir una columna travel_id si no existe
        if 'travel_id' not in df.columns:
            df['travel_id'] = "desconocido"
        
        # Mostrar información
        st.success(f"Se cargaron {len(df)} coordenadas válidas")
        
        # Mostrar una muestra de los datos
        st.write("Muestra de los datos:")
        st.dataframe(df.head())
        
        # Crear el mapa
        create_folium_map(df)
    
    except Exception as e:
        st.error(f"Error al procesar coordenadas: {str(e)}")

def create_folium_map(df, width=800, height=600):
    """
    Crea y muestra un mapa de Folium con las coordenadas proporcionadas
    
    Args:
        df: DataFrame de pandas con columnas 'lat' y 'lon'
        width: Ancho del mapa
        height: Alto del mapa
    """
    try:
        # Calcular el centro del mapa
        center = [df['lat'].mean(), df['lon'].mean()]
        
        # Crear mapa base
        m = folium.Map(location=center, zoom_start=10, control_scale=True)
        
        # Añadir controles
        folium.LayerControl().add_to(m)
        plugins.Fullscreen().add_to(m)
        plugins.MousePosition().add_to(m)
        plugins.MeasureControl().add_to(m)
        
        # Colores para diferentes viajes
        colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightblue', 
                 'darkgreen', 'cadetblue', 'darkpurple', 'beige', 'pink', 'gray']
        
        # Agrupar por travel_id
        travel_ids = df['travel_id'].unique()
        
        # Mostrar información sobre los viajes
        st.write(f"Total de viajes en el mapa: {len(travel_ids)}")
        
        # Añadir marcadores para cada punto
        for i, travel_id in enumerate(travel_ids):
            # Seleccionar color para este viaje
            color = colors[i % len(colors)]
            
            # Filtrar puntos de este viaje
            travel_points = df[df['travel_id'] == travel_id]
            
            # Crear lista de coordenadas
            line_coords = []
            
            # Añadir marcadores
            for idx, row in travel_points.iterrows():
                # Añadir a la lista de coordenadas para la línea
                line_coords.append([row['lat'], row['lon']])
                
                # Crear popup con información disponible
                popup_text = f"Viaje: {travel_id}"
                for col in travel_points.columns:
                    if col not in ['lat', 'lon', 'travel_id'] and pd.notna(row[col]):
                        popup_text += f"<br>{col}: {row[col]}"
                
                # Crear tooltip (etiqueta al pasar el mouse)
                travel_id_str = str(travel_id)
                short_id = travel_id_str[:8] + "..." if len(travel_id_str) > 8 else travel_id_str
                tooltip = f"Viaje: {short_id}"
                
                # Añadir marcador al mapa
                folium.Marker(
                    location=[row['lat'], row['lon']],
                    popup=popup_text,
                    tooltip=tooltip,
                    icon=folium.Icon(color=color, icon='info-sign')
                ).add_to(m)
            
            # Añadir línea si hay más de un punto
            if len(line_coords) >= 2:
                folium.PolyLine(
                    locations=line_coords,
                    color=color,
                    weight=2.5,
                    opacity=0.7,
                    tooltip=f"Ruta viaje: {short_id}"
                ).add_to(m)
        
        # Mostrar el mapa
        folium_static(m, width=width, height=height)
        
    except Exception as e:
        st.error(f"Error al crear el mapa: {str(e)}")

def quick_map_visualization():
    """
    Función para mostrar rápidamente un mapa con todas las coordenadas disponibles
    """
    st.subheader("Visualización Rápida de Viajes")
    
    # Ofrecer opciones de origen de datos
    data_source = st.radio(
        "Origen de los datos:",
        ["Viajes disponibles (recomendado)", "Colección coords directa"],
        horizontal=True
    )
    
    with st.spinner("Cargando coordenadas..."):
        # Obtener coordenadas según la opción seleccionada
        if data_source == "Colección coords directa":
            coords = get_coords_from_collection(limit=500)
            source_text = "colección coords"
        else:
            coords = get_all_travel_coordinates()
            source_text = "viajes disponibles"
    
    if not coords:
        st.warning(f"No se encontraron coordenadas en {source_text}")
        return
    
    # Convertir a DataFrame
    try:
        df = pd.DataFrame(coords)
        
        # Verificar que contiene las columnas necesarias
        required_columns = ['lat', 'lon']
        if not all(col in df.columns for col in required_columns):
            st.error("Los datos no contienen las columnas requeridas (lat, lon)")
            st.write("Columnas disponibles:", df.columns.tolist())
            return
        
        # Asegurar que lat/lon son numéricos
        df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
        df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
        
        # Eliminar filas con valores NaN
        df = df.dropna(subset=['lat', 'lon'])
        
        # Mostrar información
        st.success(f"Se cargaron {len(df)} coordenadas válidas de {source_text}")
        
        # Crear el mapa
        create_folium_map(df)
    
    except Exception as e:
        st.error(f"Error al procesar coordenadas: {str(e)}")