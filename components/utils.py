import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# Función para formatear fechas
def format_date(date_str, input_format=None, output_format="%d/%m/%Y %H:%M:%S"):
    try:
        if not date_str:
            return ""
        
        # Manejar objetos de Firestore DatetimeWithNanoseconds
        if hasattr(date_str, 'seconds'):
            # Convertir a datetime de Python
            date_obj = datetime.fromtimestamp(date_str.seconds)
            return date_obj.strftime(output_format)
        
        # Si la fecha ya está en formato "día de mes de año, hora UTC"
        if isinstance(date_str, str) and "de" in date_str and "," in date_str:
            # Extraer la información de la fecha
            parts = date_str.split(",")
            date_part = parts[0].strip()
            time_part = parts[1].strip() if len(parts) > 1 else ""
            
            # Parsear la fecha en español
            day, month_year = date_part.split("de", 1)
            month, year = month_year.strip().split("de")
            
            # Construir la fecha
            day = day.strip()
            month = month.strip().lower()
            year = year.strip()
            
            # Mapeo de nombres de meses en español a números
            month_map = {
                "enero": "01", "febrero": "02", "marzo": "03", "abril": "04",
                "mayo": "05", "junio": "06", "julio": "07", "agosto": "08",
                "septiembre": "09", "octubre": "10", "noviembre": "11", "diciembre": "12"
            }
            
            # Convertir el mes a número
            month_num = month_map.get(month.lower(), "01")
            
            # Parsear la hora
            hour_parts = time_part.split("UTC")
            time = hour_parts[0].strip()
            
            # Construir el string de fecha+hora
            date_string = f"{day}/{month_num}/{year} {time}"
            
            # Parsear a datetime
            date_obj = datetime.strptime(date_string, "%d/%m/%Y %I:%M:%S%p")
        else:
            # Si es un objeto datetime, usarlo directamente
            if isinstance(date_str, datetime):
                date_obj = date_str
            else:
                # Si se proporciona un formato de entrada, usarlo
                if input_format:
                    date_obj = datetime.strptime(date_str, input_format)
                else:
                    # Intentar detectar el formato automáticamente
                    for fmt in ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M:%S"]:
                        try:
                            date_obj = datetime.strptime(date_str, fmt)
                            break
                        except (ValueError, TypeError):
                            continue
                    else:
                        # Si no se puede parsear, devolver la cadena original
                        return date_str
        
        # Formatear la fecha al formato de salida
        return date_obj.strftime(output_format)
    except Exception as e:
        # En caso de error, devolver la cadena original
        return date_str

# Función para convertir coordenadas a formato legible
def format_coordinates(lat, lon):
    try:
        # Convertir a float si son strings
        lat = float(lat)
        lon = float(lon)
        
        # Determinar si es norte/sur, este/oeste
        lat_dir = "N" if lat >= 0 else "S"
        lon_dir = "E" if lon >= 0 else "W"
        
        # Tomar valor absoluto
        lat = abs(lat)
        lon = abs(lon)
        
        # Formatear con 6 decimales
        return f"{lat:.6f}° {lat_dir}, {lon:.6f}° {lon_dir}"
    except:
        return f"{lat}, {lon}"

# Función para mostrar un mensaje de éxito/error con autodesaparición
def flash_message(message, type="info", duration=3):
    if type == "success":
        placeholder = st.success(message)
    elif type == "error":
        placeholder = st.error(message)
    elif type == "warning":
        placeholder = st.warning(message)
    else:
        placeholder = st.info(message)
    
    # Usar JavaScript para eliminar el mensaje después de 'duration' segundos
    js = f"""
    <script>
    setTimeout(function() {{
        const elements = window.parent.document.querySelectorAll('.stAlert');
        if (elements.length > 0) {{
            elements[0].style.display = 'none';
        }}
    }}, {duration * 1000});
    </script>
    """
    st.markdown(js, unsafe_allow_html=True)

# Función para convertir datos a DataFrame
def convert_to_dataframe(data_list):
    if not data_list:
        return pd.DataFrame()
    
    # Crear DataFrame
    df = pd.DataFrame(data_list)
    
    # Procesar fechas
    date_columns = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
    for col in date_columns:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: format_date(x) if x else "")
    
    return df

# Función para mostrar un DataFrame con opciones de descarga
def display_dataframe_with_download(df, filename="data.csv"):
    # Mostrar el DataFrame
    st.dataframe(df)
    
    # Botón para descargar como CSV
    if not df.empty:
        csv = df.to_csv(index=False)
        st.download_button(
            label="Descargar como CSV",
            data=csv,
            file_name=filename,
            mime='text/csv',
        )