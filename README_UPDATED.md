# 🌊 Sistema de Predicción de Tsunamis - Streamlit

## 📁 Estructura del Proyecto

```
streamlit_app/
├── app.py                              # Aplicación principal
├── pages/
│   └── 1_🔴_Monitoreo_Tiempo_Real.py  # Monitoreo USGS en tiempo real
├── requirements.txt                    # Dependencias
├── .streamlit/
│   └── config.toml                    # Configuración de tema
├── README.md                          # Esta documentación
└── DEPLOY.md                          # Guía de despliegue
```

## 🚀 Características

### 📊 Predicción Manual

- Formulario interactivo para análisis de terremotos
- Visualización de riesgo con gauge y métricas
- Ejemplos históricos (Japón 2011, Indonesia 2004, Chile 2010)
- Mapa de ubicación del epicentro
- Recomendaciones según nivel de riesgo

### 🔴 Monitoreo en Tiempo Real

- **Conexión directa a USGS API** para datos reales
- Detección automática de terremotos globales
- Análisis instantáneo de riesgo de tsunami
- Sistema de alertas configurable
- Auto-actualización opcional
- Visualización en mapa interactivo
- Filtrado por magnitud y ventana temporal

### 📈 Análisis Avanzado

- Mapa de calor magnitud-profundidad
- Visualización de patrones de riesgo
- Información educativa del sistema

## 🚀 Inicio Rápido

### Instalación Local

```bash
cd streamlit_app
pip install -r requirements.txt
streamlit run app.py
```

La aplicación se abrirá en `http://localhost:8501`

### Navegación

- **Inicio**: Predicción manual y análisis
- **🔴 Monitoreo Tiempo Real** (menú lateral): Sistema de monitoreo USGS

## 🌐 API USGS

El módulo de monitoreo se conecta a:

```
https://earthquake.usgs.gov/fdsnws/event/1/query
```

**Parámetros configurables:**

- Ventana temporal (10 min - 24 horas)
- Magnitud mínima (2.5 - 7.0)
- Umbral de alerta (10% - 90%)
- Auto-actualización (30 - 300 segundos)

## 📊 Uso del Monitoreo en Tiempo Real

1. **Accede** desde el menú lateral: "🔴 Monitoreo Tiempo Real"
2. **Configura** filtros en la barra lateral:
   - Ventana temporal
   - Magnitud mínima
   - Umbral de alerta
   - Auto-actualización
3. **Visualiza** eventos en 3 pestañas:
   - 🚨 **Alertas Activas**: Eventos con riesgo alto
   - 📊 **Todos los Eventos**: Lista completa
   - 🗺️ **Mapa**: Visualización geográfica
4. **Analiza** cada evento:
   - Datos sísmicos completos
   - Probabilidad de tsunami
   - Nivel de riesgo
   - Recomendaciones
   - Enlace a USGS

## 🔧 Configuración

### Archivos del Modelo

El sistema busca en la carpeta padre:

- `../model.pkl`
- `../scaler.pkl`
- `../features.json`

Para despliegue en cloud, copia estos archivos a `streamlit_app/` y actualiza rutas en el código.

### Personalización

**Umbrales de riesgo** (`pages/1_🔴_Monitoreo_Tiempo_Real.py`):

```python
if probability < 0.2:
    risk_level = "Muy Bajo"
elif probability < 0.4:
    risk_level = "Bajo"
elif probability < 0.6:
    risk_level = "Moderado"
elif probability < 0.8:
    risk_level = "Alto"
else:
    risk_level = "Muy Alto"
```

**Colores de tema** (`.streamlit/config.toml`):

```toml
[theme]
primaryColor = "#2a5298"
backgroundColor = "#ffffff"
```

## 🌍 Datos en Tiempo Real

### Fuente

**USGS Earthquake Hazards Program**

- Datos actualizados continuamente
- Cobertura global
- Información oficial y verificada

### Campos Disponibles

- Magnitud, profundidad, ubicación
- Hora del evento
- Significancia sísmica
- Intensidad percibida (MMI, CDI)
- Metadata adicional

## 🚨 Sistema de Alertas

**Niveles de Alerta:**

- 🔴 **Muy Alto** (≥80%): Evacuación inmediata
- 🟠 **Alto** (60-80%): Preparar evacuación
- 🟡 **Moderado** (40-60%): Mantenerse alerta
- 🟢 **Bajo** (<40%): Vigilancia rutinaria

**Configuración:**
Ajusta el umbral de alerta según necesidades:

- Sistemas de emergencia: 30%
- Uso educativo: 50%
- Alta sensibilidad: 20%

## 📈 Rendimiento

### Optimizaciones

- `@st.cache_resource` para modelo
- Carga diferida de páginas
- Minimización de recargas

### Límites USGS API

- Sin autenticación: ~100 req/hora
- Respeta rate limiting
- Implementa delays entre consultas

## 🐛 Solución de Problemas

### Error de conexión USGS

```
Error al obtener datos de USGS: ...
```

**Solución:**

- Verifica conexión a internet
- USGS API puede estar temporalmente no disponible
- Aumenta timeout en configuración

### Datos faltantes

Algunos terremotos pueden no tener todos los campos (MMI, CDI, etc.).
El sistema usa valores por defecto automáticamente.

### Rendimiento lento

- Reduce ventana temporal
- Aumenta magnitud mínima
- Desactiva auto-actualización

## 🔐 Consideraciones de Seguridad

- No requiere autenticación para USGS (API pública)
- Rate limiting recomendado para producción
- Validación de datos de entrada
- Manejo de errores robusto

## 📝 Diferencias con Sistema Original

### Ventajas Streamlit

✅ Despliegue más rápido  
✅ UI/UX integrada  
✅ Sin backend separado  
✅ Ideal para demos y análisis

### Sistema Original (Flask + API REST)

✅ Mayor escalabilidad  
✅ Integración con otros sistemas  
✅ Mayor control de infraestructura  
✅ Mejor para producción enterprise

## 🤝 Contribuciones

Mejoras posibles:

- Notificaciones push
- Historial de alertas
- Exportación de datos
- Más visualizaciones
- Integración con bases de datos

## 📚 Recursos

- [USGS Earthquake API](https://earthquake.usgs.gov/fdsnws/event/1/)
- [Documentación Streamlit](https://docs.streamlit.io)
- [Streamlit Pages](https://docs.streamlit.io/library/get-started/multipage-apps)

## 📄 Licencia

Parte del Sistema de Predicción de Tsunamis.
