import streamlit as st
import pandas as pd
import plotly.express as px

from utils.database import collect_user_statistics
from ui.filters import filter_controls, get_users_to_analyze
from ui.components import create_summary_metrics

def page_general_stats(db, user_role, user_email):
    """
    Page for displaying general statistics across all users
    
    Args:
        db: Firestore client
        user_role: Role of the current user
        user_email: Email of the current user
    """
    st.title("Estadísticas Generales 📊")
    
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
    
    # Display summary metrics
    st.header("Resumen Global")
    create_summary_metrics(stats)
    
    # Create visualization data
    st.header("Gráficos")
    
    # Prepare data for visualizations
    user_trip_data = []
    for email, user_stat in stats.items():
        user_trip_data.append({
            'Usuario': email,
            'Viajes': user_stat['total_travels'],
            'Distancia': user_stat['total_distance'],
            'Duración': user_stat['total_duration'],
            'Velocidad': user_stat['avg_speed']
        })
    
    if user_trip_data:
        df_stats = pd.DataFrame(user_trip_data)
        
        # Create visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Bar chart for number of trips by user
            fig1 = px.bar(
                df_stats, 
                x='Usuario', 
                y='Viajes',
                title='Número de Viajes por Usuario',
                labels={'Usuario': 'Usuario', 'Viajes': 'Número de Viajes'},
                color='Viajes'
            )
            st.plotly_chart(fig1, use_container_width=True)
            
            # Bar chart for average speed
            fig3 = px.bar(
                df_stats,
                x='Usuario',
                y='Velocidad',
                title='Velocidad Promedio por Usuario (km/h)',
                labels={'Usuario': 'Usuario', 'Velocidad': 'Velocidad Promedio (km/h)'},
                color='Velocidad'
            )
            st.plotly_chart(fig3, use_container_width=True)
        
        with col2:
            # Bar chart for total distance by user
            fig2 = px.bar(
                df_stats,
                x='Usuario',
                y='Distancia',
                title='Distancia Total por Usuario (km)',
                labels={'Usuario': 'Usuario', 'Distancia': 'Distancia Total (km)'},
                color='Distancia'
            )
            st.plotly_chart(fig2, use_container_width=True)
            
            # Bar chart for total duration
            fig4 = px.bar(
                df_stats,
                x='Usuario',
                y='Duración',
                title='Tiempo Total por Usuario (horas)',
                labels={'Usuario': 'Usuario', 'Duración': 'Tiempo Total (horas)'},
                color='Duración'
            )
            st.plotly_chart(fig4, use_container_width=True)
        
        # Scatter plot comparing distance vs. duration
        fig5 = px.scatter(
            df_stats,
            x='Distancia',
            y='Duración',
            title='Relación entre Distancia y Tiempo',
            labels={'Distancia': 'Distancia Total (km)', 'Duración': 'Tiempo Total (horas)'},
            color='Usuario',
            size='Viajes',
            hover_data=['Velocidad']
        )
        st.plotly_chart(fig5, use_container_width=True)