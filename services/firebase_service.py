import firebase_admin
from firebase_admin import credentials, firestore
from config.firebase_config import get_firebase_config
import streamlit as st

def initialize_firebase():
    """Inicializar Firebase con credenciales de Streamlit secrets"""
    if not firebase_admin._apps:
        try:
            firebase_config = get_firebase_config()
            
            # Usar el archivo temporal de credenciales creado por get_firebase_config
            if firebase_config and "serviceAccount" in firebase_config:
                cred = credentials.Certificate(firebase_config["serviceAccount"])
                firebase_admin.initialize_app(cred)
                print("✅ Firebase inicializado con credenciales de Streamlit secrets")
            else:
                raise Exception("No se encontraron credenciales válidas en Streamlit secrets")
        
        except Exception as e:
            print(f"❌ Error al inicializar Firebase: {e}")
            st.error("Error al conectar con Firebase. Verifique sus credenciales en .streamlit/secrets.toml")
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