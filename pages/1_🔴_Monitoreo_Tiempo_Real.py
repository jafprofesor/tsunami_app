import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import json
import joblib
import numpy as np

st.set_page_config(
    page_title="Monitoreo en Tiempo Real - Tsunamis",
    page_icon="🔴",
    layout="wide"
)

# Cargar modelo
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

# Función para obtener terremotos de USGS
def fetch_recent_earthquakes(minutes=60, min_magnitude=5.0):
    """Obtener terremotos recientes de USGS API"""
    try:
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=minutes)
        
        params = {
            'format': 'geojson',
            'starttime': start_time.strftime('%Y-%m-%dT%H:%M:%S'),
            'endtime': end_time.strftime('%Y-%m-%dT%H:%M:%S'),
            'minmagnitude': min_magnitude,
            'orderby': 'time-asc'
        }
        
        response = requests.get(
            "https://earthquake.usgs.gov/fdsnws/event/1/query",
            params=params,
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        earthquakes = []
        
        for feature in data.get('features', []):
            props = feature['properties']
            coords = feature['geometry']['coordinates']
            
            earthquake = {
                'id': feature['id'],
                'time': datetime.fromtimestamp(props['time']/1000),
                'magnitude': props['mag'],
                'place': props['place'],
                'longitude': coords[0],
                'latitude': coords[1],
                'depth': coords[2],
                'sig': props.get('sig', 1000),
                'mmi': props.get('mmi', 5),
                'cdi': props.get('cdi', 5),
                'nst': props.get('nst', 50),
                'dmin': props.get('dmin', 1.0),
                'gap': props.get('gap', 100.0),
                'url': props.get('url', ''),
                'tsunami': props.get('tsunami', 0)
            }
            
            earthquakes.append(earthquake)
        
        return earthquakes
        
    except Exception as e:
        st.error(f"Error al obtener datos de USGS: {e}")
        return []

# Función para calcular proximidad oceánica
def calculate_ocean_proximity(lat, lon):
    """Calcula si está cerca de zonas de riesgo de tsunami"""
    pacific_ring = (
        ((lat > -60) and (lat < 60)) and
        (((lon > 120) and (lon < 180)) or ((lon > -180) and (lon < -60)))
    )
    indian_ocean = ((lat > -45) and (lat < 25)) and ((lon > 40) and (lon < 120))
    caribbean = ((lat > 5) and (lat < 25)) and ((lon > -90) and (lon < -55))
    return int(pacific_ring or indian_ocean or caribbean)

# Función para predecir riesgo
def predict_tsunami_risk(earthquake):
    """Predecir riesgo de tsunami"""
    if model is None:
        return None
    
    try:
        # Preparar datos con defaults para valores faltantes
        defaults = {
            'magnitude': 5.0,
            'depth': 10.0,
            'latitude': 0.0,
            'longitude': 0.0,
            'sig': 1000,
            'mmi': 5.0,
            'cdi': 5.0,
            'nst': 50,
            'dmin': 1.0,
            'gap': 100.0,
        }
        
        input_data = {}
        for key in defaults:
            val = earthquake.get(key, defaults[key])
            if val is None or (isinstance(val, float) and pd.isna(val)):
                val = defaults[key]
            input_data[key] = val
        
        # Añadir Year y Month
        dt = earthquake['time']
        input_data['Year'] = dt.year
        input_data['Month'] = dt.month
        
        # Ingeniería de características
        df = pd.DataFrame([input_data])
        
        lat = df['latitude'].iloc[0]
        lon = df['longitude'].iloc[0]
        df['ocean_proximity'] = calculate_ocean_proximity(lat, lon)
        df['mag_depth_ratio'] = df['magnitude'] / (df['depth'] + 1)
        df['intensity_score'] = (
            df['magnitude'] * 0.5 + 
            df['mmi'] * 0.3 + 
            df['sig'] / 100 * 0.2
        )
        df['shallow_strong'] = (
            (df['depth'] < 70) & 
            (df['magnitude'] > 7.5)
        ).astype(int)
        
        # Predecir
        X = df[feature_names]
        X_scaled = scaler.transform(X)
        probability = float(model.predict_proba(X_scaled)[0, 1])
        
        # Clasificar riesgo
        if probability < 0.2:
            risk_level = "Muy Bajo"
            risk_color = "#10b981"
            risk_emoji = "🟢"
        elif probability < 0.4:
            risk_level = "Bajo"
            risk_color = "#84cc16"
            risk_emoji = "🟢"
        elif probability < 0.6:
            risk_level = "Moderado"
            risk_color = "#f59e0b"
            risk_emoji = "🟡"
        elif probability < 0.8:
            risk_level = "Alto"
            risk_color = "#f97316"
            risk_emoji = "🟠"
        else:
            risk_level = "Muy Alto"
            risk_color = "#ef4444"
            risk_emoji = "🔴"
        
        return {
            'probability': probability,
            'risk_level': risk_level,
            'risk_color': risk_color,
            'risk_emoji': risk_emoji
        }
        
    except Exception as e:
        st.error(f"Error en predicción: {e}")
        return None

# Título
st.title("🔴 Monitoreo de Terremotos en Tiempo Real")
st.markdown("Conectado a **USGS Earthquake API** para detección y análisis automático")

# Controles en sidebar
with st.sidebar:
    st.header("⚙️ Configuración")
    
    time_window = st.selectbox(
        "Ventana de tiempo",
        options=[10, 30, 60, 120, 360, 720, 1440],
        index=2,
        format_func=lambda x: f"Últimos {x} minutos" if x < 1440 else "Últimas 24 horas"
    )
    
    min_magnitude = st.slider(
        "Magnitud mínima",
        min_value=2.5,
        max_value=7.0,
        value=5.0,
        step=0.5,
        help="Filtrar terremotos por magnitud mínima"
    )
    
    alert_threshold = st.slider(
        "Umbral de alerta (%)",
        min_value=10,
        max_value=90,
        value=30,
        step=5,
        help="Probabilidad mínima para considerar alerta"
    ) / 100
    
    auto_refresh = st.checkbox("Auto-actualización", value=False)
    
    if auto_refresh:
        refresh_interval = st.slider(
            "Intervalo (segundos)",
            min_value=30,
            max_value=300,
            value=60,
            step=30
        )
    
    st.divider()
    
    if st.button("🔄 Actualizar ahora", use_container_width=True):
        st.rerun()
    
    st.divider()
    st.markdown("""
    **Fuente de datos:**
    [USGS Earthquake Hazards Program](https://earthquake.usgs.gov/)
    
    **Actualización:**
    Los datos del USGS se actualizan continuamente.
    """)

# Obtener datos
with st.spinner("🌍 Obteniendo datos de terremotos..."):
    earthquakes = fetch_recent_earthquakes(
        minutes=time_window,
        min_magnitude=min_magnitude
    )

# Estadísticas generales
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Terremotos", len(earthquakes))

with col2:
    if earthquakes:
        max_mag = max(eq['magnitude'] for eq in earthquakes)
        st.metric("Magnitud Máxima", f"{max_mag:.1f}")
    else:
        st.metric("Magnitud Máxima", "N/A")

with col3:
    alerts_count = 0
    if earthquakes and model is not None:
        for eq in earthquakes:
            risk = predict_tsunami_risk(eq)
            if risk and risk['probability'] >= alert_threshold:
                alerts_count += 1
    st.metric("Alertas de Tsunami", alerts_count)

with col4:
    st.metric("Última actualización", datetime.now().strftime("%H:%M:%S"))

st.divider()

# Mostrar terremotos
if not earthquakes:
    st.info(f"ℹ️ No se encontraron terremotos de magnitud ≥{min_magnitude} en los últimos {time_window} minutos.")
else:
    st.subheader(f"📋 Terremotos Detectados ({len(earthquakes)})")
    
    # Analizar cada terremoto
    earthquakes_with_risk = []
    for eq in earthquakes:
        risk = predict_tsunami_risk(eq)
        if risk:
            eq['risk'] = risk
            earthquakes_with_risk.append(eq)
    
    # Ordenar por probabilidad de tsunami (descendente)
    earthquakes_with_risk.sort(key=lambda x: x['risk']['probability'], reverse=True)
    
    # Tabs para diferentes vistas
    tab1, tab2, tab3 = st.tabs(["🚨 Alertas Activas", "📊 Todos los Eventos", "🗺️ Mapa"])
    
    with tab1:
        high_risk = [eq for eq in earthquakes_with_risk if eq['risk']['probability'] >= alert_threshold]
        
        if not high_risk:
            st.success(f"✅ No hay alertas activas (umbral: {alert_threshold*100:.0f}%)")
        else:
            st.warning(f"⚠️ {len(high_risk)} alerta(s) detectada(s)")
            
            for eq in high_risk:
                risk = eq['risk']
                with st.expander(
                    f"{risk['risk_emoji']} M{eq['magnitude']:.1f} - {eq['place']} - "
                    f"Riesgo: {risk['probability']*100:.1f}%",
                    expanded=True
                ):
                    col_a, col_b = st.columns([2, 1])
                    
                    with col_a:
                        st.markdown(f"""
                        **📍 Ubicación:** {eq['place']}  
                        **🕐 Hora:** {eq['time'].strftime('%Y-%m-%d %H:%M:%S')} UTC  
                        **📏 Magnitud:** {eq['magnitude']:.1f}  
                        **⬇️ Profundidad:** {eq['depth']:.1f} km  
                        **🌐 Coordenadas:** {eq['latitude']:.3f}, {eq['longitude']:.3f}  
                        """)
                        
                        if eq['url']:
                            st.markdown(f"[🔗 Ver detalles en USGS]({eq['url']})")
                    
                    with col_b:
                        st.markdown(f"""
                        ### {risk['risk_emoji']} {risk['risk_level']}
                        **Probabilidad:** {risk['probability']*100:.1f}%
                        """)
                        st.markdown(
                            f"<div style='background-color: {risk['risk_color']}; "
                            f"height: 10px; border-radius: 5px;'></div>",
                            unsafe_allow_html=True
                        )
                        
                        if risk['probability'] >= 0.7:
                            st.error("🚨 EVACUACIÓN INMEDIATA")
                        elif risk['probability'] >= 0.5:
                            st.warning("⚠️ PREPARAR EVACUACIÓN")
                        else:
                            st.info("ℹ️ MANTENERSE ALERTA")
    
    with tab2:
        for eq in earthquakes_with_risk:
            risk = eq['risk']
            
            with st.expander(
                f"{risk['risk_emoji']} M{eq['magnitude']:.1f} - {eq['place']} - "
                f"{eq['time'].strftime('%H:%M:%S')} UTC"
            ):
                col_a, col_b, col_c = st.columns([2, 1, 1])
                
                with col_a:
                    st.markdown(f"""
                    **Ubicación:** {eq['place']}  
                    **Hora:** {eq['time'].strftime('%Y-%m-%d %H:%M:%S')} UTC  
                    **Magnitud:** {eq['magnitude']:.1f}  
                    **Profundidad:** {eq['depth']:.1f} km  
                    **Coordenadas:** {eq['latitude']:.3f}, {eq['longitude']:.3f}  
                    """)
                
                with col_b:
                    st.metric("Riesgo de Tsunami", f"{risk['probability']*100:.1f}%")
                    st.markdown(f"**{risk['risk_level']}**")
                
                with col_c:
                    st.metric("Significancia", eq['sig'])
                    if eq['url']:
                        st.markdown(f"[🔗 USGS]({eq['url']})")
    
    with tab3:
        st.markdown("### 🗺️ Ubicación de Terremotos")
        
        # Preparar datos para el mapa
        map_data = pd.DataFrame([{
            'lat': eq['latitude'],
            'lon': eq['longitude'],
            'magnitude': eq['magnitude'],
            'risk': eq['risk']['probability'] * 100,
            'place': eq['place']
        } for eq in earthquakes_with_risk])
        
        # Mostrar mapa
        st.map(map_data, zoom=1, use_container_width=True)
        
        # Tabla resumen
        st.dataframe(
            map_data.sort_values('risk', ascending=False),
            use_container_width=True,
            hide_index=True
        )

# Auto-refresh
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()
