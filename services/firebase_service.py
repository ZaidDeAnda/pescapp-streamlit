import firebase_admin
from firebase_admin import credentials, firestore
from config.firebase_config import get_firebase_config, CREDENTIALS_PATH
import streamlit as st
import os

def initialize_firebase():
    """Inicializar Firebase con credenciales del entorno o archivo"""
    if not firebase_admin._apps:
        try:
            firebase_config = get_firebase_config()
            
            # Intentar usar credenciales del archivo
            if os.path.exists(CREDENTIALS_PATH):
                cred = credentials.Certificate(CREDENTIALS_PATH)
                firebase_admin.initialize_app(cred)
                print("✅ Firebase inicializado con credenciales locales")
            else:
                # Intentar usar credenciales del entorno
                cred_dict = {
                    "type": "service_account",
                    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                    "private_key": os.getenv("FIREBASE_PRIVATE_KEY"),
                    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                    "token_uri": "https://oauth2.googleapis.com/token"
                }
                
                if all(cred_dict.values()):
                    cred = credentials.Certificate(cred_dict)
                    firebase_admin.initialize_app(cred)
                    print("✅ Firebase inicializado con credenciales del entorno")
                else:
                    # Inicializar sin credenciales (solo para desarrollo)
                    firebase_admin.initialize_app()
                    print("⚠️ Firebase inicializado sin credenciales. Algunas funciones pueden no estar disponibles.")
        
        except Exception as e:
            print(f"❌ Error al inicializar Firebase: {e}")
            st.error("Error al conectar con Firebase. Verifique sus credenciales.")
            return None
    
    return get_firestore()

# Función para obtener la conexión a Firestore
@st.cache_resource
def get_firestore():
    try:
        return firestore.client()
    except Exception as e:
        print(f"❌ Error al obtener cliente Firestore: {e}")
        return None

# Función para obtener una colección
def get_collection(collection_name):
    db = get_firestore()
    if db:
        return db.collection(collection_name)
    return None

# Función para obtener un documento
def get_document(collection_name, document_id):
    db = get_firestore()
    if db:
        return db.collection(collection_name).document(document_id).get()
    return None

# Función para obtener todos los documentos de una colección
def get_all_documents(collection_name):
    db = get_firestore()
    if db:
        try:
            docs = db.collection(collection_name).stream()
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            print(f"❌ Error al obtener documentos de {collection_name}: {e}")
    return []

# Función para crear/actualizar un documento
def set_document(collection_name, document_id, data):
    db = get_firestore()
    if db:
        try:
            db.collection(collection_name).document(document_id).set(data)
            return True
        except Exception as e:
            print(f"❌ Error al guardar documento en {collection_name}/{document_id}: {e}")
    return False

# Función para eliminar un documento
def delete_document(collection_name, document_id):
    db = get_firestore()
    if db:
        try:
            db.collection(collection_name).document(document_id).delete()
            return True
        except Exception as e:
            print(f"❌ Error al eliminar documento de {collection_name}/{document_id}: {e}")
    return False

# Función para agregar un documento con ID generado
def add_document(collection_name, data):
    db = get_firestore()
    if db:
        try:
            return db.collection(collection_name).add(data)
        except Exception as e:
            print(f"❌ Error al agregar documento a {collection_name}: {e}")
    return None

# Función para realizar consultas
def query_documents(collection_name, field, operation, value):
    db = get_firestore()
    if db:
        try:
            docs = db.collection(collection_name).filter(field, operation, value).stream()
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            print(f"❌ Error al consultar documentos de {collection_name}: {e}")
    return []