import streamlit as st
import requests

st.set_page_config(page_title="Test", layout="wide")
st.title("✅ TEST - Panel Funcional")

st.success("Streamlit se está ejecutando correctamente")

# Test de conexión básica
try:
    response = requests.get("https://gimnasio-2-0-1.onrender.com/socios/", timeout=10)
    if response.status_code == 200:
        st.write("✅ Conexión a API: EXITOSA")
        st.json(response.json())
    else:
        st.error(f"❌ Error en API: {response.status_code}")
except Exception as e:
    st.error(f"❌ Error de conexión: {e}")

st.info("Si ves este mensaje, Streamlit funciona correctamente")