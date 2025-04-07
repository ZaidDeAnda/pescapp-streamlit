import streamlit as st

from utils.database import obtain_available_travels, obtain_coords_by_id, obtain_travel_info
from ui.filters import filter_controls
from ui.components import create_map, display_travel_stats

def page_map(db, user_role, user_email):
    """
    Page for displaying travel maps with filters
    
    Args:
        db: Firestore client
        user_role: Role of the current user
        user_email: Email of the current user
    """
    st.title("Mapa de Viajes 🗺️")
    
    # Get and apply filters
    start_date, end_date, selected_users = filter_controls(db, user_role, user_email)
    
    # Fetch available travels with filters
    try:
        available_travels = obtain_available_travels(
            _db=db, 
            user_email=user_email, 
            user_role=user_role,
            filter_users=selected_users if "Todos" not in selected_users else None,
            start_date=start_date,
            end_date=end_date
        )
    except Exception as e:
        st.error(f"Error al obtener los viajes: {str(e)}")
        return
    
    if not available_travels:
        st.warning("No hay viajes disponibles para mostrar con los filtros seleccionados.")
        return
    
    # Travel selection
    st.subheader("Selección de Viaje")
    seleccion_dia = st.selectbox(
        "Escoge la ruta de interés",
        available_travels,
        index=0
    )
    
    if not seleccion_dia:
        st.warning("Por favor selecciona un viaje")
        return
    
    # Fetch coordinates for the selected travel
    try:
        coord_list = obtain_coords_by_id(seleccion_dia, db)
        # Debug information
        st.write(f"Travel ID: {seleccion_dia.split(' - ')[1]}")
        st.write(f"Number of coordinates found: {len(coord_list)}")
        if coord_list and len(coord_list) > 0:
            st.write("Sample coordinate data keys:", list(coord_list[0].keys()))
    except Exception as e:
        st.error(f"Error al obtener coordenadas: {str(e)}")
        return
    
    if not coord_list:
        st.warning(f"No se encontraron coordenadas para el viaje: {seleccion_dia}")
        return
    
    # Display detailed trip information
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Interactive Map
        st.subheader("Ruta del Viaje")
        create_map(coord_list)
    
    with col2:
        # Travel Statistics
        st.subheader("Estadísticas del Viaje")
        
        # Get travel info and display statistics
        travel_info = obtain_travel_info(seleccion_dia, db)
        display_travel_stats(coord_list, travel_info)