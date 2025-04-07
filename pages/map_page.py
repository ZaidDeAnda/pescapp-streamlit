import streamlit as st
import folium
from streamlit_folium import st_folium

from utils.database import obtain_available_travels, obtain_coords_by_id, obtain_travel_info
from ui.filters import filter_controls
from ui.components import display_travel_stats

def create_multi_route_map(all_route_data, selected_route=None, height=500):
    """
    Create an interactive map with multiple routes
    
    Args:
        all_route_data: Dictionary mapping travel_id to coord_list
        selected_route: Currently selected route ID for highlighting
        height: Height of the map in pixels
        
    Returns:
        folium.Map: The created map with multiple routes
    """
    if not all_route_data:
        st.warning("No hay rutas disponibles para mostrar")
        return None
    
    # Find center point for map (use first point of first route)
    center_coords = None
    for route_id, coords in all_route_data.items():
        if coords and len(coords) > 0:
            first_coord = coords[0]
            lat = first_coord.get("lat", first_coord.get("latitude", 0))
            lon = first_coord.get("lon", first_coord.get("lng", first_coord.get("longitude", 0)))
            center_coords = [lat, lon]
            break
    
    if not center_coords:
        st.warning("No se pudieron determinar las coordenadas del mapa")
        return None
    
    # Create map
    mapa = folium.Map(location=center_coords, zoom_start=13)
    
    # Define colors for routes (selected route will be blue, others gray)
    icon_image = "assets/Elipse.png"
    
    # Add each route to the map
    for route_id, coord_list in all_route_data.items():
        if not coord_list or len(coord_list) < 2:
            continue
        
        # Determine if this is the selected route
        is_selected = (route_id == selected_route)
        route_color = "blue" if is_selected else "gray"
        route_weight = 3 if is_selected else 1.5
        route_opacity = 1 if is_selected else 0.7
        
        # Extract coordinates for polyline
        route_coords = []
        for coord_dict in coord_list:
            lat = coord_dict.get("lat", coord_dict.get("latitude", 0))
            lon = coord_dict.get("lon", coord_dict.get("lng", coord_dict.get("longitude", 0)))
            route_coords.append([lat, lon])
        
        # Add polyline for this route
        folium.PolyLine(
            route_coords, 
            color=route_color, 
            weight=route_weight, 
            opacity=route_opacity,
            popup=route_id.split(' - ')[0]  # Show user email as popup
        ).add_to(mapa)
        
        # If this is the selected route, add markers
        if is_selected:
            for i, coord in enumerate(coord_list):
                if i % 10 == 0 or i == len(coord_list) - 1:  # Add markers every 10 points and at the end
                    lat = coord.get("lat", coord.get("latitude", 0))
                    lon = coord.get("lon", coord.get("lng", coord.get("longitude", 0)))
                    
                    # Create custom icon
                    icon = folium.CustomIcon(
                        icon_image,
                        icon_size=(15, 15),
                        icon_anchor=(15, 15),
                    )
                    
                    # Add marker
                    folium.Marker(
                        location=[lat, lon],
                        popup=f"Punto {i+1}",
                        icon=icon
                    ).add_to(mapa)
    
    # Display the map
    return st_folium(mapa, height=height)

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
    
    # Option to show all routes or select specific one
    show_all = st.checkbox("Mostrar todas las rutas", value=True)
    
    seleccion_dia = None
    if not show_all or len(available_travels) == 1:
        seleccion_dia = st.selectbox(
            "Escoge la ruta de interés para destacar",
            available_travels,
            index=0
        )
    
    # Fetch coordinates for all filtered travels
    all_route_data = {}
    
    with st.spinner("Cargando coordenadas de viajes..."):
        for travel_id in available_travels:
            try:
                coords = obtain_coords_by_id(travel_id, db)
                if coords and len(coords) > 0:
                    all_route_data[travel_id] = coords
            except Exception as e:
                st.error(f"Error al obtener coordenadas para {travel_id}: {str(e)}")
    
    if not all_route_data:
        st.warning("No se encontraron coordenadas para los viajes seleccionados")
        return
    
    # Display route count
    st.info(f"Mostrando {len(all_route_data)} rutas en el mapa")
    
    # Display detailed trip information
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Interactive Map with all routes
        st.subheader("Rutas de Viaje")
        map_result = create_multi_route_map(all_route_data, seleccion_dia)
        
        # Show tooltip about the map
        with st.expander("Ayuda del mapa"):
            st.write("""
            - Las rutas grises son todas las rutas disponibles según los filtros aplicados
            - La ruta azul es la ruta seleccionada específicamente (si hay alguna)
            - Puedes hacer zoom y moverte por el mapa para ver mejor las rutas
            - Haz clic en una ruta para ver a qué usuario pertenece
            """)
    
    with col2:
        # Travel Statistics for selected route
        if seleccion_dia:
            st.subheader("Estadísticas del Viaje")
            
            # Get travel info and display statistics
            travel_info = obtain_travel_info(seleccion_dia, db)
            selected_coords = all_route_data.get(seleccion_dia, [])
            display_travel_stats(selected_coords, travel_info)
        else:
            st.info("Selecciona una ruta específica para ver sus estadísticas")