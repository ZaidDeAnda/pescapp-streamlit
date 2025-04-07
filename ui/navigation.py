import streamlit as st

def navigation():
    """
    Sidebar navigation for the app
    
    Returns:
        str: The name of the selected page
    """
    st.sidebar.title("Navegación")
    page = st.sidebar.radio(
        "Seleccionar Página",
        ["Mapa de Viajes", "Estadísticas Generales", "Estadísticas por Usuario"]
    )
    return page