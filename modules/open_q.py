from matplotlib import text
import streamlit as st
from utils.helpers import load_image, get_ai_feedback


# ------------------------------------------------------------
# REGISTRO DE RESULTADOS EN SISTEMA GLOBAL DE PROGRESO
# ------------------------------------------------------------
def register_result_open(q, result):

    topic = "Diagnóstico ECG"

    # Evitar duplicaciones
    already = any(a["id"] == q["id"] for a in st.session_state["progress"]["attempts"])
    if not already:
        st.session_state["progress"]["attempts"].append({
            "id": q["id"],
            "topic": topic,
            "result": result
        })

        if topic not in st.session_state["progress"]["by_topic"]:
            st.session_state["progress"]["by_topic"][topic] = {"ok": 0, "fail": 0}

        if result == "correct":
            st.session_state["progress"]["by_topic"][topic]["ok"] += 1
        else:
            st.session_state["progress"]["by_topic"][topic]["fail"] += 1


# ------------------------------------------------------------
# RENDERIZADOR PRINCIPAL PARA TODOS LOS CASOS ABIERTOS
# ------------------------------------------------------------
def render_open_all(open_list, api_key):

    # Inicializar índice global si no existe
    if "open_idx" not in st.session_state:
        st.session_state["open_idx"] = 0

    idx = st.session_state["open_idx"]

    # --------------- FIN DEL MÓDULO ----------------
    if idx >= len(open_list):
        st.success("🎉 ¡Has completado todos los casos diagnósticos!")
        st.session_state["progress"]["completed"] = True

        if st.button("🔄 Volver a empezar"):
            st.session_state["open_idx"] = 0
            st.session_state["progress"]["attempts"] = []
            st.session_state["progress"]["by_topic"] = {}
            st.session_state["progress"]["completed"] = False
            st.experimental_rerun()
        return

    # Obtener caso actual
    q = open_list[idx]

    # Keys consistentes por pregunta
    status_key = f"status_{q['id']}"                # "input" o "feedback"
    feedback_key = f"feedback_{q['id']}"
    result_key = f"result_{q['id']}"

    if status_key not in st.session_state:
        st.session_state[status_key] = "input"

    st.markdown("<h2 style='margin-top:60px; margin-bottom:20px;'>🩺 Interpretación Diagnóstica del ECG</h2>", unsafe_allow_html=True)


    # Mostrar ECG
    try:
        st.image(load_image(q["image"]), use_container_width=True)
    except Exception:
        st.error("No se pudo cargar la imagen.")

    st.markdown(f"### ❓ {q['question']}")
    st.write("---")

    # ===========================================================
    #     FASE 1 — FORMULARIO ESTRUCTURADO + ANALISIS
    # ===========================================================
    if st.session_state[status_key] == "input":

        with st.form(key=f"form_{q['id']}"):

            st.subheader("1️⃣ Evaluación estructurada del ECG")

            c1, c2 = st.columns(2)

            with c1:
                rhythm = st.selectbox("Ritmo:", 
                    ["Selecciona...", "Sinusal", "No sinusal", "Indeterminado"],
                    key=f"rhythm_{q['id']}"
                )
                rate = st.selectbox("Frecuencia:", 
                    ["Selecciona...", "<60 (Bradicardia)", "60–100 (Normal)", ">100 (Taquicardia)"],
                    key=f"rate_{q['id']}"
                )
                axis = st.selectbox("Eje:", 
                    ["Selecciona...", "Normal", "Izq", "Der", "Indeterminado"],
                    key=f"axis_{q['id']}"
                )
                pr = st.selectbox("Intervalo PR:", 
                    ["Selecciona...", "Normal", "Prolongado", "Corto", "No medible"],
                    key=f"pr_{q['id']}"
                )

            with c2:
                qrs = st.selectbox("QRS:", 
                    ["Selecciona...", "Estrecho", "Ancho"],
                    key=f"qrs_{q['id']}"
                )
                st_segment = st.selectbox("Segmento ST:", 
                    ["Selecciona...", "Normal", "Elevado", "Deprimido", "No evaluable"],
                    key=f"st_{q['id']}"
                )
                pwaves = st.selectbox("Ondas P:", 
                    ["Selecciona...", "Presentes", "Ausentes", "Anormales"],
                    key=f"p_{q['id']}"
                )

            st.write("---")
            st.subheader("2️⃣ Análisis obligatorio")
            ekg_description = st.text_area("Descripción (¿Cómo le presentarías el caso a un colega?):", height=120)
            justification = st.text_area("Justificación (¿por qué llegas al diagnóstico?):", height=120)

            submitted = st.form_submit_button("📤 Enviar análisis completo")

        # ---- Validación del form fuera del 'with' pero indentado en el if ----
        if submitted:

            # Validación estricta
            invalid = any([
                rhythm == "Selecciona...",
                rate == "Selecciona...",
                axis == "Selecciona...",
                pr == "Selecciona...",
                qrs == "Selecciona...",
                st_segment == "Selecciona...",
                pwaves == "Selecciona...",
                not ekg_description.strip(),
                not justification.strip()
            ])

            if invalid:
                st.error("⚠️ Debes completar TODAS las secciones antes de enviar.")
            else:
                structured = (
                    f"Ritmo: {rhythm}, Frecuencia: {rate}, "
                    f"Eje: {axis}, PR: {pr}, QRS: {qrs}, ST: {st_segment}, P: {pwaves}"
                )

                student_full = (
                    f"Descripción: {ekg_description}\n"
                    f"Justificación: {justification}"
                )
                instuction = "llegar al diagnóstico correcto basándote en tu análisis estructurado y justificación"
                
                context = f"Diagnóstico correcto: {q['correct_diagnosis']}\nClaves: {q['key_features']}"
                
                gold = (
                    f"Diagnóstico correcto: {q['correct_diagnosis']}\n"
                    f"Claves: {q['key_features']}"
                )

                # -------- Llamada a IA --------
                with st.spinner("🤖 Analizando tu interpretación..."):
                    prompt = (
                        "Eres un cardiólogo experto. Evalúa la interpretación del estudiante.\n"
                        "Indica si su diagnóstico concuerda o no. vas a decir Diagnóstico correcto! o Diagnóstico incorrecto!\n"
                        "Explica brevemente en segunda persona sus aciertos o errores.\n\n"
                        f"{gold}\n\n"
                        f"Evaluación del estudiante:\n{structured}\n\n"
                        f"{student_full}"
                    )

                    feedback = get_ai_feedback(api_key, "Experto ECG", prompt,instuction, context, model="gemini")

                # ¿El estudiante mencionó el diagnóstico correcto?
                import matplotlib
                text = feedback.lower()
                feedback_correct = ("diagnóstico correcto" in text) or ("diagnostico correcto" in text)

                
                # Evaluar si aparece en el texto del estudiante
                result_status = "correct" if feedback_correct else "fail"


                # Guardar estados
                st.session_state[feedback_key] = feedback
                st.session_state[result_key] = result_status

                register_result_open(q, result_status)

                # Cambiar a modo feedback Y RECARGAR
                st.session_state[status_key] = "feedback"
                st.rerun()  # <--- ESTA ES LA CLAVE

    # ===========================================================
    #     FASE 2 — RETROALIMENTACIÓN + SIGUIENTE CASO
    # ===========================================================
    else:
        st.markdown("---")
        st.markdown("## 👩‍⚕️ Retroalimentación del docente")

        res = st.session_state.get(result_key, "fail")

        if res == "correct":
            st.success("✅ ¡Diagnóstico correcto!")
        else:
            st.error(f"❌ Diagnóstico incorrecto. Lo correcto era **{q['correct_diagnosis']}**")

        st.info(st.session_state.get(feedback_key, "No hay feedback disponible."))

        if st.button("➡️ Siguiente Caso"):
            st.session_state["open_idx"] += 1
            # Limpieza de variables de estado de la pregunta anterior
            del st.session_state[status_key]
            if feedback_key in st.session_state: del st.session_state[feedback_key]
            if result_key in st.session_state: del st.session_state[result_key]
            
            st.experimental_rerun()
