import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from components.auth_class import Authentication
from components.navigation import setup_sidebar, show_header, show_footer
from services.travel_service import get_available_travels, get_user_travels
from components.utils import display_dataframe_with_download

# Configurar la página
st.set_page_config(
    page_title="PescApp - Estadísticos",
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
    "📊 Análisis Estadístico",
    "Análisis y visualización de los datos de viajes registrados."
)

# Función principal
def main():
    # Determinar qué viajes mostrar según el rol del usuario
    role = user.get("role", "user")
    
    if role == "admin":
        st.info("Como administrador, puedes ver los viajes de todos los usuarios.")
        
        view_option = st.radio(
            "Mostrar viajes de:",
            options=["Todos los usuarios", "Solo mis viajes"],
            horizontal=True,
            key="admin_view_option"
        )
        
        if view_option == "Todos los usuarios":
            travels = get_available_travels()
            title = "Análisis de Todos los Viajes"
        else:
            travels = get_user_travels(user.get("id"))
            title = "Análisis de Mis Viajes"
    
    elif role == "monitor":
        st.info("Como monitor, puedes ver tus viajes y los de los usuarios asignados a ti.")
        
        view_option = st.radio(
            "Mostrar viajes de:",
            options=["Todos los disponibles", "Solo mis viajes"],
            horizontal=True,
            key="monitor_view_option"
        )
        
        if view_option == "Todos los disponibles":
            travels = get_available_travels()
            title = "Análisis de Viajes Disponibles"
        else:
            travels = get_user_travels(user.get("id"))
            title = "Análisis de Mis Viajes"
    
    else:
        travels = get_user_travels(user.get("id"))
        title = "Análisis de Mis Viajes"
    
    st.subheader(title)
    
    if not travels:
        st.warning("No hay viajes disponibles para analizar.")
        return
    
    # Convertir a DataFrame para análisis
    df = pd.DataFrame(travels)
    
    # Procesamiento de datos
    if 'timestamp' in df.columns:
        df['date'] = pd.to_datetime(df['timestamp'], errors='coerce')
    
    if 'end_timestamp' in df.columns:
        df['end_date'] = pd.to_datetime(df['end_timestamp'], errors='coerce')
        
        # Calcular duración en horas si no existe el campo 'duration'
        if 'duration' not in df.columns and 'date' in df.columns and 'end_date' in df.columns:
            # Calcular duración en horas
            df['duration'] = (df['end_date'] - df['date']).dt.total_seconds() / 3600
            df['duration'] = df['duration'].apply(lambda x: max(0, x) if pd.notna(x) else np.nan)

    # Asegurar que distancia y velocidad sean numéricas
    for col in ['distance', 'speed']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    if len(df) < 2:
        st.info("Se necesitan al menos 2 viajes para realizar análisis.")
        return

    # Filtros para el análisis
    with st.expander("Filtros de Análisis", expanded=False):
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

    # ------------------- Métricas Principales -------------------
    st.write("### Métricas Principales")
    
    # Crear fila de métricas
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Distancia total recorrida
    with col1:
        if 'distance' in df.columns:
            total_distance = df['distance'].sum()
            if pd.isna(total_distance):
                total_distance = 0
            st.metric(
                label="Distancia Total",
                value=f"{total_distance:.2f} km"
            )
        else:
            st.metric(label="Distancia Total", value="No disponible")
    
    # Distancia promedio por viaje
    with col2:
        if 'distance' in df.columns:
            avg_distance = df['distance'].mean()
            if pd.isna(avg_distance):
                avg_distance = 0
            st.metric(
                label="Distancia Promedio",
                value=f"{avg_distance:.2f} km"
            )
        else:
            st.metric(label="Distancia Promedio", value="No disponible")
    
    # Velocidad máxima
    with col3:
        if 'speed' in df.columns:
            max_speed = df['speed'].max()
            if pd.isna(max_speed):
                max_speed = 0
            st.metric(
                label="Velocidad Máxima",
                value=f"{max_speed:.2f} km/h"
            )
        else:
            st.metric(label="Velocidad Máxima", value="No disponible")
    
    # Velocidad promedio
    with col4:
        if 'speed' in df.columns:
            avg_speed = df['speed'].mean()
            if pd.isna(avg_speed):
                avg_speed = 0
            st.metric(
                label="Velocidad Promedio",
                value=f"{avg_speed:.2f} km/h"
            )
        else:
            st.metric(label="Velocidad Promedio", value="No disponible")
    
    # Total horas recorridas
    with col5:
        if 'duration' in df.columns:
            total_hours = df['duration'].sum()
            if pd.isna(total_hours):
                total_hours = 0
            st.metric(
                label="Total Horas",
                value=f"{total_hours:.2f} h"
            )
        else:
            st.metric(label="Total Horas", value="No disponible")
    
    # ------------------- Visualizaciones detalladas -------------------
    st.write("### Visualizaciones Detalladas")
    
    # Pestañas para diferentes visualizaciones
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Distribución por Tipo", 
        "⏱️ Actividad Temporal",
        "📏 Análisis de Distancia",
        "🚀 Análisis de Velocidad"
    ])
    
    # Tab 1: Distribución por tipo
    with tab1:
        if 'type' in df.columns:
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
        else:
            st.info("No hay datos de tipo de viaje disponibles para visualizar.")
    
    # Tab 2: Actividad temporal
    with tab2:
        if 'date' in df.columns:
            col1, col2 = st.columns(2)
            
            with col1:
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
            
            with col2:
                # Viajes por hora del día
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
                
            # Distribución por día de la semana
            df['weekday'] = df['date'].dt.day_name()
            order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            trips_by_weekday = df.groupby('weekday').size().reset_index(name='count')
            
            # Reordenar los días de la semana
            trips_by_weekday['weekday'] = pd.Categorical(trips_by_weekday['weekday'], categories=order, ordered=True)
            trips_by_weekday = trips_by_weekday.sort_values('weekday')
            
            fig = px.bar(
                trips_by_weekday, 
                x='weekday', 
                y='count',
                title='Distribución de Viajes por Día de la Semana',
                labels={'weekday': 'Día de la Semana', 'count': 'Número de Viajes'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos temporales disponibles para visualizar.")
    
    # Tab 3: Análisis de distancia
    with tab3:
        if 'distance' in df.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                # Histograma de distancias
                fig = px.histogram(
                    df, 
                    x='distance',
                    nbins=20,
                    title='Distribución de Distancias de Viaje',
                    labels={'distance': 'Distancia (km)', 'count': 'Frecuencia'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Si hay tipo de viaje, mostrar distancia promedio por tipo
                if 'type' in df.columns:
                    avg_distance_by_type = df.groupby('type')['distance'].mean().reset_index()
                    avg_distance_by_type.columns = ['Tipo', 'Distancia Promedio']
                    
                    fig = px.bar(
                        avg_distance_by_type, 
                        x='Tipo', 
                        y='Distancia Promedio',
                        title='Distancia Promedio por Tipo de Viaje',
                        labels={'Tipo': 'Tipo de Viaje', 'Distancia Promedio': 'Distancia Promedio (km)'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    # Si hay fecha, mostrar distancia por día de la semana
                    if 'date' in df.columns and 'weekday' in df.columns:
                        avg_distance_by_weekday = df.groupby('weekday')['distance'].mean().reset_index()
                        avg_distance_by_weekday.columns = ['Día de la Semana', 'Distancia Promedio']
                        
                        # Reordenar los días de la semana
                        avg_distance_by_weekday['Día de la Semana'] = pd.Categorical(
                            avg_distance_by_weekday['Día de la Semana'], 
                            categories=order, 
                            ordered=True
                        )
                        avg_distance_by_weekday = avg_distance_by_weekday.sort_values('Día de la Semana')
                        
                        fig = px.bar(
                            avg_distance_by_weekday, 
                            x='Día de la Semana', 
                            y='Distancia Promedio',
                            title='Distancia Promedio por Día de la Semana',
                            labels={'Día de la Semana': 'Día de la Semana', 'Distancia Promedio': 'Distancia Promedio (km)'}
                        )
                        st.plotly_chart(fig, use_container_width=True)
            
            # Si tiene datos de tiempo, mostrar distancia vs. tiempo
            if 'date' in df.columns:
                df_sorted = df.sort_values('date')
                fig = px.scatter(
                    df_sorted, 
                    x='date', 
                    y='distance',
                    title='Evolución de Distancias a lo Largo del Tiempo',
                    labels={'date': 'Fecha', 'distance': 'Distancia (km)'}
                )
                fig.update_traces(mode='lines+markers')
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos de distancia disponibles para visualizar.")
    
    # Tab 4: Análisis de velocidad
    with tab4:
        if 'speed' in df.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                # Histograma de velocidades
                fig = px.histogram(
                    df, 
                    x='speed',
                    nbins=20,
                    title='Distribución de Velocidades',
                    labels={'speed': 'Velocidad (km/h)', 'count': 'Frecuencia'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Si hay tipo de viaje, mostrar velocidad promedio por tipo
                if 'type' in df.columns:
                    avg_speed_by_type = df.groupby('type')['speed'].mean().reset_index()
                    avg_speed_by_type.columns = ['Tipo', 'Velocidad Promedio']
                    
                    fig = px.bar(
                        avg_speed_by_type, 
                        x='Tipo', 
                        y='Velocidad Promedio',
                        title='Velocidad Promedio por Tipo de Viaje',
                        labels={'Tipo': 'Tipo de Viaje', 'Velocidad Promedio': 'Velocidad Promedio (km/h)'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Si hay fecha, mostrar velocidad vs. hora del día
                if 'hour' in df.columns:
                    avg_speed_by_hour = df.groupby('hour')['speed'].mean().reset_index()
                    avg_speed_by_hour.columns = ['Hora', 'Velocidad Promedio']
                    
                    fig = px.line(
                        avg_speed_by_hour, 
                        x='Hora', 
                        y='Velocidad Promedio',
                        title='Velocidad Promedio por Hora del Día',
                        labels={'Hora': 'Hora del Día', 'Velocidad Promedio': 'Velocidad Promedio (km/h)'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            # Relación entre velocidad y distancia
            if 'distance' in df.columns:
                fig = px.scatter(
                    df, 
                    x='distance', 
                    y='speed',
                    title='Relación entre Distancia y Velocidad',
                    labels={'distance': 'Distancia (km)', 'speed': 'Velocidad (km/h)'}
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos de velocidad disponibles para visualizar.")
    
    # Analíticas - por usuario (solo para admin/monitor)
    if 'user_email' in df.columns and (role == 'admin' or role == 'monitor'):
        st.write("### Distribución por Usuario")
        
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
        
        # Si hay datos de distancia, mostrar distancia total por usuario
        if 'distance' in df.columns:
            dist_by_user = df.groupby('user_email')['distance'].sum().reset_index()
            dist_by_user.columns = ['Usuario', 'Distancia Total']
            
            fig = px.bar(
                dist_by_user, 
                x='Usuario', 
                y='Distancia Total',
                title='Distancia Total por Usuario (km)',
                labels={'Usuario': 'Usuario', 'Distancia Total': 'Distancia Total (km)'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # ------------------- Datos Tabulares -------------------
    with st.expander("Ver Datos en Tabla", expanded=False):
        # Seleccionar columnas relevantes
        display_cols = ['travel_id', 'type', 'date']
        
        # Añadir columnas numéricas si existen
        for col in ['distance', 'speed', 'duration']:
            if col in df.columns:
                display_cols.append(col)
        
        # Añadir usuario si está disponible y es admin/monitor
        if 'user_email' in df.columns and (role == 'admin' or role == 'monitor'):
            display_cols.append('user_email')
        
        # Filtrar columnas existentes
        display_cols = [col for col in display_cols if col in df.columns]
        
        # Mostrar tabla
        if display_cols:
            display_dataframe_with_download(
                df[display_cols], 
                filename=f"{title.lower().replace(' ', '_')}.csv"
            )
        else:
            st.info("No hay columnas disponibles para mostrar.")

# Ejecutar la función principal
if __name__ == "__main__":
    main()

# Mostrar pie de página
show_footer()