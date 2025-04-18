# PescApp 🌍

PescApp es una aplicación web desarrollada con Streamlit para el rastreo y visualización de viajes de pesca, diseñada para promover la trazabilidad pesquera y proporcionar información valiosa para la toma de decisiones.

## 📋 Descripción

Este es un proyecto académico desarrollado por investigadores de ECOSUR y UABC con financiamiento de CCyTET. La aplicación está diseñada para:
- Rastrear y visualizar viajes de pesca
- Promover la trazabilidad pesquera
- Proporcionar herramientas de análisis y visualización de datos

## 🚀 Características Principales

- 🗺️ Mapa interactivo para visualización de viajes
- 📊 Análisis estadístico de datos pesqueros
- ☁️ Información climática
- 👥 Gestión de usuarios y perfiles
- 🔒 Sistema de autenticación seguro

## 💻 Requisitos Previos

- Python 3.11 o superior
- pip (gestor de paquetes de Python)
- Cuenta de Firebase (para autenticación y almacenamiento)

## 🛠️ Instalación

1. Clonar el repositorio:
```bash
git clone [URL-del-repositorio]
cd pescapp-streamlit
```

2. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

3. Configurar las variables de entorno:
   - Crear un archivo `.env` en la raíz del proyecto
   - Añadir las credenciales necesarias de Firebase

4. Ejecutar la aplicación:
```bash
streamlit run Pescapp.py
```

## 📁 Estructura del Proyecto

```
pescapp-streamlit/
├── assets/                 # Recursos estáticos (imágenes, logos)
├── components/            # Componentes reutilizables
├── config/               # Configuraciones
├── docs/                 # Documentación
├── models/              # Modelos de datos
├── pages/               # Páginas de la aplicación
├── services/            # Servicios (Firebase, autenticación)
├── Pescapp.py          # Archivo principal
├── requirements.txt    # Dependencias
└── README.md
```

## 👥 Equipo

Este proyecto es mantenido por investigadores de:
- ECOSUR (El Colegio de la Frontera Sur)
- UABC (Universidad Autónoma de Baja California)
- MLcats

## 📞 Soporte

Para soporte técnico, contactar a:
- Email: cavieses@uabcs.mx

## ⚠️ Aviso Legal

Esta aplicación es un proyecto académico desarrollado con fines de investigación y demostración. No debe considerarse como una herramienta de seguridad o sistema de auxilio en tiempo real. ECOSUR y UABC proporcionan esta plataforma en su estado actual, sin garantías específicas sobre su funcionamiento o precisión.

## 📄 Licencia

[Especificar tipo de licencia]

---
Desarrollado con ❤️ por el equipo de PescApp