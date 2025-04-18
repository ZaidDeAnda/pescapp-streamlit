import streamlit as st
from components.auth_class import Authentication
from components.navigation import setup_sidebar, show_header, show_footer
from components.map_components import create_travel_map, validate_coordinates
from services.get_data_utils import (
    load_coords, load_travels, load_users,
    filter_data_by_user, filter_by_travel_ids
)
from services.travel_service import get_assigned_users
from streamlit_folium import folium_static

# Configurar la página
st.set_page_config(
    page_title="Travel Tracker - Visualizador de Datos",
    page_icon="📊",
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
    "🗺️ Mapa de Coordenadas",
    "Visualización geográfica de coordenadas con filtros relacionales."
)

def main():
    # Obtener información del usuario actual
    current_user = auth.get_current_user()
    user_role = current_user.get('role', 'user')
    user_id = current_user.get('id', '')
    user_email = current_user.get('email', '')
    
    # Inicializar session state
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
        st.session_state.users_df = None
        st.session_state.travels_df = None
        st.session_state.coords_df = None
    
    # Cargar los datos cuando se haga clic en el botón
    if st.button("Cargar Datos", use_container_width=True):
        with st.spinner("Cargando datos..."):
            # Obtener usuarios disponibles según el rol
            if user_role == 'admin':
                users_df = load_users(limit=2000)
            elif user_role == 'monitor':
                assigned_users = get_assigned_users(user_id)
                assigned_user_ids = [user['id'] if isinstance(user, dict) else user.id for user in assigned_users]
                assigned_user_ids.append(user_id)
                all_users_df = load_users(limit=2000)
                users_df = all_users_df[all_users_df['user_id'].isin(assigned_user_ids)] if all_users_df is not None else None
            else:
                all_users_df = load_users(limit=2000)
                users_df = all_users_df[all_users_df['user_id'] == user_id] if all_users_df is not None else None
            
            # Cargar viajes y coordenadas
            travels_df = load_travels(limit=2000)
            coords_df = load_coords(limit=2000)
            
            # Filtrar datos según permisos
            if travels_df is not None and users_df is not None:
                available_user_ids = users_df['user_id'].unique().tolist()
                travels_df = travels_df[travels_df['user_id'].isin(available_user_ids)]
                
                if coords_df is not None:
                    available_travel_ids = travels_df['travel_id'].unique().tolist()
                    coords_df = coords_df[coords_df['travel_id'].isin(available_travel_ids)]
            
            # Guardar en session state
            st.session_state.users_df = users_df
            st.session_state.travels_df = travels_df
            st.session_state.coords_df = coords_df
            st.session_state.data_loaded = True
    
    # Mostrar datos si están cargados
    if st.session_state.data_loaded:
        users_df = st.session_state.users_df
        travels_df = st.session_state.travels_df
        coords_df = st.session_state.coords_df
        
        if users_df is None or travels_df is None or coords_df is None:
            st.warning("No se pudieron cargar todos los datos necesarios")
            return
        
        if len(users_df) == 0:
            st.warning("No hay usuarios disponibles según tus permisos.")
            return
        
        # Filtros de usuario
        st.subheader("🔍 Filtro de Usuarios")
        
        if 'email' in users_df.columns:
            user_emails = sorted(users_df['email'].unique().tolist())
            
            # Configurar opciones de selección de usuario
            if user_role == 'user' and len(user_emails) == 1:
                st.write(f"**Usuario seleccionado:** {user_emails[0]}")
                selected_user_option = user_emails[0]
            else:
                user_options = ["Todos los usuarios"] + user_emails if user_role in ['admin', 'monitor'] and len(user_emails) > 1 else user_emails
                selected_user_option = st.selectbox("Filtrar por usuario:", options=user_options, index=0)
            
            # Aplicar filtros de usuario
            filtered_users_df, filtered_travels_df, filtered_coords_df = filter_data_by_user(
                users_df, travels_df, coords_df, selected_user_option
            )
            
            # Filtros de viaje
            if len(filtered_travels_df) > 0 and 'travel_id' in filtered_travels_df.columns:
                st.subheader("🛣️ Filtro de Viajes")
                travel_ids = filtered_travels_df['travel_id'].unique().tolist()
                
                if travel_ids:
                    travel_options = ["Todos los viajes"] + travel_ids
                    selected_travel_ids = st.multiselect(
                        "Seleccionar viajes específicos:",
                        options=travel_options,
                        default=["Todos los viajes"]
                    )
                    
                    # Aplicar filtros de viaje
                    filtered_travels_df, filtered_coords_df = filter_by_travel_ids(
                        filtered_travels_df, filtered_coords_df, selected_travel_ids
                    )
            
            # Mostrar mapa
            if filtered_coords_df is not None:
                st.subheader("🗺️ Mapa de Coordenadas")
                
                # Validar coordenadas
                valid_coords = validate_coordinates(filtered_coords_df)
                
                if valid_coords is None:
                    st.warning("No hay coordenadas válidas para mostrar en el mapa.")
                else:
                    st.write(f"Mostrando {len(valid_coords)} coordenadas en el mapa.")
                    
                    # Crear y mostrar mapa
                    m = create_travel_map(valid_coords)
                    if m is not None:
                        folium_static(m, width=1000, height=600)
                
                # Opción de descarga
                coords_csv = filtered_coords_df.to_csv(index=False)
                st.download_button(
                    label="Descargar Coordenadas como CSV",
                    data=coords_csv,
                    file_name="coordenadas_filtradas.csv",
                    mime="text/csv"
                )
        else:
            st.warning("La columna 'email' no está disponible en la tabla de usuarios para filtrar")
    else:
        st.info("Por favor, haga clic en 'Cargar Datos' para visualizar las coordenadas.")

if __name__ == "__main__":
    main()

# Mostrar pie de página
show_footer()