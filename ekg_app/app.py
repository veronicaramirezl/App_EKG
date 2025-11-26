import os
import streamlit as st
import json
from utils.styles import load_css
from modules import visual, multiple, open_q
from login import login_screen
from utils.gsheets import append_user_result
from PIL import Image




params = st.experimental_get_query_params()

# ----------------------------------------------------
# CONFIGURACIÓN GENERAL DE LA APP
# ----------------------------------------------------
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown(load_css(), unsafe_allow_html=True)


# ----------------------------------------------------
# CARGA DE BASE DE DATOS
# ----------------------------------------------------
@st.cache_data
def load_data():
    with open('data/db.json', 'r', encoding='utf-8') as f:
        return json.load(f)

data_db = load_data()


# ----------------------------------------------------
# SESIONES: LOGIN Y PROGRESO
# ----------------------------------------------------

# Estado para login de usuario
if "user_data" not in st.session_state:
    st.session_state["user_data"] = None

# Mostrar pantalla de login si aún no hay usuario
if st.session_state["user_data"] is None:
    login_screen()
    st.stop()


# Estado para progreso
if "progress" not in st.session_state:
    st.session_state["progress"] = {
        "attempts": [],  # registros de intento
        "by_topic": {},  # desempeño por tema
        "completed": False
    }


# ----------------------------------------------------
# BARRA LATERAL MEJORADA
# ----------------------------------------------------

with st.sidebar:
    logo = Image.open("assets/logo/logo.png")
    st.image(logo, use_column_width=True)

    # Información del usuario
    user = st.session_state["user_data"]
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, rgba(230, 57, 70, 0.2), rgba(193, 18, 31, 0.2)); 
                padding: 1rem; 
                border-radius: 10px; 
                border-left: 4px solid #E63946;
                margin-bottom: 1rem;'>
        <p style='margin: 0; color: #FFB3BA; font-size: 0.9rem;'>👤 Estudiante</p>
        <p style='margin: 0; color: white; font-weight: 600; font-size: 1.1rem;'>{user['name']}</p>
        <p style='margin: 0; color: #B0B0B0; font-size: 0.85rem;'>DNI: {user['dni']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # API Key con mejor presentación
    st.markdown("#### 🔑 Configuración")
    api_key = st.text_input("OpenAI API Key", type="password", help="Necesaria para feedback con IA")
    
    st.markdown("---")
    
    # Menú con iconos mejorados
    st.markdown("#### 📚 Módulos de Aprendizaje")
    mode = st.radio(
        "Selecciona un módulo:",
        [
            "📏 Medición de Intervalos",
            "✅ Selección Múltiple",
            "🩺 Diagnóstico Completo"
        ],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Estadísticas rápidas
    st.markdown("#### 📊 Tu Progreso")
    attempts = st.session_state["progress"]["attempts"]
    if len(attempts) > 0:
        correct = len([a for a in attempts if "correct" in a["result"]])
        total = len(attempts)
        pct = round((correct / total) * 100)
        
        st.metric("Respuestas correctas", f"{correct}/{total}", f"{pct}%")
    else:
        st.info("Aún no has respondido preguntas")
    
    st.markdown("---")
    
    # Control adicional
    # Inicializar contador de reinicio global para el canvas
    if "canvas_reset_counter" not in st.session_state:
        st.session_state["canvas_reset_counter"] = 0
    if "visual_idx" not in st.session_state:
        st.session_state["visual_idx"] = 0


    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #B0B0B0; font-size: 0.8rem;'>
        <p>Aureus Cardio v1.0</p>
        <p>Sistema de Entrenamiento ECG</p>
    </div>
    """, unsafe_allow_html=True)




# ----------------------------------------------------
# ENRUTAMIENTO PRINCIPAL
# ----------------------------------------------------
if "📏 Medición" in mode:
    # modulo de visualizaciones y mediciones, banner introductorio
    visual.render(data_db, api_key)

elif "✅ Selección" in mode:
    multiple.render(data_db["multiple_choice"])

elif "🩺 Diagnóstico" in mode:
    
    open_q.render_open_all(data_db["open"], api_key)
    

    

# ----------------------------------------------------
# RESUMEN FINAL + GUARDADO EN GOOGLE SHEETS
# ----------------------------------------------------
if st.session_state["progress"]["completed"]:
    
    if "summary_shown" not in st.session_state:
        st.session_state["summary_shown"] = False
        st.session_state["sheets_saved"] = False

    if st.session_state["summary_shown"]:
        st.stop()

    st.session_state["summary_shown"] = True
    
    # Banner de finalización
    st.markdown("""
    <div style='background: linear-gradient(135deg, #06D6A0, #048A81); 
                padding: 2rem; 
                border-radius: 15px; 
                text-align: center;
                box-shadow: 0 10px 40px rgba(6, 214, 160, 0.4);
                margin: 2rem 0;'>
        <h1 style='color: white; margin: 0;'>🎉 ¡Felicitaciones!</h1>
        <p style='color: white; font-size: 1.2rem; margin: 0.5rem 0 0 0;'>
            Has completado el módulo de entrenamiento
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("## 📊 Resumen de tu Desempeño")

    user = st.session_state["user_data"]
    attempts = st.session_state["progress"]["attempts"]
    by_topic = st.session_state["progress"]["by_topic"]

    total = len(attempts)
    correct = len([a for a in attempts if "correct" in a["result"]])
    score = round((correct / total) * 100) if total > 0 else 0

    # Métricas principales en columnas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🎯 Puntaje Final", f"{score}%", 
                 delta="Aprobado" if score >= 70 else "Necesita refuerzo",
                 delta_color="normal" if score >= 70 else "inverse")
    
    with col2:
        st.metric("✅ Respuestas Correctas", f"{correct}/{total}")
    
    with col3:
        accuracy = "Excelente" if score >= 90 else "Bueno" if score >= 70 else "Regular"
        st.metric("📈 Nivel de Dominio", accuracy)

    # GUARDAR EN GOOGLE SHEETS
    # --------------------
    if not st.session_state["sheets_saved"]:
        try:
            append_user_result(
                sheet_name="Registro_EKG",
                user_data={
                    "name": user["name"],
                    "dni": user["dni"],
                    "sex": user["sex"],
                    "country": user["country"],
                    "level": user["level"],
                    "term": user["term"],
                    "university": user["university"],
                    "experience": user["experience"],
                    "formal_training": user["formal_training"],
                    "clinical_frequency": user["clinical_frequency"],
                    "score": score,
                    "module": mode,
                    "num_questions": total
                }
            )
            st.session_state["sheets_saved"] = True
            st.success("✅ Registro guardado en Google Sheets correctamente")
        except Exception as e:
            st.error(f"❌ Error guardando en Sheets: {e}")
    else:
        st.success("✅ Registro guardado en Google Sheets correctamente")

    st.markdown("---")


    # --------------------
    # DESEMPEÑO POR TEMA
    # --------------------
    st.markdown("### 📌 Rendimiento por Tema")

    for topic, stats in by_topic.items():
        total_t = stats["ok"] + stats["fail"]
        if total_t == 0:
            continue
            
        pct = round(stats["ok"] / total_t * 100)
        
        # Determinar color y emoji según rendimiento
        if pct >= 75:
            color = "#06D6A0"
            emoji = "🌟"
            nivel = "Excelente"
        elif pct >= 50:
            color = "#FFD166"
            emoji = "⚠️"
            nivel = "Aceptable"
        else:
            color = "#EF476F"
            emoji = "📚"
            nivel = "Necesita refuerzo"

        st.markdown(f"""
        <div style='background-color: rgba(230, 57, 70, 0.05); 
                    padding: 1rem; 
                    border-radius: 10px; 
                    border-left: 5px solid {color};
                    margin-bottom: 1rem;'>
            <p style='margin: 0; color: #E5E5E5; font-size: 1.1rem; font-weight: 600;'>
                {emoji} {topic}
            </p>
            <div style='display: flex; justify-content: space-between; margin-top: 0.5rem;'>
                <span style='color: #B0B0B0;'>Correctas: <strong style='color: {color};'>{stats['ok']}</strong></span>
                <span style='color: #B0B0B0;'>Incorrectas: <strong style='color: #EF476F;'>{stats['fail']}</strong></span>
                <span style='color: #B0B0B0;'>Nivel: <strong style='color: {color};'>{nivel} ({pct}%)</strong></span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # --------------------
    # TEMAS DÉBILES
    # --------------------
    weak = [t for t, s in by_topic.items() if s["fail"] > s["ok"]]

    if weak:
        st.markdown("### 🚨 Áreas de Mejora")
        st.markdown("""
        <div style='background-color: rgba(239, 71, 111, 0.1); 
                    padding: 1.5rem; 
                    border-radius: 10px; 
                    border: 2px solid #EF476F;'>
        """, unsafe_allow_html=True)
        
        for w in weak:
            st.markdown(f"""
            <p style='color: #E5E5E5; margin: 0.5rem 0;'>
                📚 <strong style='color: #EF476F;'>{w}</strong> - Se recomienda repaso adicional
            </p>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='background-color: rgba(6, 214, 160, 0.1); 
                    padding: 1.5rem; 
                    border-radius: 10px; 
                    border: 2px solid #06D6A0;
                    text-align: center;'>
            <p style='color: #06D6A0; font-size: 1.2rem; margin: 0; font-weight: 600;'>
                🚀 ¡Excelente trabajo! Dominas todos los temas evaluados
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Botón de finalización
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='text-align: center; margin-top: 2rem;'>
            <p style='color: #B0B0B0; font-size: 1.1rem;'>
                Gracias por usar Aureus Cardio 🫀
            </p>
        </div>
        """, unsafe_allow_html=True)