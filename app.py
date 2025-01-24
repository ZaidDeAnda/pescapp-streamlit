import json

import streamlit as st
import folium
from streamlit_folium import st_folium

from utils.database import obtain_firestore_client, obtain_available_travels, obtain_coords_by_id

st.header("Pescapp 🎣🐟🐠🐡🦈")

db = obtain_firestore_client()

available_travels = obtain_available_travels(db)

seleccion_dia = st.selectbox("Escoge la ruta de interés", available_travels)

coord_list = obtain_coords_by_id(seleccion_dia, db)

# Crear un mapa centrado en el primer punto
inicio = coord_list[0]
mapa = folium.Map(location=[inicio["lat"], inicio["lon"]], zoom_start=13)

icon_image = "assets/Elipse.png"

# Añadir los puntos y las líneas al mapa
coordenadas = []
for i, coord_dict in enumerate(coord_list, start=1):
    coord = [coord_dict["lat"], coord_dict["lon"]]
    coordenadas.append(coord)
    offsetx=-0.0005
    offsety=0.0005
    icon = folium.CustomIcon(
        icon_image,
        icon_size=(20, 20),
        icon_anchor=(20, 20),
    )
    folium.Marker(
        location=[coord[0]+offsetx, coord[1]+offsety],
        popup=f"Punto {i}",
        icon=icon
    ).add_to(mapa)

# Añadir líneas que conecten los puntos
folium.PolyLine(coordenadas, color="blue", weight=2.5, opacity=1).add_to(mapa)

# Mostrar el mapa en Streamlit
st.components.v1.html(
        mapa.get_root()._repr_html_(), height=500,
    )

