import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json

def load_firebase_creds():
    creds = {
        'type' : st.secrets['type'],
        'project_id' : st.secrets['project_id'],
        'private_key_id' : st.secrets['private_key_id'],
        'private_key' : st.secrets['private_key'],
        'client_email' : st.secrets['client_email'],
        'client_id' : st.secrets['client_id'],
        'auth_uri' : st.secrets['auth_uri'],
        'token_uri' : st.secrets['token_uri'],
        'auth_provider_x509_cert_url' : st.secrets['auth_provider_x509_cert_url'],
        'client_x509_cert_url' : st.secrets['client_x509_cert_url'],
        'universe_domain' : st.secrets['universe_domain'],
    }

    return creds


@st.cache_resource
def obtain_firestore_client():
    cred = credentials.Certificate(load_firebase_creds)
    firebase_admin.initialize_app(cred)

    db = firestore.client()

    return db

@st.cache_data
def obtain_available_travels(_db):
    available_travels = []

    for doc in _db.collection('travels').list_documents():
        travel_info = doc.get().to_dict()
        available_travels.append(str(travel_info['travel_id']) + '|' + travel_info['timestamp'].strftime('%m/%d/%Y'))

    return available_travels

def obtain_coords_by_id(travel_id, db):
    coord_list = []

    for item in db.collection('coords').where('travel_id', '==', travel_id.split('|')[0]).order_by('timestamp', 'DESCENDING').get():
        coord_list.append(item.to_dict()['coords'])

    return coord_list