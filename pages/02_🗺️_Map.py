import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from components.auth_class import Authentication
from components.navigation import setup_sidebar, show_header, show_footer
from services.travel_service import get_all_travel_coordinates

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

# Mostrar header
show_header(
    "🗺️ Mapa de Viajes",
    "Visualiza todos tus viajes registrados en el mapa interactivo."
)

# Función principal
def main():
    # 1. Obtener todas las coordenadas disponibles en la base de datos
    st.write("Obteniendo coordenadas de la base de datos...")
    coordinates = get_all_travel_coordinates()
    
    # Verificar si hay datos
    if not coordinates or len(coordinates) == 0:
        st.warning("No se encontraron coordenadas para mostrar en el mapa.")
        return
    
    st.success(f"Se encontraron {len(coordinates)} coordenadas.")
    
    # 2. Transformar en DataFrame
    st.write("Convirtiendo coordenadas a DataFrame...")
    
    # Asegurar que las coordenadas tengan el formato correcto
    valid_coordinates = []
    for coord in coordinates:
        try:
            # Validar y convertir lat/lon a float
            lat = float(coord.get('lat', 0))
            lon = float(coord.get('lon', 0))
            
            # Solo incluir coordenadas válidas
            if lat != 0 and lon != 0:
                valid_coord = {
                    'lat': lat,
                    'lon': lon,
                    'travel_id': coord.get('travel_id', 'desconocido'),
                    # Convertir timestamp a string para evitar problemas
                    'timestamp': str(coord.get('timestamp', ''))
                }
                
                # Incluir datos de usuario si están disponibles
                if 'user_email' in coord:
                    valid_coord['user_email'] = str(coord.get('user_email', ''))
                
                valid_coordinates.append(valid_coord)
        except Exception as e:
            st.write(f"Se omitió una coordenada inválida: {e}")
    
    # Verificar si quedaron coordenadas válidas después del filtrado
    if not valid_coordinates:
        st.warning("No quedaron coordenadas válidas después del filtrado.")
        return
    
    # Crear DataFrame
    df = pd.DataFrame(valid_coordinates)
    st.write(f"DataFrame creado con {len(df)} coordenadas.")
    
    # Mostrar primeras filas para verificación
    st.write("Muestra de datos:")
    st.dataframe(df.head())
    
    # 3. Mostrar en mapa Folium
    st.write("Creando mapa...")
    
    # Calcular el centro del mapa (promedio de coordenadas)
    center = [df['lat'].mean(), df['lon'].mean()]
    
    # Crear mapa base
    m = folium.Map(location=center, zoom_start=10, control_scale=True)
    
    # Añadir marcadores para cada punto
    for _, row in df.iterrows():
        # Crear popup con información disponible
        popup_text = f"Viaje: {row['travel_id']}"
        if 'user_email' in row:
            popup_text += f"<br>Usuario: {row['user_email']}"
        if 'timestamp' in row:
            popup_text += f"<br>Fecha: {row['timestamp']}"
        
        # Añadir marcador al mapa
        folium.Marker(
            location=[row['lat'], row['lon']],
            popup=popup_text,
            tooltip=f"Viaje: {row['travel_id']}"
        ).add_to(m)
    
    # Mostrar el mapa
    st.write("Mostrando mapa:")
    folium_static(m, width=1000, height=600)

# Ejecutar la función principal
if __name__ == "__main__":
    main()

# Mostrar pie de página
show_footer()