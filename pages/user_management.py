import streamlit as st
import pandas as pd

from utils.database import get_user_role

def page_user_management(db, admin_email):
    """
    Page for managing user roles (admin only)
    
    Args:
        db: Firestore client
        admin_email: Email of the admin user
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
    df = pd.DataFrame(user_data)
    
    # Role selection
    roles = ['user', 'monitor', 'admin']
    
    # Editable DataFrame
    st.subheader("Tabla de Usuarios")
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
        num_rows="dynamic"
    )
    
    # Save changes button
    if st.button("Guardar Cambios"):
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
        
    # Display role description
    with st.expander("Descripción de Roles"):
        st.markdown("""
        ### Roles de usuario:
        
        - **Usuario**: Acceso solo a sus propios viajes.
        - **Monitor**: Puede ver los viajes de los usuarios asignados.
        - **Administrador**: Acceso completo a todos los viajes y gestión de usuarios.
        
        Los monitores deben ser asignados a usuarios específicos en la columna "Monitor Asignado".
        """)