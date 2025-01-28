<div align='center'>
   <img src='https://github.com/user-attachments/assets/1c540dd9-7824-4921-8872-e1aef2c407b5' width='500px' />
</div>

---

# Pescapp 🎣

Pescapp es una aplicación web construida con Streamlit que visualiza rutas de pesca en un mapa interactivo. La aplicación se conecta a Firebase para obtener y mostrar los datos de las rutas.

## Tecnologías Utilizadas

- Python 3.8+
- Streamlit
- Firebase Admin SDK
- Folium (para visualización de mapas)
- Pandas

## Requisitos Previos

Antes de ejecutar este proyecto, asegúrate de tener:

- Python 3.8 o superior instalado
- Un proyecto de Firebase configurado con Firestore
- Credenciales de Firebase (clave de cuenta de servicio)

## Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/yourusername/pescapp-streamlit.git
cd pescapp-streamlit
```

2. Crea y activa un entorno virtual:

```bash
# En Windows
python -m venv venv
.\venv\Scripts\activate

# En macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Instala las dependencias requeridas:
```bash
pip install -r requirements.txt
```

4. Configura las credenciales de Firebase:
   - Crea un archivo `creds.json` en el directorio raíz
   - Agrega las credenciales de tu cuenta de servicio de Firebase a este archivo

## Ejecución de la Aplicación

Para ejecutar la aplicación localmente:

```bash
streamlit run app.py
```

La aplicación estará disponible en `http://localhost:8501`

## Estructura del Proyecto
```
pescapp-streamlit/
├── app.py # Aplicación principal de Streamlit
├── requirements.txt # Dependencias de Python
├── .gitignore # Archivo de Git ignore
├── README.md # Documentación del proyecto
├── assets/ # Recursos estáticos
│ └── Elipse.png # Icono de marcador del mapa
├── utils/ # Funciones de utilidad
│ └── database.py # Operaciones con la base de datos Firebase
├── .streamlit/ # Configuración de Streamlit
│ └── secrets.toml # Configuración de secretos
└── creds.json # Credenciales de Firebase
```

## Funcionalidades

- Visualización de rutas de pesca en un mapa interactivo
- Selección de diferentes viajes de pesca por fecha
- Visualización de puntos de ruta con marcadores personalizados
- Caminos de rutas mostrados como líneas conectadas
- Integración con Firebase para almacenamiento y recuperación de datos

## Estructura de la Base de Datos Firebase

La aplicación espera las siguientes colecciones en Firestore:

- `travels`: Contiene documentos con información de los viajes
  - Campos: `travel_id`, `timestamp`
- `coords`: Contiene información de coordenadas para cada viaje
  - Campos: `travel_id`, `coords` (con `lat` y `lon`), `timestamp`

## Contribuciones

1. Haz un fork del repositorio
2. Crea tu rama de característica (`git checkout -b feature/AmazingFeature`)
3. Realiza tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Sube la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - consulta el archivo LICENSE para más detalles.
