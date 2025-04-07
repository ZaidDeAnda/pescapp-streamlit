import streamlit as st
import pandas as pd
from datetime import datetime

from utils.database import collect_user_statistics, obtain_available_travels, obtain_coords_by_id
from ui.filters import filter_controls, get_users_to_analyze
from ui.components import stats_to_dataframe

def page_user_stats(db, user_role, user_email):
    """
    Page for displaying individual user statistics in table format
    
    Args:
        db: Firestore client
        user_role: Role of the current user
        user_email: Email of the current user
    """
    st.title("Estadísticas por Usuario 👤")
    
    # Get and apply filters
    start_date, end_date, selected_users = filter_controls(db, user_role, user_email)
    
    # Determine which users to include
    users_to_analyze = get_users_to_analyze(db, user_role, user_email, selected_users)
    
    if not users_to_analyze:
        st.warning("No hay usuarios disponibles para mostrar estadísticas")
        return
    
    # Collect statistics for all applicable users
    stats = collect_user_statistics(db, users_to_analyze)
    
    if not stats:
        st.warning("No hay datos disponibles para los usuarios seleccionados")
        return
    
    # Convert stats to DataFrame for display
    df_table = stats_to_dataframe(stats)
    
    # Create and display the table
    st.subheader("Tabla de Estadísticas por Usuario")
    st.dataframe(
        df_table,
        use_container_width=True,
        hide_index=True
    )
    
    # Download button for the table
    csv = df_table.to_csv(index=False).encode('utf-8')
    st.download_button(
        "Descargar Tabla CSV",
        csv,
        "estadisticas_usuarios.csv",
        "text/csv"
    )
    
    # Additional user-specific analyses
    st.subheader("Análisis Detallado por Usuario")
    
    # Select a user for detailed view
    selected_user = st.selectbox(
        "Seleccionar Usuario para Análisis Detallado",
        options=list(stats.keys())
    )
    
    if selected_user:
        st.subheader(f"Detalles de {selected_user}")
        user_stat = stats[selected_user]
        
        # Display detailed metrics for the selected user
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total de Viajes", user_stat['total_travels'])
            st.metric("Primer Viaje", user_stat['first_travel_date'] or "N/A")
        
        with col2:
            st.metric("Distancia Total", f"{user_stat['total_distance']:.2f} km")
            st.metric("Último Viaje", user_stat['last_travel_date'] or "N/A")
        
        with col3:
            st.metric("Velocidad Promedio", f"{user_stat['avg_speed']:.2f} km/h")
            st.metric("Tiempo Total", f"{user_stat['total_duration']:.2f} horas")
        
        # Fetch all travels for this user within the filter dates
        try:
            user_travels = obtain_available_travels(
                _db=db,
                user_email=user_email,
                user_role=user_role,
                filter_users=[selected_user],
                start_date=start_date,
                end_date=end_date
            )
            
            if user_travels:
                st.subheader("Listado de Viajes")
                
                travel_table = []
                for travel_id in user_travels:
                    # Extract date from travel_id (format: email - id - date)
                    parts = travel_id.split(" - ")
                    if len(parts) >= 3:
                        date_str = " - ".join(parts[2:])
                        
                        # Get coordinates to calculate stats
                        coords = obtain_coords_by_id(travel_id, db)
                        
                        if coords and len(coords) > 1:
                            # Calculate distance
                            distance = sum([
                                ((coords[i]['lat'] - coords[i-1]['lat'])**2 + 
                                 (coords[i]['lon'] - coords[i-1]['lon'])**2)**0.5 
                                for i in range(1, len(coords))
                            ]) * 111
                            
                            # Calculate duration if timestamps are available
                            duration = "N/A"
                            speed = "N/A"
                            
                            if ('timestamp' in coords[0] and 'timestamp' in coords[-1] and
                                isinstance(coords[0]['timestamp'], datetime) and 
                                isinstance(coords[-1]['timestamp'], datetime)):
                                
                                time_diff = coords[-1]['timestamp'] - coords[0]['timestamp']
                                duration_hours = time_diff.total_seconds() / 3600
                                duration = f"{duration_hours:.2f}"
                                
                                if duration_hours > 0:
                                    speed = f"{(distance / duration_hours):.2f}"
                            
                            travel_table.append({
                                'Fecha': date_str,
                                'Distancia (km)': f"{distance:.2f}",
                                'Duración (horas)': duration,
                                'Velocidad (km/h)': speed,
                                'Puntos': len(coords)
                            })
                
                if travel_table:
                    st.dataframe(
                        pd.DataFrame(travel_table),
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("No se encontraron detalles de viajes para este usuario")
            
        except Exception as e:
            st.error(f"Error al obtener detalles de viajes: {str(e)}")