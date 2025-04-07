import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore as firebase_firestore
import json
from datetime import datetime, timedelta
from google.cloud import firestore

def load_firebase_creds():
    # Load credentials from Streamlit secrets
    creds = {
        'type': st.secrets['type'],
        'project_id': st.secrets['project_id'],
        'private_key_id': st.secrets['private_key_id'],
        'private_key': st.secrets['private_key'],
        'client_email': st.secrets['client_email'],
        'client_id': st.secrets['client_id'],
        'auth_uri': st.secrets['auth_uri'],
        'token_uri': st.secrets['token_uri'],
        'auth_provider_x509_cert_url': st.secrets['auth_provider_x509_cert_url'],
        'client_x509_cert_url': st.secrets['client_x509_cert_url'],
        'universe_domain': st.secrets['universe_domain'],
    }
    return creds

@st.cache_resource
def obtain_firestore_client():
    """
    Initialize and return a Firestore client using credentials from creds.json
    """
    try:
        # Check if Firebase app is already initialized
        try:
            firebase_admin.get_app()
        except ValueError:
            # If not initialized, load credentials and initialize
            cred = credentials.Certificate("creds.json")
            firebase_admin.initialize_app(cred)
        
        # Return Firestore client
        return firebase_firestore.client()
    except Exception as e:
        st.error(f"Error initializing Firestore client: {e}")
        raise

def get_user_role(db, user_email):
    """
    Retrieve user role from Firestore
    
    Roles:
    - 'admin': Can view all travels
    - 'monitor': Can view assigned group travels
    - 'user': Can only view own travels
    """
    try:
        # Query the users collection to get user role
        user_ref = db.collection('users').where('email', '==', user_email).limit(1)
        users = list(user_ref.stream())
        
        if users:
            user_doc = users[0].to_dict()
            return user_doc.get('role', 'user')
        
        return 'user'  # Default to user role if not found
    except Exception as e:
        st.error(f"Error retrieving user role: {e}")
        return 'user'

def get_monitor_assigned_users(_db, monitor_email):
    """
    Retrieve list of users assigned to a monitor
    """
    try:
        # Query users collection to find users with this monitor assigned
        assigned_users_ref = _db.collection('users').where('assigned_monitor', '==', monitor_email)
        assigned_users = [doc.to_dict()['email'] for doc in assigned_users_ref.stream()]
        return assigned_users
    except Exception as e:
        st.error(f"Error retrieving assigned users: {e}")
        return []

def get_all_users(_db):
    """
    Get all users from Firestore
    """
    try:
        users_ref = _db.collection('users')
        users = list(users_ref.stream())
        return [user.to_dict()['email'] for user in users if 'email' in user.to_dict()]
    except Exception as e:
        st.error(f"Error retrieving users: {e}")
        return []

@st.cache_data
def obtain_available_travels(_db, user_email=None, user_role=None, filter_users=None, start_date=None, end_date=None):
    """
    Fetch available travels based on user role and include user names
    Returns: List of travels formatted as "username - travel_id - date"
    
    Args:
        _db (firestore.Client): Firestore client (leading underscore to prevent hashing)
        user_email (str, optional): Email of the current user
        user_role (str, optional): Role of the current user
        filter_users (list, optional): List of user emails to filter by
        start_date (datetime, optional): Start date for filtering
        end_date (datetime, optional): End date for filtering
    """
    try:
        travels_ref = _db.collection('travels')
        start_date_std = standardize_datetime(start_date) if start_date else None
        end_date_std = standardize_datetime(end_date) if end_date else None
        
        accessible_users = []
        
        if user_role == 'admin':
            if filter_users and "Todos" not in filter_users:
                accessible_users = filter_users
            else:
                accessible_users = get_all_users(_db)
        
        elif user_role == 'monitor':
            assigned_users = get_monitor_assigned_users(_db, user_email)
            
            if filter_users and "Todos" not in filter_users:
                accessible_users = [u for u in filter_users if u in assigned_users]
            else:
                accessible_users = assigned_users
        
        else:
            accessible_users = [user_email]
        

        available_travels = []
        

        for email in accessible_users:
            query = travels_ref.where('user_email', '==', email)
            travels = query.stream()
            
            for travel in travels:
                travel_data = travel.to_dict()
                timestamp = travel_data.get('timestamp')
                timestamp_std = standardize_datetime(timestamp)
                

                if timestamp_std is None:
                    continue

                if start_date_std and timestamp_std < start_date_std:
                    continue
                if end_date_std and timestamp_std > end_date_std:
                    continue
                
                travel_date = timestamp_std.strftime("%Y-%m-%d %H:%M") if timestamp_std else "Unknown Date"
                travel_id = f"{travel_data.get('user_email', 'Unknown')} - {travel.id} - {travel_date}"
                available_travels.append(travel_id)
        
        return sorted(available_travels)
    except Exception as e:
        st.error(f"Error fetching travels: {str(e)}")
        return []

def obtain_coords_by_id(travel_id, db):
    """Get coordinates for a specific travel"""
    try:
        if not travel_id:
            st.error("No se seleccionó ningún viaje")
            return []
            
        # Extract the actual travel ID from the combined string
        actual_id = travel_id.split(' - ')[1]
        
        # Query the coords collection without using order_by to avoid index requirement
        # This is a simpler approach that doesn't require an index
        coords_ref = db.collection('coords').where('trip_id', '==', actual_id)
        coords = coords_ref.stream()
        
        coord_list = []
        for coord in coords:
            coord_data = coord.to_dict()
            if 'timestamp' in coord_data:
                # Handle different timestamp formats
                if isinstance(coord_data['timestamp'], str):
                    try:
                        coord_data['timestamp'] = datetime.strptime(coord_data['timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ")
                    except ValueError:
                        try:
                            coord_data['timestamp'] = datetime.strptime(coord_data['timestamp'], "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            # If all parsing fails, keep as string
                            pass
                elif hasattr(coord_data['timestamp'], 'replace'):
                    coord_data['timestamp'] = coord_data['timestamp'].replace(tzinfo=None)
            coord_list.append(coord_data)
        
        # Sort the coordinates by timestamp after fetching them
        # This moves the sorting to the client side instead of requiring a database index
        coord_list.sort(key=lambda x: x.get('timestamp', 0))
            
        return coord_list
    except Exception as e:
        st.error(f"Error fetching coordinates: {str(e)}")
        return []

def obtain_travel_info(travel_id, db):
    """Get travel information including user details"""
    try:
        if not travel_id:
            return None
            
        actual_id = travel_id.split(' - ')[1]
        travel_doc = db.collection('travels').document(actual_id).get()
        
        if travel_doc.exists:
            return travel_doc.to_dict()
        return None
    except Exception as e:
        st.error(f"Error fetching travel info: {str(e)}")
        return None

def collect_user_statistics(_db, user_emails):
    """
    Collect statistics for specified users
    
    Args:
        _db: Firestore client
        user_emails: List of user emails to analyze
        
    Returns:
        Dictionary with user statistics
    """
    stats = {}
    
    try:
        for email in user_emails:
            # Get all travels for this user
            travels_ref = _db.collection('travels').where('user_email', '==', email)
            travels = list(travels_ref.stream())
            
            # Initialize user stats
            user_stats = {
                'total_travels': len(travels),
                'total_distance': 0,
                'avg_speed': 0,
                'total_duration': 0,
                'first_travel_date': None,
                'last_travel_date': None
            }
            
            total_speed_sum = 0
            speed_count = 0
            
            # Process each travel
            for travel in travels:
                travel_id = f"{email} - {travel.id}"
                coords = obtain_coords_by_id(travel_id, _db)
                
                if coords and len(coords) > 1:
                    # Calculate distance for this travel
                    travel_distance = sum([
                        ((coords[i]['lat'] - coords[i-1]['lat'])**2 + 
                         (coords[i]['lon'] - coords[i-1]['lon'])**2)**0.5 
                        for i in range(1, len(coords))
                    ]) * 111  # Approximate km conversion
                    
                    user_stats['total_distance'] += travel_distance
                    
                    # Get timestamps for duration calculation
                    if coords[0].get('timestamp') and coords[-1].get('timestamp'):
                        if isinstance(coords[0]['timestamp'], datetime) and isinstance(coords[-1]['timestamp'], datetime):
                            travel_duration = (coords[-1]['timestamp'] - coords[0]['timestamp']).total_seconds() / 3600  # hours
                            user_stats['total_duration'] += travel_duration
                            
                            # Calculate average speed
                            if travel_duration > 0:
                                speed = travel_distance / travel_duration
                                total_speed_sum += speed
                                speed_count += 1
                    
                    # Update first and last travel dates
                    travel_dict = travel.to_dict()
                    if 'timestamp' in travel_dict:
                        timestamp = travel_dict['timestamp']
                        
                        # Convert string timestamp to datetime if needed
                        if isinstance(timestamp, str):
                            try:
                                if "UTC" in timestamp:
                                    timestamp = datetime.strptime(timestamp, "%d de marzo de %Y, %H:%M:%S p.m. %Z-%z")
                                else:
                                    timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
                            except ValueError:
                                timestamp = None
                        
                        if timestamp:
                            if user_stats['first_travel_date'] is None or timestamp < user_stats['first_travel_date']:
                                user_stats['first_travel_date'] = timestamp
                            
                            if user_stats['last_travel_date'] is None or timestamp > user_stats['last_travel_date']:
                                user_stats['last_travel_date'] = timestamp
            
            # Calculate average speed across all travels
            if speed_count > 0:
                user_stats['avg_speed'] = total_speed_sum / speed_count
            
            # Format dates and numbers
            if user_stats['first_travel_date']:
                user_stats['first_travel_date'] = user_stats['first_travel_date'].strftime('%Y-%m-%d')
            if user_stats['last_travel_date']:
                user_stats['last_travel_date'] = user_stats['last_travel_date'].strftime('%Y-%m-%d')
            
            user_stats['total_distance'] = round(user_stats['total_distance'], 2)
            user_stats['avg_speed'] = round(user_stats['avg_speed'], 2)
            user_stats['total_duration'] = round(user_stats['total_duration'], 2)
            
            # Add to overall stats
            stats[email] = user_stats
        
        return stats
    except Exception as e:
        st.error(f"Error collecting user statistics: {str(e)}")
        return {}

def manage_user_roles(db, admin_email):
    """
    Function to manage user roles (to be used in a separate admin management page)
    """
    st.title("Gestión de Roles de Usuario")
    
    # Verify admin status
    admin_role = get_user_role(db, admin_email)
    if admin_role != 'admin':
        st.error("Acceso denegado. Solo administradores pueden gestionar roles.")
        return
    
    # Fetch all users
    users_ref = db.collection('users')
    users = list(users_ref.stream())
    
    # Fetch all monitors for assignment dropdown
    monitors = [user.to_dict().get('email', '') for user in users 
                if user.to_dict().get('role', '') == 'monitor']
    
    # Prepare user data for editing
    user_data = []
    for user in users:
        user_dict = user.to_dict()
        user_data.append({
            'id': user.id,
            'email': user_dict.get('email', ''),
            'current_role': user_dict.get('role', 'user'),
            'assigned_monitor': user_dict.get('assigned_monitor', '')
        })
    
    # Create DataFrame for editing
    import pandas as pd
    df = pd.DataFrame(user_data)
    
    # Role selection
    roles = ['user', 'monitor', 'admin']
    
    # Editable DataFrame
    edited_df = st.data_editor(
        df,
        column_config={
            "current_role": st.column_config.SelectboxColumn(
                "Rol",
                options=roles,
                required=True
            ),
            "assigned_monitor": st.column_config.SelectboxColumn(
                "Monitor Asignado",
                options=[""] + monitors,
                help="Email del monitor para usuarios asignados"
            )
        },
        disabled=["email"],
        num_rows="dynamic",
        key="user_management_table"
    )
    
    # Save changes button
    if st.button("Guardar Cambios", key="save_changes_button"):
        for _, row in edited_df.iterrows():
            # Update user role in Firestore
            user_ref = users_ref.document(row['id'])
            update_data = {
                'role': row['current_role']
            }
            
            # Add assigned monitor for user role if selected
            if row['current_role'] == 'user' and row['assigned_monitor']:
                update_data['assigned_monitor'] = row['assigned_monitor']
            
            user_ref.update(update_data)
        
        st.success("Roles de usuario actualizados exitosamente.")

def standardize_datetime(timestamp):
    """
    Convierte diferentes formatos de timestamp a un formato estándar datetime sin zona horaria
    
    Args:
        timestamp: Puede ser un objeto datetime, una cadena con formato de fecha, o None
        
    Returns:
        datetime sin zona horaria o None si no se puede convertir
    """
    if timestamp is None:
        return None
        
    # Si ya es un objeto datetime
    if isinstance(timestamp, datetime):
        # Eliminar información de zona horaria si existe
        return timestamp.replace(tzinfo=None)
        
    # Si es una cadena, intentar diferentes formatos
    if isinstance(timestamp, str):
        formats_to_try = [
            "%Y-%m-%dT%H:%M:%S.%fZ",  # Formato ISO
            "%Y-%m-%d %H:%M:%S",       # Formato estándar
            "%d de %B de %Y, %H:%M:%S %p %Z-%z",  # Formato largo en español con zona
            "%d de %B de %Y, %H:%M:%S %p"         # Formato largo en español
        ]
        
        for format_str in formats_to_try:
            try:
                # Intentar parsear con este formato
                parsed_date = datetime.strptime(timestamp, format_str)
                # Eliminar zona horaria si existe
                return parsed_date.replace(tzinfo=None)
            except ValueError:
                continue
            except Exception:
                # Otros errores, continuar con el siguiente formato
                continue
    
    # Si llegamos aquí, no pudimos convertir
    return None