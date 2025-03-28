import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json
from datetime import datetime

def load_firebase_creds():
    creds = {
        'type' : st.secrets['creds']['type'],
        'project_id' : st.secrets['creds']['project_id'],
        'private_key_id' : st.secrets['creds']['private_key_id'],
        'private_key' : st.secrets['creds']['private_key'],
        'client_email' : st.secrets['creds']['client_email'],
        'client_id' : st.secrets['creds']['client_id'],
        'auth_uri' : st.secrets['creds']['auth_uri'],
        'token_uri' : st.secrets['creds']['token_uri'],
        'auth_provider_x509_cert_url' : st.secrets['creds']['auth_provider_x509_cert_url'],
        'client_x509_cert_url' : st.secrets['creds']['client_x509_cert_url'],
        'universe_domain' : st.secrets['creds']['universe_domain'],
    }

    return creds


@st.cache_resource
def obtain_firestore_client():
    cred = credentials.Certificate(load_firebase_creds())
    firebase_admin.initialize_app(cred)

    db = firestore.client()

    return db

@st.cache_data
def obtain_available_travels(_db):
    available_travels = []

    for doc in _db.collection('travels').list_documents():
        travel_info = doc.get().to_dict()
        
        # Obtener el ID del viaje
        travel_id = str(travel_info.get('travel_id', 'Sin ID'))
        
        # Manejar el timestamp de manera robusta
        timestamp = travel_info.get('timestamp')
        formatted_date = "Fecha desconocida"
        
        if timestamp:
            try:
                # Si es un objeto datetime de Python o de Firestore
                if hasattr(timestamp, 'strftime'):
                    formatted_date = timestamp.strftime('%m/%d/%Y')
                # Si es una cadena ISO formato
                elif isinstance(timestamp, str) and 'T' in timestamp:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    formatted_date = dt.strftime('%m/%d/%Y')
                # Si es otro formato de texto
                elif isinstance(timestamp, str):
                    # Intentar varios formatos comunes
                    for fmt in ['%d de %B de %Y, %I:%M:%S %p', '%Y-%m-%d %H:%M:%S']:
                        try:
                            # Para formato con meses en español
                            spanish_months = {
                                'enero': 'January', 'febrero': 'February', 'marzo': 'March',
                                'abril': 'April', 'mayo': 'May', 'junio': 'June',
                                'julio': 'July', 'agosto': 'August', 'septiembre': 'September',
                                'octubre': 'October', 'noviembre': 'November', 'diciembre': 'December'
                            }
                            
                            timestamp_str = timestamp
                            for es_month, en_month in spanish_months.items():
                                timestamp_str = timestamp_str.replace(es_month, en_month)
                                
                            dt = datetime.strptime(timestamp_str, fmt)
                            formatted_date = dt.strftime('%m/%d/%Y')
                            break
                        except ValueError:
                            continue
            except Exception as e:
                # Si hay cualquier error, usar el timestamp como cadena
                formatted_date = str(timestamp)[:10]
                
        # Formatear la entrada
        available_travels.append(f"{travel_id}|{formatted_date}")

    return available_travels

def obtain_coords_by_id(travel_id, db):
    coord_list = []

    for item in db.collection('coords').where('travel_id', '==', travel_id.split('|')[0]).order_by('timestamp', 'DESCENDING').get():
        coord_list.append(item.to_dict()['coords'])

    return coord_list