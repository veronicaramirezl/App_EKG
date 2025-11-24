import streamlit as st
import json
from utils.styles import load_css
from modules import visual, multiple, open_q

# Configuración
st.set_page_config(page_title="Simulador EKG", page_icon="🫀", layout="wide")
st.markdown(load_css(), unsafe_allow_html=True)

# Cargar DB
@st.cache_data
def load_data():
    with open('data/db.json', 'r', encoding='utf-8') as f:
        return json.load(f)

data_db = load_data()

# ---- SISTEMA DE PROGRESO ----

if "progress" not in st.session_state:
    st.session_state["progress"] = {
        "attempts": [],  # cada entrada será un dict con: id, topic, result
        "by_topic": {},  # success / fail por tema
        "completed": False
    }

# Barra lateral
st.sidebar.title("🫀 CardioSim Pro")
api_key = st.sidebar.text_input("OpenAI API Key", type="password")
mode = st.sidebar.radio("Menú", ["Medición de Intervalos y Ondas", "Selección Múltiple", "Diagnóstico Completo"])

# Small controls
if "visual_idx" not in st.session_state:
    st.session_state["visual_idx"] = 0

if st.sidebar.button("Reiniciar módulo visual"):
    st.session_state["visual_idx"] = 0
    st.experimental_rerun()

# Enrutamiento
if mode == "Medición de Intervalos y Ondas":
    visual.render(data_db, api_key)
elif mode == "Selección Múltiple":
    multiple.render(data_db["multiple_choice"])
elif mode == "Diagnóstico Completo":
    open_q.render_open_all(data_db["open"], api_key)

# ---- RESUMEN FINAL DEL PROGRESO ----
if st.session_state["progress"]["completed"]:
    st.markdown("## 📊 Resumen de tu desempeño")

    attempts = st.session_state["progress"]["attempts"]
    by_topic = st.session_state["progress"]["by_topic"]

    total = len(attempts)
    correct = len([a for a in attempts if "correct" in a["result"]])
    score = round((correct / total) * 100)

    st.metric("Puntaje final", f"{score}%")

    st.markdown("### 📌 Rendimiento por tema")
    for topic, stats in by_topic.items():
        total_t = stats["ok"] + stats["fail"]
        pct = round(stats["ok"] / total_t * 100)
        color = "green" if pct >= 75 else "orange" if pct >= 50 else "red"

        st.markdown(f"""
        **{topic}**  
        - Correctas: {stats['ok']}  
        - Incorrectas: {stats['fail']}  
        - **Nivel: <span style='color:{color}'>{pct}%</span>**  
        """, unsafe_allow_html=True)

    # temas débiles
    weak = [t for t, s in by_topic.items() if s["fail"] > s["ok"]]

    if weak:
        st.markdown("### 🚨 Temas a reforzar")
        for w in weak:
            st.markdown(f"- **{w}** , te costó más trabajo. Revisa los conceptos relacionados.")
    else:
        st.success("¡No tienes temas débiles! Excelente trabajo 🚀")

