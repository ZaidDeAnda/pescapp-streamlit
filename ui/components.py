import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from datetime import datetime

def create_map(coord_list, height=500):
    """
    Create an interactive map with route markers and lines
    
    Args:
        coord_list: List of coordinates (must have lat/latitude and lon/longitude keys)
        height: Height of the map in pixels
        
    Returns:
        folium.Map or None: The created map or None if error
    """
    if not coord_list:
        st.warning("No hay coordenadas disponibles para mostrar")
        return None
        
    try:
        # Function to get latitude value, handling different possible field names
        def get_lat(coord):
            if "lat" in coord:
                return coord["lat"]
            elif "latitude" in coord:
                return coord["latitude"]
            else:
                return 0
                
        # Function to get longitude value, handling different possible field names
        def get_lon(coord):
            if "lon" in coord:
                return coord["lon"]
            elif "lng" in coord:
                return coord["lng"]
            elif "longitude" in coord:
                return coord["longitude"]
            else:
                return 0
        
        # Center map on first point
        inicio = coord_list[0]
        mapa = folium.Map(location=[get_lat(inicio), get_lon(inicio)], zoom_start=13)
        
        icon_image = "assets/Elipse.png"
        
        # Add markers and collect coordinates for line
        coordenadas = []
        for i, coord_dict in enumerate(coord_list, start=1):
            lat = get_lat(coord_dict)
            lon = get_lon(coord_dict)
            coord = [lat, lon]
            coordenadas.append(coord)
            offsetx = -0.0005
            offsety = 0.0005
            
            # Create custom icon
            icon = folium.CustomIcon(
                icon_image,
                icon_size=(20, 20),
                icon_anchor=(20, 20),
            )
            
            # Add marker
            folium.Marker(
                location=[lat+offsetx, lon+offsety],
                popup=f"Punto {i}",
                icon=icon
            ).add_to(mapa)
        
        # Add polyline connecting all points
        folium.PolyLine(coordenadas, color="blue", weight=2.5, opacity=1).add_to(mapa)
        
        # Display the map
        return st_folium(mapa, height=height)
        
    except Exception as e:
        st.error(f"Error al crear el mapa: {str(e)}")
        return None

def display_travel_stats(coord_list, travel_info=None):
    """
    Display statistics for a travel/route
    
    Args:
        coord_list: List of coordinates with timestamps
        travel_info: Additional travel information (optional)
    """
    # Helper functions to get lat/lon with different possible field names
    def get_lat(coord):
        if "lat" in coord:
            return coord["lat"]
        elif "latitude" in coord:
            return coord["latitude"]
        else:
            st.error(f"No latitude field found in coordinate data")
            return 0
            
    def get_lon(coord):
        if "lon" in coord:
            return coord["lon"]
        elif "lng" in coord:
            return coord["lng"]
        elif "longitude" in coord:
            return coord["longitude"]
        else:
            st.error(f"No longitude field found in coordinate data")
            return 0
            
    # Display user info if available
    if travel_info:
        user_name = travel_info.get('user_name', 'Desconocido')
        user_email = travel_info.get('user_email', 'Desconocido')
        
        st.metric("Usuario", f"{user_name if user_name else user_email}")
        st.metric("Email", user_email)
    
    # Calculate and display statistics
    if len(coord_list) > 1:
        try:
            # Calculate distance using our helper functions
            total_distance = sum([
                ((get_lat(coord_list[i]) - get_lat(coord_list[i-1]))**2 + 
                 (get_lon(coord_list[i]) - get_lon(coord_list[i-1]))**2)**0.5 
                for i in range(1, len(coord_list))
            ]) * 111  # Approximate km conversion (1 degree ≈ 111 km)
            
            # Check if valid timestamps exist
            has_valid_timestamps = (
                'timestamp' in coord_list[0] and 
                'timestamp' in coord_list[-1] and 
                isinstance(coord_list[0]['timestamp'], datetime) and 
                isinstance(coord_list[-1]['timestamp'], datetime)
            )
            
            # Calculate and display time-based metrics if possible
            if has_valid_timestamps:
                time_diff = coord_list[-1]['timestamp'] - coord_list[0]['timestamp']
                hours = time_diff.total_seconds() / 3600  # Convert to hours
                
                if hours > 0:
                    avg_speed = total_distance / hours
                    st.metric("Velocidad Promedio", f"{avg_speed:.2f} km/h")
                
                st.metric("Duración", f"{hours:.2f} horas")
                
                # Show timestamps
                start_time = coord_list[0]['timestamp']
                end_time = coord_list[-1]['timestamp']
                
                st.metric("Inicio", start_time.strftime("%Y-%m-%d %H:%M:%S"))
                st.metric("Fin", end_time.strftime("%Y-%m-%d %H:%M:%S"))
            
            # Always show these metrics
            st.metric("Distancia Total", f"{total_distance:.2f} km")
            st.metric("Total de Puntos", len(coord_list))
        except Exception as e:
            st.error(f"Error al calcular estadísticas: {str(e)}")
            import traceback
            st.error(traceback.format_exc())
    else:
        st.warning("Datos insuficientes para calcular estadísticas")

def create_summary_metrics(stats_dict):
    """
    Create summary metrics from user statistics
    
    Args:
        stats_dict: Dictionary of user statistics
    """
    if not stats_dict:
        st.warning("No hay datos disponibles para mostrar estadísticas")
        return
        
    # Calculate aggregate statistics
    total_trips = sum(stat['total_travels'] for stat in stats_dict.values())
    total_distance = sum(stat['total_distance'] for stat in stats_dict.values())
    total_duration = sum(stat['total_duration'] for stat in stats_dict.values())
    
    # Calculate averages (avoid division by zero)
    avg_distance_per_trip = total_distance / total_trips if total_trips > 0 else 0
    avg_duration_per_trip = total_duration / total_trips if total_trips > 0 else 0
    avg_speed = total_distance / total_duration if total_duration > 0 else 0
    
    # Determine the date range of trips
    all_first_dates = [stat['first_travel_date'] for stat in stats_dict.values() if stat['first_travel_date']]
    all_last_dates = [stat['last_travel_date'] for stat in stats_dict.values() if stat['last_travel_date']]
    
    first_date = min(all_first_dates) if all_first_dates else "N/A"
    last_date = max(all_last_dates) if all_last_dates else "N/A"
    
    # Display summary metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total de Usuarios", len(stats_dict))
        st.metric("Total de Viajes", total_trips)
    
    with col2:
        st.metric("Distancia Total", f"{total_distance:.2f} km")
        st.metric("Tiempo Total", f"{total_duration:.2f} horas")
    
    with col3:
        st.metric("Velocidad Promedio", f"{avg_speed:.2f} km/h")
        st.metric("Distancia Promedio por Viaje", f"{avg_distance_per_trip:.2f} km")
    
    st.metric("Primer Viaje Registrado", first_date)
    st.metric("Último Viaje Registrado", last_date)

def stats_to_dataframe(stats):
    """
    Convert user statistics to a pandas DataFrame
    
    Args:
        stats: Dictionary of user statistics
        
    Returns:
        pandas.DataFrame: DataFrame with user statistics
    """
    user_data = []
    for email, user_stat in stats.items():
        user_data.append({
            'Usuario': email,
            'Total de Viajes': user_stat['total_travels'],
            'Distancia Total (km)': f"{user_stat['total_distance']:.2f}",
            'Tiempo Total (horas)': f"{user_stat['total_duration']:.2f}",
            'Velocidad Promedio (km/h)': f"{user_stat['avg_speed']:.2f}",
            'Primer Viaje': user_stat['first_travel_date'] or "N/A",
            'Último Viaje': user_stat['last_travel_date'] or "N/A"
        })
    
    return pd.DataFrame(user_data)