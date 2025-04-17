import streamlit as st
import pandas as pd
import plotly.express as px
from components.auth_class import Authentication
from components.navigation import setup_sidebar, show_header, show_footer
from services.travel_service import get_available_travels, get_user_travels
from components.map_components import travel_map_component
from components.utils import format_date, display_dataframe_with_download

# Configurar la página
st.set_page_config(
    page_title="Travel Tracker - Mis Viajes",
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

# Obtener información del usuario
user = auth.get_current_user()

# Mostrar header
show_header(
    "📊 Mis Viajes",
    "Consulta y analiza todos tus viajes registrados."
)

# Función principal
def main():
    # Determinar qué viajes mostrar según el rol del usuario
    role = user.get("role", "user")
    
    if role == "admin":
        # Admin puede ver todos los viajes o filtrar por usuario
        st.info("Como administrador, puedes ver los viajes de todos los usuarios.")
        
        # Opción para ver todos los viajes o solo los propios
        view_option = st.radio(
            "Mostrar viajes de:",
            options=["Todos los usuarios", "Solo mis viajes"],
            horizontal=True,
            key="admin_view_option"
        )
        
        if view_option == "Todos los usuarios":
            travels = get_available_travels()
            title = "Todos los Viajes"
        else:
            travels = get_user_travels(user.get("id"))
            title = "Mis Viajes"
    
    elif role == "monitor":
        # Monitor puede ver sus viajes y los de usuarios asignados
        st.info("Como monitor, puedes ver tus viajes y los de los usuarios asignados a ti.")
        
        # Opción para ver todos los viajes disponibles o solo los propios
        view_option = st.radio(
            "Mostrar viajes de:",
            options=["Todos los disponibles", "Solo mis viajes"],
            horizontal=True,
            key="monitor_view_option"
        )
        
        if view_option == "Todos los disponibles":
            travels = get_available_travels()
            title = "Viajes Disponibles"
        else:
            travels = get_user_travels(user.get("id"))
            title = "Mis Viajes"
    
    else:
        # Usuario normal solo ve sus propios viajes
        travels = get_user_travels(user.get("id"))
        title = "Mis Viajes"
    
    # Mostrar viajes
    st.subheader(title)
    
    if not travels:
        st.warning("No hay viajes disponibles para mostrar.")
        return
    
    # Convertir a DataFrame para análisis
    df = pd.DataFrame(travels)
    
    # Procesamiento de datos
    # Asegurarse de que las columnas necesarias existen
    if 'timestamp' in df.columns:
        # Convertir timestamp a datetime
        df['date'] = pd.to_datetime(df['timestamp'], errors='coerce')
    
    # Visualización principal - Tabla de viajes
    tab1, tab2, tab3 = st.tabs(["📋 Tabla de Viajes", "📈 Análisis", "🗺️ Mapa"])
    
    with tab1:
        # Seleccionar columnas para mostrar
        available_columns = df.columns.tolist()
        default_columns = [col for col in ['travel_id', 'type', 'timestamp', 'user_email'] 
                          if col in available_columns]
        
        # Si hay demasiadas columnas, permitir al usuario seleccionar
        if len(available_columns) > 6:
            selected_columns = st.multiselect(
                "Selecciona las columnas a mostrar:",
                options=available_columns,
                default=default_columns
            )
        else:
            selected_columns = default_columns
        
        # Mostrar tabla con columnas seleccionadas
        if selected_columns:
            # Filtros adicionales
            with st.expander("Filtros", expanded=False):
                # Filtro por tipo de viaje si está disponible
                if 'type' in df.columns:
                    types = df['type'].unique().tolist()
                    selected_types = st.multiselect(
                        "Tipo de viaje:",
                        options=['Todos'] + types,
                        default='Todos'
                    )
                    
                    if 'Todos' not in selected_types and selected_types:
                        df = df[df['type'].isin(selected_types)]
                
                # Filtro por fecha si está disponible
                if 'date' in df.columns:
                    min_date = df['date'].min()
                    max_date = df['date'].max()
                    
                    if pd.notna(min_date) and pd.notna(max_date):
                        date_range = st.date_input(
                            "Rango de fechas:",
                            value=[min_date.date(), max_date.date()],
                            min_value=min_date.date(),
                            max_value=max_date.date()
                        )
                        
                        if len(date_range) == 2:
                            start_date, end_date = date_range
                            df = df[(df['date'].dt.date >= start_date) & 
                                     (df['date'].dt.date <= end_date)]
            
            # Mostrar DataFrame con opciones de descarga
            display_dataframe_with_download(
                df[selected_columns], 
                filename=f"{title.lower().replace(' ', '_')}.csv"
            )
        else:
            st.info("Selecciona al menos una columna para mostrar.")
    
    with tab2:
        st.subheader("Análisis de Viajes")
        
        if len(df) < 2:
            st.info("Se necesitan al menos 2 viajes para realizar análisis.")
            return
        
        # Analíticas - conteo por tipo
        if 'type' in df.columns:
            st.write("#### Distribución por Tipo de Viaje")
            
            # Contar viajes por tipo
            type_counts = df['type'].value_counts().reset_index()
            type_counts.columns = ['Tipo', 'Cantidad']
            
            # Crear gráfico
            fig = px.pie(
                type_counts, 
                values='Cantidad', 
                names='Tipo',
                title='Distribución de Viajes por Tipo',
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Analíticas - viajes por tiempo
        if 'date' in df.columns:
            st.write("#### Actividad de Viajes por Tiempo")
            
            # Agrupar por día
            df['day'] = df['date'].dt.date
            trips_by_day = df.groupby('day').size().reset_index(name='count')
            
            # Crear gráfico
            fig = px.line(
                trips_by_day, 
                x='day', 
                y='count',
                title='Número de Viajes por Día',
                labels={'day': 'Fecha', 'count': 'Número de Viajes'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Viajes por hora del día
            if 'date' in df.columns:
                df['hour'] = df['date'].dt.hour
                trips_by_hour = df.groupby('hour').size().reset_index(name='count')
                
                fig = px.bar(
                    trips_by_hour, 
                    x='hour', 
                    y='count',
                    title='Distribución de Viajes por Hora del Día',
                    labels={'hour': 'Hora', 'count': 'Número de Viajes'}
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Analíticas - por usuario (solo para admin/monitor)
        if 'user_email' in df.columns and (role == 'admin' or role == 'monitor'):
            st.write("#### Distribución por Usuario")
            
            # Contar viajes por usuario
            user_counts = df['user_email'].value_counts().reset_index()
            user_counts.columns = ['Usuario', 'Cantidad']
            
            # Crear gráfico
            fig = px.bar(
                user_counts, 
                x='Usuario', 
                y='Cantidad',
                title='Número de Viajes por Usuario',
                labels={'Usuario': 'Usuario', 'Cantidad': 'Número de Viajes'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Mapa de Viajes")
        
        # Mostrar mapa específico para estos viajes
        travel_map_component()

# Ejecutar la función principal
if __name__ == "__main__":
    main()

# Mostrar pie de página
show_footer()