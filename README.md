# 🌊 Sistema de Predicción de Tsunamis - Streamlit

Implementación simplificada del sistema de predicción de tsunamis para despliegue rápido en Streamlit.

## 🚀 Inicio Rápido

### Instalación Local

1. **Instalar dependencias:**

```bash
pip install -r requirements.txt
```

2. **Ejecutar la aplicación:**

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

## ☁️ Despliegue en Streamlit Cloud

### Opción 1: Desde GitHub

1. Sube esta carpeta a un repositorio de GitHub
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Conecta tu cuenta de GitHub
4. Selecciona el repositorio y la carpeta `streamlit_app`
5. Especifica `app.py` como archivo principal
6. ¡Despliega!

### Opción 2: Configuración Manual

Crea un archivo `config.toml` en la carpeta `.streamlit/` con:

```toml
[theme]
primaryColor = "#2a5298"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[server]
port = 8501
enableCORS = false
enableXsrfProtection = true
```

## 📁 Estructura de Archivos

```
streamlit_app/
├── app.py                  # Aplicación principal de Streamlit
├── requirements.txt        # Dependencias de Python
└── README.md              # Esta documentación
```

## 🎯 Características

### Interfaz Interactiva

- **Entrada de datos**: Formulario intuitivo para datos sísmicos
- **Predicción en tiempo real**: Análisis instantáneo del riesgo
- **Visualizaciones**: Gauge, mapas y gráficos interactivos
- **Ejemplos históricos**: Casos reales precargados (Japón 2011, Indonesia 2004, Chile 2010)

### Análisis Avanzado

- **Mapa de calor**: Relación magnitud-profundidad
- **Factores de riesgo**: Identificación automática de condiciones peligrosas
- **Recomendaciones**: Acciones sugeridas según nivel de riesgo

### Información Educativa

- Explicación del funcionamiento del sistema
- Niveles de riesgo detallados
- Descargo de responsabilidad

## 🔧 Configuración

### Archivos del Modelo

La aplicación busca los archivos del modelo en la carpeta padre:

- `../model.pkl` - Modelo entrenado
- `../scaler.pkl` - Scaler para normalización
- `../features.json` - Lista de características

Si quieres desplegar en Streamlit Cloud, debes:

1. Copiar estos archivos a la carpeta `streamlit_app/`
2. Actualizar las rutas en `app.py`:

```python
model = joblib.load('model.pkl')
scaler = joblib.load('scaler.pkl')
with open('features.json', 'r') as f:
    feature_names = json.load(f)
```

## 📊 Uso

1. **Ingresa los datos del terremoto** en el panel izquierdo
2. **Haz clic en "Analizar Riesgo"** para obtener la predicción
3. **Revisa los resultados**:

   - Probabilidad de tsunami (%)
   - Nivel de riesgo (Alto/Moderado/Bajo)
   - Factores de riesgo identificados
   - Ubicación en el mapa
   - Recomendaciones de seguridad

4. **Prueba los ejemplos históricos** desde la barra lateral

## 🎨 Personalización

### Colores y Tema

Edita la sección de configuración al inicio de `app.py`:

```python
st.set_page_config(
    page_title="Tu Título",
    page_icon="🌊",
    layout="wide"
)
```

### Umbrales de Riesgo

Modifica los umbrales en la función `predict_tsunami()`:

```python
if probability >= 0.7:
    risk_level = "Alto"
elif probability >= 0.3:
    risk_level = "Moderado"
else:
    risk_level = "Bajo"
```

## 🐛 Solución de Problemas

### Error al cargar el modelo

- Verifica que los archivos `model.pkl`, `scaler.pkl` y `features.json` existan
- Comprueba las rutas de los archivos en el código
- Asegúrate de tener las versiones correctas de scikit-learn

### La aplicación no se carga

- Verifica que todas las dependencias estén instaladas
- Comprueba la versión de Python (recomendado: 3.8+)
- Revisa los logs de Streamlit para errores específicos

### Problemas de visualización

- Actualiza Streamlit a la última versión: `pip install --upgrade streamlit`
- Limpia la caché del navegador
- Reinicia la aplicación

## 📝 Notas de Desarrollo

### Diferencias con la API REST

- **Simplicidad**: No requiere backend separado
- **Interactividad**: UI integrada y responsive
- **Despliegue**: Más rápido y sencillo
- **Escalabilidad**: Limitada comparada con API REST

### Cuándo usar Streamlit vs API REST

- **Streamlit**: Demos, prototipos, análisis interactivo, dashboards internos
- **API REST**: Producción, integración con otros sistemas, alta concurrencia

## 🔐 Seguridad

Para despliegue en producción:

1. No expongas claves API directamente en el código
2. Usa Streamlit Secrets para credenciales
3. Implementa rate limiting si es necesario
4. Añade autenticación si manejas datos sensibles

## 📚 Recursos

- [Documentación de Streamlit](https://docs.streamlit.io)
- [Galería de Streamlit](https://streamlit.io/gallery)
- [Foro de la Comunidad](https://discuss.streamlit.io)

## 🤝 Contribuciones

Para mejorar esta implementación:

1. Añade más visualizaciones
2. Implementa caché para mejor rendimiento
3. Agrega más ejemplos históricos
4. Mejora la UX/UI

## 📄 Licencia

Este código es parte del Sistema de Predicción de Tsunamis y sigue la misma licencia del proyecto principal.
