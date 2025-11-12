# 🚀 Guía de Despliegue en Streamlit Cloud

## Paso 1: Preparar los archivos

Copia los archivos del modelo a la carpeta `streamlit_app/`:

```bash
# Desde la carpeta raíz del proyecto
copy model.pkl streamlit_app/
copy scaler.pkl streamlit_app/
copy features.json streamlit_app/
```

## Paso 2: Actualizar rutas en app.py

Cambia estas líneas en `app.py`:

```python
# De:
model = joblib.load('../model.pkl')
scaler = joblib.load('../scaler.pkl')
with open('../features.json', 'r') as f:

# A:
model = joblib.load('model.pkl')
scaler = joblib.load('scaler.pkl')
with open('features.json', 'r') as f:
```

## Paso 3: Subir a GitHub

```bash
git add streamlit_app/
git commit -m "Add Streamlit app"
git push origin main
```

## Paso 4: Desplegar en Streamlit Cloud

1. Ve a https://share.streamlit.io
2. Click en "New app"
3. Conecta tu repositorio de GitHub
4. Configura:
   - **Repository:** tu-usuario/tu-repo
   - **Branch:** main
   - **Main file path:** streamlit_app/app.py
5. Click en "Deploy!"

## Paso 5: ¡Listo!

Tu app estará disponible en:

```
https://tu-usuario-tu-repo.streamlit.app
```

---

## 🔧 Prueba Local Primero

Antes de desplegar, prueba localmente:

```bash
cd streamlit_app
pip install -r requirements.txt
streamlit run app.py
```

## 🐛 Solución de Problemas Comunes

### Error: "No module named 'streamlit'"

```bash
pip install streamlit
```

### Error: "FileNotFoundError: model.pkl"

Verifica que los archivos estén en la carpeta correcta y las rutas sean correctas.

### La app se ve diferente en Cloud

Asegúrate de que el archivo `.streamlit/config.toml` esté incluido en el repositorio.

## 📝 Variables de Entorno (Opcional)

Si necesitas variables de entorno, créalas en Streamlit Cloud:

1. Settings > Secrets
2. Añade en formato TOML:

```toml
API_KEY = "tu_clave_api"
```

Y úsalas en el código:

```python
import streamlit as st
api_key = st.secrets["API_KEY"]
```
