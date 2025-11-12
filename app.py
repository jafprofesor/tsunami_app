import streamlit as st
import pandas as pd
import numpy as np
import joblib
import json
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Predicción de Tsunamis",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cargar modelo y scaler
@st.cache_resource
def load_model():
    """Cargar modelo, scaler y características"""
    try:
        model = joblib.load('model.pkl')
        scaler = joblib.load('scaler.pkl')
        with open('features.json', 'r') as f:
            feature_names = json.load(f)
        return model, scaler, feature_names
    except Exception as e:
        st.error(f"Error al cargar el modelo: {e}")
        return None, None, None

model, scaler, feature_names = load_model()

# Función para calcular proximidad a océanos
def calculate_ocean_proximity(lat, lon):
    """Calcula si está cerca de zonas de riesgo de tsunami"""
    pacific_ring = (
        ((lat > -60) & (lat < 60)) &
        (((lon > 120) & (lon < 180)) | ((lon > -180) & (lon < -60)))
    )
    indian_ocean = ((lat > -45) & (lat < 25)) & ((lon > 40) & (lon < 120))
    caribbean = ((lat > 5) & (lat < 25)) & ((lon > -90) & (lon < -55))
    return int(pacific_ring or indian_ocean or caribbean)

# Función para ingeniería de características
def engineer_features(data):
    """Genera características adicionales"""
    data['ocean_proximity'] = calculate_ocean_proximity(
        data['latitude'], data['longitude']
    )
    data['mag_depth_ratio'] = data['magnitude'] / (data['depth'] + 1)
    data['intensity_score'] = (
        data['magnitude'] * 0.5 +
        data.get('mmi', 0) * 0.3 +
        data.get('sig', 0) / 100 * 0.2
    )
    data['shallow_strong'] = int(
        (data['depth'] < 70) and (data['magnitude'] > 7.5)
    )
    return data

# Función de predicción
def predict_tsunami(earthquake_data):
    """Predice el riesgo de tsunami"""
    if model is None:
        return None
    
    # Ingeniería de características
    processed = engineer_features(earthquake_data.copy())
    
    # Preparar datos para predicción
    X = pd.DataFrame([processed])[feature_names]
    X_scaled = scaler.transform(X)
    
    # Predicción
    probability = model.predict_proba(X_scaled)[0][1]
    prediction = model.predict(X_scaled)[0]
    
    # Determinar nivel de riesgo
    if probability >= 0.7:
        risk_level = "🔴 Alto"
        risk_color = "#dc3545"
    elif probability >= 0.3:
        risk_level = "🟡 Moderado"
        risk_color = "#ffc107"
    else:
        risk_level = "🟢 Bajo"
        risk_color = "#28a745"
    
    # Factores de riesgo
    risk_factors = []
    if earthquake_data['magnitude'] >= 7.5:
        risk_factors.append("⚠️ Magnitud muy alta (≥7.5)")
    if earthquake_data['depth'] < 70:
        risk_factors.append("⚠️ Terremoto superficial (<70km)")
    if processed['ocean_proximity'] == 1:
        risk_factors.append("⚠️ Cerca de zona oceánica de riesgo")
    if earthquake_data.get('mmi', 0) >= 6:
        risk_factors.append("⚠️ Intensidad percibida alta")
    
    return {
        'probability': probability,
        'prediction': prediction,
        'risk_level': risk_level,
        'risk_color': risk_color,
        'risk_factors': risk_factors
    }

# Interfaz principal
st.title("🌊 Sistema de Predicción de Tsunamis")
st.markdown("### Sistema de alerta temprana basado en Machine Learning")

# Sidebar con información
with st.sidebar:
    st.header("ℹ️ Información del Sistema")
    st.markdown("""
    **Modelo:** Gradient Boosting Classifier
    
    **Características:**
    - Magnitud del terremoto
    - Profundidad
    - Ubicación geográfica
    - Intensidad percibida
    - Proximidad oceánica
    
    **Niveles de Riesgo:**
    - 🔴 Alto: ≥70% probabilidad
    - 🟡 Moderado: 30-70%
    - 🟢 Bajo: <30%
    """)
    
    st.divider()
    st.markdown("**Ejemplos Históricos**")
    if st.button("Japón 2011"):
        st.session_state.example = "japan"
    if st.button("Indonesia 2004"):
        st.session_state.example = "indonesia"
    if st.button("Chile 2010"):
        st.session_state.example = "chile"

# Tabs principales
tab1, tab2, tab3, tab4 = st.tabs(["📊 Predicción", "📈 Análisis", "🔴 Monitoreo Tiempo Real", "📚 Información"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Datos del Terremoto")
        
        # Cargar ejemplo si fue seleccionado
        if 'example' in st.session_state:
            if st.session_state.example == "japan":
                magnitude = 9.1
                depth = 29.0
                latitude = 38.322
                longitude = 142.369
                place = "Japón 2011"
            elif st.session_state.example == "indonesia":
                magnitude = 9.1
                depth = 30.0
                latitude = 3.295
                longitude = 95.982
                place = "Indonesia 2004"
            elif st.session_state.example == "chile":
                magnitude = 8.8
                depth = 22.9
                latitude = -35.846
                longitude = -72.719
                place = "Chile 2010"
            del st.session_state.example
        else:
            magnitude = 7.0
            depth = 50.0
            latitude = 0.0
            longitude = 0.0
            place = ""
        
        magnitude = st.number_input(
            "Magnitud",
            min_value=0.0,
            max_value=10.0,
            value=magnitude,
            step=0.1,
            help="Magnitud del terremoto en escala Richter"
        )
        
        depth = st.number_input(
            "Profundidad (km)",
            min_value=0.0,
            max_value=700.0,
            value=depth,
            step=1.0,
            help="Profundidad del epicentro en kilómetros"
        )
        
        latitude = st.number_input(
            "Latitud",
            min_value=-90.0,
            max_value=90.0,
            value=latitude,
            step=0.001,
            format="%.3f",
            help="Latitud del epicentro"
        )
        
        longitude = st.number_input(
            "Longitud",
            min_value=-180.0,
            max_value=180.0,
            value=longitude,
            step=0.001,
            format="%.3f",
            help="Longitud del epicentro"
        )
        
        place = st.text_input(
            "Ubicación (opcional)",
            value=place,
            help="Nombre o descripción del lugar"
        )
        
        col_a, col_b = st.columns(2)
        with col_a:
            cdi = st.number_input("CDI", min_value=0.0, max_value=10.0, value=5.0, step=0.1)
            mmi = st.number_input("MMI", min_value=0.0, max_value=12.0, value=6.0, step=0.1)
        with col_b:
            sig = st.number_input("Significancia", min_value=0, max_value=2000, value=800, step=10)
            nst = st.number_input("Estaciones", min_value=0, max_value=500, value=50, step=1)
        
        col_c, col_d = st.columns(2)
        with col_c:
            dmin = st.number_input("Dmin", min_value=0.0, max_value=20.0, value=1.0, step=0.1)
            gap = st.number_input("Gap", min_value=0.0, max_value=360.0, value=100.0, step=1.0)
        with col_d:
            year = st.number_input("Año", min_value=1900, max_value=2100, value=datetime.now().year, step=1)
            month = st.number_input("Mes", min_value=1, max_value=12, value=datetime.now().month, step=1)
    
    with col2:
        st.subheader("Resultado de la Predicción")
        
        if st.button("🔍 Analizar Riesgo de Tsunami", type="primary", use_container_width=True):
            earthquake_data = {
                'magnitude': magnitude,
                'depth': depth,
                'latitude': latitude,
                'longitude': longitude,
                'cdi': cdi,
                'mmi': mmi,
                'sig': sig,
                'nst': nst,
                'dmin': dmin,
                'gap': gap,
                'Year': year,
                'Month': month,
                'place': place
            }
            
            with st.spinner("Analizando datos sísmicos..."):
                result = predict_tsunami(earthquake_data)
                
                if result:
                    st.markdown(f"### {result['risk_level']}")
                    
                    # Gauge de probabilidad
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=result['probability'] * 100,
                        title={'text': "Probabilidad de Tsunami"},
                        gauge={
                            'axis': {'range': [None, 100]},
                            'bar': {'color': result['risk_color']},
                            'steps': [
                                {'range': [0, 30], 'color': "#d4edda"},
                                {'range': [30, 70], 'color': "#fff3cd"},
                                {'range': [70, 100], 'color': "#f8d7da"}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': 70
                            }
                        }
                    ))
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Factores de riesgo
                    if result['risk_factors']:
                        st.markdown("#### Factores de Riesgo Identificados")
                        for factor in result['risk_factors']:
                            st.warning(factor)
                    else:
                        st.success("✅ No se detectaron factores de riesgo significativos")
                    
                    # Mapa de ubicación
                    st.markdown("#### Ubicación del Epicentro")
                    map_data = pd.DataFrame({
                        'lat': [latitude],
                        'lon': [longitude],
                        'magnitude': [magnitude]
                    })
                    st.map(map_data, zoom=4, use_container_width=True)
                    
                    # Recomendaciones
                    st.markdown("#### Recomendaciones")
                    if result['probability'] >= 0.7:
                        st.error("""
                        **🚨 ALERTA MÁXIMA**
                        - Evacuar zonas costeras inmediatamente
                        - Dirigirse a zonas elevadas
                        - Activar protocolos de emergencia
                        - Mantenerse alejado de la costa
                        """)
                    elif result['probability'] >= 0.3:
                        st.warning("""
                        **⚠️ PRECAUCIÓN**
                        - Estar alerta a información oficial
                        - Preparar plan de evacuación
                        - Monitorear comunicaciones
                        - Evitar zonas costeras bajas
                        """)
                    else:
                        st.info("""
                        **ℹ️ RIESGO BAJO**
                        - Mantener vigilancia rutinaria
                        - No se requieren acciones especiales
                        - Seguir protocolos normales
                        """)

with tab2:
    st.subheader("📈 Análisis de Características")
    
    st.markdown("""
    Esta sección muestra cómo diferentes factores afectan la probabilidad de tsunami.
    """)
    
    # Análisis de magnitud vs profundidad
    st.markdown("#### Relación Magnitud - Profundidad")
    
    mag_range = np.linspace(5, 9, 20)
    depth_range = np.linspace(0, 200, 20)
    
    lat_test = 35.0
    lon_test = 140.0
    
    probs = []
    for mag in mag_range:
        row_probs = []
        for dep in depth_range:
            test_data = {
                'magnitude': mag,
                'depth': dep,
                'latitude': lat_test,
                'longitude': lon_test,
                'cdi': 5.0,
                'mmi': 6.0,
                'sig': 800,
                'nst': 50,
                'dmin': 1.0,
                'gap': 100.0,
                'Year': 2024,
                'Month': 1
            }
            result = predict_tsunami(test_data)
            row_probs.append(result['probability'] * 100 if result else 0)
        probs.append(row_probs)
    
    fig = go.Figure(data=go.Heatmap(
        z=probs,
        x=depth_range,
        y=mag_range,
        colorscale='Reds',
        colorbar=dict(title="Probabilidad (%)")
    ))
    fig.update_layout(
        title="Mapa de Calor: Probabilidad de Tsunami",
        xaxis_title="Profundidad (km)",
        yaxis_title="Magnitud",
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("""
    **Interpretación:**
    - Terremotos superficiales y de alta magnitud tienen mayor probabilidad de generar tsunamis
    - La zona roja indica combinaciones de alto riesgo
    - Terremotos profundos raramente generan tsunamis, independiente de su magnitud
    """)

with tab3:
    st.subheader("� Monitoreo de Terremotos en Tiempo Real")
    st.info("💡 Esta funcionalidad completa está disponible en la página dedicada: **Monitoreo Tiempo Real** en el menú lateral.")
    
    st.markdown("""
    El sistema incluye monitoreo en tiempo real conectado a la API de **USGS (United States Geological Survey)**:
    
    - 🌍 **Datos en vivo** de terremotos globales
    - ⚡ **Análisis automático** de riesgo de tsunami
    - 🚨 **Sistema de alertas** configurable
    - 🗺️ **Visualización** en mapa interactivo
    - 🔄 **Auto-actualización** opcional
    
    **Para acceder:**
    1. Usa el menú lateral izquierdo
    2. Selecciona "🔴 Monitoreo Tiempo Real"
    3. Configura tus preferencias de filtrado y alertas
    
    O ejecuta directamente el módulo de monitoreo desde la línea de comandos para integración con sistemas de alerta.
    """)
    
    if st.button("🔄 Ir a Monitoreo en Tiempo Real", use_container_width=True):
        st.switch_page("pages/1_🔴_Monitoreo_Tiempo_Real.py")

with tab4:
    st.subheader("�📚 Información del Sistema")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### ¿Cómo funciona?
        
        Este sistema utiliza **Machine Learning** para predecir la probabilidad de tsunami 
        basándose en características sísmicas:
        
        1. **Datos de entrada**: Magnitud, profundidad, ubicación, etc.
        2. **Procesamiento**: Ingeniería de características y normalización
        3. **Predicción**: Modelo de Gradient Boosting entrenado con datos históricos
        4. **Resultado**: Probabilidad y nivel de riesgo
        
        #### Características Clave
        
        - **Magnitud**: Energía liberada por el terremoto
        - **Profundidad**: Distancia del epicentro a la superficie
        - **Ubicación**: Coordenadas geográficas
        - **Proximidad oceánica**: Cercanía a zonas de riesgo
        - **Intensidad**: MMI, CDI, significancia
        """)
    
    with col2:
        st.markdown("""
        #### Niveles de Riesgo
        
        **🔴 Riesgo Alto (≥70%)**
        - Alta probabilidad de tsunami
        - Requiere evacuación inmediata
        - Activación de protocolos de emergencia
        
        **🟡 Riesgo Moderado (30-70%)**
        - Probabilidad significativa
        - Mantenerse alerta
        - Preparar plan de evacuación
        
        **🟢 Riesgo Bajo (<30%)**
        - Baja probabilidad de tsunami
        - Vigilancia rutinaria
        - No requiere acciones especiales
        
        #### Datos Históricos
        
        El modelo fue entrenado con datos de terremotos y tsunamis 
        registrados por el USGS y otras fuentes oficiales.
        """)
    
    st.divider()
    
    st.markdown("""
    #### ⚠️ Descargo de Responsabilidad
    
    Este sistema es una herramienta de apoyo para la toma de decisiones y **no reemplaza** 
    los sistemas oficiales de alerta de tsunami. Siempre siga las instrucciones de las 
    autoridades locales y organismos especializados como:
    
    - NOAA (National Oceanic and Atmospheric Administration)
    - PTWC (Pacific Tsunami Warning Center)
    - Servicios geológicos y sismológicos nacionales
    """)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666;'>
    Sistema de Predicción de Tsunamis | Desarrollado con Streamlit y Machine Learning
</div>
""", unsafe_allow_html=True)
