import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la aplicación
APP_NAME = "Travel Tracker"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Una aplicación para rastrear y visualizar viajes"

# Configuración de mapas
DEFAULT_MAP_CENTER = [25.0, -99.0]  # Centro de México por defecto
DEFAULT_MAP_ZOOM = 5
MAP_STYLES = {
    "OpenStreetMap": "OpenStreetMap",
    "Stamen Terrain": "Stamen Terrain",
    "Stamen Toner": "Stamen Toner",
    "CartoDB positron": "CartoDB positron",
    "CartoDB dark_matter": "CartoDB dark_matter"
}
DEFAULT_MAP_STYLE = "OpenStreetMap"

# Colores para marcadores de usuario
USER_COLORS = [
    'red', 'blue', 'green', 'purple', 'orange', 'darkred',
    'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue',
    'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen',
    'gray', 'black', 'lightgray'
]

# Roles de usuario
USER_ROLES = ["user", "monitor", "admin"]

# Configuración de la base de datos
DB_COLLECTIONS = {
    "USERS": "users",
    "TRAVELS": "travels",
    "COORDS": "coords",
    "ASSIGNMENTS": "assignments"
}

# Configuración de fechas
DATE_FORMAT = "%d/%m/%Y %H:%M:%S"
DATE_TIMEZONE = "America/Denver"  # UTC-7

# Configuración de la autenticación
AUTH_COOKIE_NAME = "travel_tracker_auth"
AUTH_COOKIE_EXPIRY_DAYS = 30

# Configuración de la interfaz de usuario
UI_THEME = "light"  # "light", "dark", "system"
UI_SIDEBAR_STATE = "expanded"  # "expanded", "collapsed", "auto"
UI_PAGE_LAYOUT = "wide"  # "wide", "centered"

# Configuración de caché
CACHE_TTL_SECONDS = 300  # 5 minutos

# Mensajes de la aplicación
MESSAGES = {
    "login_required": "Debe iniciar sesión para acceder a esta página.",
    "login_success": "Inicio de sesión exitoso.",
    "login_error": "Error de inicio de sesión. Verifique sus credenciales.",
    "logout_success": "Sesión cerrada exitosamente.",
    "access_denied": "No tiene permisos para acceder a esta página.",
    "no_data": "No hay datos disponibles para mostrar.",
    "no_travels": "No hay viajes disponibles para mostrar.",
    "no_users": "No hay usuarios registrados en el sistema.",
    "user_updated": "Usuario actualizado exitosamente.",
    "user_created": "Usuario creado exitosamente.",
    "user_assigned": "Usuario asignado exitosamente.",
    "password_changed": "Contraseña cambiada exitosamente."
}

# Obtener configuraciones del entorno
def get_env_var(var_name, default_value=None):
    """Obtener variable de entorno con valor predeterminado"""
    return os.environ.get(var_name, default_value)

# Configuraciones específicas del entorno
ENVIRONMENT = get_env_var("ENVIRONMENT", "development")
DEBUG = ENVIRONMENT == "development"