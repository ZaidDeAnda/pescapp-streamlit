import streamlit as st
import pandas as pd
from components.authentication import require_role
from components.navigation import setup_sidebar, show_header, show_footer
from services.firebase_service import get_all_documents, set_document
from services.auth_service import update_user_role, assign_user_to_monitor, register_user
from components.utils import flash_message

# Configurar la página
st.set_page_config(
    page_title="Travel Tracker - Usuarios",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurar la barra lateral
setup_sidebar()

# Verificar que el usuario es administrador
user = require_role("admin")

# Mostrar header
show_header(
    "👥 Gestión de Usuarios",
    "Administra los usuarios de la aplicación, asigna roles y monitorea la actividad."
)

# Función principal
def main():
    # Obtener todos los usuarios
    users = get_all_documents("users")
    
    if not users:
        st.warning("No hay usuarios registrados en el sistema.")
        
        # Formulario para crear el primer usuario
        with st.form("crear_primer_usuario"):
            st.subheader("Crear Usuario")
            nombre = st.text_input("Nombre completo")
            email = st.text_input("Email")
            rol = st.selectbox("Rol", ["user", "monitor", "admin"])
            password = st.text_input("Contraseña", type="password")
            submitted = st.form_submit_button("Crear Usuario")
            
            if submitted and nombre and email and password:
                success, message = register_user(email, password, nombre, rol)
                if success:
                    st.success(f"Usuario creado exitosamente: {email}")
                    st.rerun()
                else:
                    st.error(f"Error al crear usuario: {message}")
        return
    
    # Convertir a DataFrame para mejor manipulación
    df_users = pd.DataFrame(users)
    
    # Pestañas para diferentes funciones
    tab1, tab2, tab3 = st.tabs(["📋 Lista de Usuarios", "➕ Nuevo Usuario", "🔄 Asignar Monitores"])
    
    with tab1:
        st.subheader("Lista de Usuarios")
        
        # Mostrar tabla de usuarios
        columns_to_show = ["name", "email", "role", "createdAt"]
        available_columns = [col for col in columns_to_show if col in df_users.columns]
        
        if available_columns:
            # Filtros
            with st.expander("Filtros", expanded=False):
                # Filtro por rol
                if "role" in df_users.columns:
                    roles = df_users["role"].unique().tolist()
                    selected_roles = st.multiselect(
                        "Filtrar por rol:",
                        options=["Todos"] + roles,
                        default="Todos"
                    )
                    
                    if "Todos" not in selected_roles and selected_roles:
                        df_filtered = df_users[df_users["role"].isin(selected_roles)]
                    else:
                        df_filtered = df_users
                else:
                    df_filtered = df_users
            
            # Mostrar usuarios
            st.dataframe(
                df_filtered[available_columns],
                use_container_width=True,
                hide_index=True
            )
            
            # Seleccionar usuario para editar
            st.divider()
            st.subheader("Editar Usuario")
            
            # Seleccionar usuario
            user_emails = df_users["email"].tolist()
            selected_user_email = st.selectbox(
                "Seleccionar usuario para editar:",
                options=user_emails
            )
            
            # Obtener datos del usuario seleccionado
            selected_user = df_users[df_users["email"] == selected_user_email].iloc[0]
            
            # Mostrar formulario de edición
            with st.form("editar_usuario"):
                # Campos no editables
                st.text_input("ID", value=selected_user.get("id", ""), disabled=True)
                st.text_input("Email", value=selected_user.get("email", ""), disabled=True)
                
                # Campos editables
                nombre = st.text_input("Nombre", value=selected_user.get("name", ""))
                rol = st.selectbox(
                    "Rol", 
                    options=["user", "monitor", "admin"], 
                    index=["user", "monitor", "admin"].index(selected_user.get("role", "user"))
                )
                
                # Botón de guardar
                submitted = st.form_submit_button("Guardar Cambios")
                
                if submitted:
                    # Actualizar datos
                    user_id = selected_user.get("id")
                    
                    # Actualizar documento en Firestore
                    set_document("users", user_id, {
                        **selected_user,
                        "name": nombre,
                        "role": rol
                    })
                    
                    st.success("Usuario actualizado exitosamente")
                    st.rerun()
    
    with tab2:
        st.subheader("Crear Nuevo Usuario")
        
        # Formulario para crear usuario
        with st.form("crear_usuario"):
            nombre = st.text_input("Nombre completo")
            email = st.text_input("Email")
            rol = st.selectbox("Rol", ["user", "monitor", "admin"])
            password = st.text_input("Contraseña", type="password")
            submitted = st.form_submit_button("Crear Usuario")
            
            if submitted and nombre and email and password:
                success, message = register_user(email, password, nombre, rol)
                if success:
                    st.success(f"Usuario creado exitosamente: {email}")
                    st.rerun()
                else:
                    st.error(f"Error al crear usuario: {message}")
    
    with tab3:
        st.subheader("Asignar Usuarios a Monitores")
        
        # Obtener monitores
        monitores = df_users[df_users["role"] == "monitor"]
        
        if monitores.empty:
            st.warning("No hay monitores registrados en el sistema.")
            return
        
        # Obtener usuarios normales
        usuarios = df_users[df_users["role"] == "user"]
        
        if usuarios.empty:
            st.warning("No hay usuarios normales registrados en el sistema.")
            return
        
        # Seleccionar monitor
        monitor_emails = monitores["email"].tolist()
        selected_monitor_email = st.selectbox(
            "Seleccionar monitor:",
            options=monitor_emails
        )
        
        # Obtener ID del monitor seleccionado
        selected_monitor = monitores[monitores["email"] == selected_monitor_email].iloc[0]
        monitor_id = selected_monitor.get("id")
        
        # Seleccionar usuarios a asignar
        usuario_emails = usuarios["email"].tolist()
        selected_user_emails = st.multiselect(
            "Seleccionar usuarios para asignar al monitor:",
            options=usuario_emails
        )
        
        # Botón para asignar
        if st.button("Asignar Usuarios al Monitor"):
            if not selected_user_emails:
                st.warning("Selecciona al menos un usuario para asignar.")
                return
            
            # Obtener IDs de usuarios seleccionados
            selected_users = usuarios[usuarios["email"].isin(selected_user_emails)]
            user_ids = selected_users["id"].tolist()
            
            # Asignar cada usuario al monitor
            for user_id in user_ids:
                success, message = assign_user_to_monitor(user_id, monitor_id)
                if success:
                    flash_message(f"Usuario asignado: {user_id}", "success")
                else:
                    flash_message(f"Error al asignar usuario {user_id}: {message}", "error")
            
            st.success(f"Se han asignado {len(user_ids)} usuarios al monitor.")

# Ejecutar la función principal
if __name__ == "__main__":
    main()

# Mostrar pie de página
show_footer()