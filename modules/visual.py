import streamlit as st
from streamlit_drawable_canvas import st_canvas
from utils.helpers import load_image, get_ai_feedback, get_ai_visual_feedback
from PIL import Image
import io
import base64

# ---------- UTILS ----------
def pil_to_base64(img):
    """Convierte PIL Image a base64 para enviar a la IA."""
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def combine_canvas_with_image(background_img, canvas_data):
    """Combina la imagen de fondo con lo dibujado en el canvas."""
    if canvas_data is None or canvas_data.image_data is None:
        return background_img
    canvas_img = Image.fromarray(canvas_data.image_data.astype('uint8'), 'RGBA')
    combined = background_img.copy().convert('RGBA')
    combined.paste(canvas_img, (0, 0), canvas_img)
    return combined

def register_result(q, result):
    """Registra el resultado del estudiante."""
    topic = q.get("topic", "General")
    st.session_state["progress"]["attempts"].append({
        "id": q["id"],
        "topic": topic,
        "result": result
    })
    if topic not in st.session_state["progress"]["by_topic"]:
        st.session_state["progress"]["by_topic"][topic] = {"ok": 0, "fail": 0}
    if "correct" in result:
        st.session_state["progress"]["by_topic"][topic]["ok"] += 1
    else:
        st.session_state["progress"]["by_topic"][topic]["fail"] += 1

def reset_question_state(qid):
    """Limpia el estado de una pregunta."""
    keys = [f"canvas_{qid}", f"ai_feedback_{qid}", f"user_ms_{qid}",
            f"attempt_failed_{qid}", f"solved_success_{qid}", 
            f"second_ms_value_{qid}", f"screenshot_{qid}",
            f"first_expl_sent_{qid}", f"logic_{qid}", f"failed_second_attempt_{qid}"]
    for k in list(st.session_state.keys()):
        if any(key in k for key in keys):
            del st.session_state[k]

def find_next_index_same_topic(visuals, current_idx):
    if current_idx is None: return None
    current_topic = visuals[current_idx].get("topic")
    for i in range(current_idx + 1, len(visuals)):
        if visuals[i].get("topic") == current_topic:
            return i
    return None

def find_next_index_next_topic(visuals, current_idx):
    if current_idx is None: return 0 if len(visuals) > 0 else None
    current_topic = visuals[current_idx].get("topic")
    for i in range(current_idx + 1, len(visuals)):
        if visuals[i].get("topic") != current_topic:
            return i
    return None

# ---------- RENDER MODULE ----------
def render(data_db, api_key):
    """Módulo visual con dibujo libre y revisión por IA."""
    
    visuals = data_db.get("visual", [])
    if len(visuals) == 0:
        st.warning("No hay ejercicios visuales en la base de datos.")
        return

    if "visual_idx" not in st.session_state:
        st.session_state["visual_idx"] = 0
    current_idx = st.session_state["visual_idx"]
    
    if current_idx >= len(visuals):
        st.session_state["progress"]["completed"] = True
        st.success("🎉 Has terminado todos los ejercicios. ¡Bien hecho!")
        if st.button("🔄 Volver a empezar"):
            st.session_state["visual_idx"] = 0
            st.session_state["progress"] = {"attempts": [], "by_topic": {}, "completed": False}
            st.rerun()
        return

    q = visuals[current_idx]
    qid = q["id"]

    # Inicializar flags
    for key in ["first_expl_sent", "ai_feedback", "attempt_failed", "solved_success", "failed_second_attempt"]:
        full_key = f"{key}_{qid}"
        if full_key not in st.session_state:
            st.session_state[full_key] = False

    # Header
    if current_idx == 0:
        st.markdown("<h1 style='text-align: center;'>Módulo de Medición de Intervalos en ECG</h1>", unsafe_allow_html=True)
        st.markdown("""
        **Instrucciones:**
        1. Dibuja puntos/círculos en el ECG para marcar el inicio y fin del intervalo
        2. Escribe tu medición en milisegundos
        3. La IA revisará visualmente tu trabajo y te dará feedback
        """)

    st.header(f"📏 [{q.get('topic','')}] {q.get('title')}")
    st.info(q.get("instruction", ""))

    # Cargar imagen
    img = load_image(q.get("image"))
    if img is None:
        st.error(f"No se pudo cargar la imagen: {q.get('image')}")
        st.stop()

    locked = st.session_state[f"solved_success_{qid}"]
    drawing_mode = "transform" if locked else "circle"

    # Canvas
    canvas_result = st_canvas(
        fill_color="rgba(255, 0, 0, 0.3)",
        stroke_width=3,
        stroke_color="#FF0000",
        background_image=img,
        update_streamlit=True,
        height=img.height,
        width=img.width,
        drawing_mode=drawing_mode,
        point_display_radius=10,
        key=f"canvas_{qid}"
    )

    # Primer intento
    user_ms = st.number_input("¿Cuánto mide el intervalo (ms)?", min_value=0, max_value=2000, step=1, key=f"user_ms_{qid}")
    
    if st.button("Revisar", key=f"submit_{qid}", type="primary"):
        if not api_key:
            st.error("⚠️ Se requiere API Key de OpenAI")
        elif user_ms <= 0:
            st.warning("⚠️ Ingresa un valor válido")
        elif abs(user_ms - q.get("correct_ms", 0)) <= q.get("tolerance_ms", 5):
            register_result(q, "correct_first_try")
            st.session_state[f"solved_success_{qid}"] = True
            st.success("✅ ¡Excelente! Respuesta correcta a la primera.")
            st.rerun()
        else:
            st.session_state[f"attempt_failed_{qid}"] = True
            register_result(q, "failed_first_try")
            st.error("❌ Respuesta incorrecta. Intenta de nuevo.")

    # Feedback IA después del primer intento fallido
    if st.session_state.get(f"attempt_failed_{qid}") and not st.session_state.get(f"first_expl_sent_{qid}"):
        explanation = st.text_area("Intento fallido, explica como llegaste a la respuesta en tus palabras (ej. conté 3 cuadritos):", key=f"logic_input_{qid}")
        if st.button("Enviar explicación (pedir feedback)", key=f"btn_explain_{qid}"):
            if not explanation.strip():
                st.warning("Escribe tu explicación antes de pedir feedback.")
            else:
                st.session_state[f"logic_{qid}"] = explanation
                st.session_state[f"first_expl_sent_{qid}"] = True
                
                combined_img = combine_canvas_with_image(img, canvas_result)
                img_base64 = pil_to_base64(combined_img)
                st.session_state[f"screenshot_{qid}"] = combined_img

                with st.spinner("🤖 La IA está revisando tu trabajo..."):
                    try:
                        ai_fb = get_ai_visual_feedback(
                            api_key=api_key,
                            img_base64=img_base64,
                            user_measurement=user_ms,
                            correct_ms=q.get("correct_ms"),
                            tolerance=q.get("tolerance_ms"),
                            instruction=q.get("instruction"),
                            explanation=explanation
                        )
                        st.session_state[f"ai_feedback_{qid}"] = ai_fb
                    except Exception as e:
                        st.session_state[f"ai_feedback_{qid}"] = f"Error llamando a la IA: {e}"
                st.rerun()

    # Segundo intento
    if st.session_state.get(f"first_expl_sent_{qid}"):
        st.markdown("### Retroalimentación docente (IA)")
        st.write(st.session_state.get(f"ai_feedback_{qid}", "Sin feedback disponible."))
        st.image(st.session_state.get(f"screenshot_{qid}"), caption="Tu trabajo", use_column_width=True)
        st.info("Segundo intento habilitado. Ingresa tu nuevo valor.")

        second_ms = st.number_input(
            "Segundo intento (ms)",
            min_value=1,
            max_value=2000,
            step=1,
            value=st.session_state.get(f"second_ms_value_{qid}", 1),
            key=f"second_input_{qid}"
        )
        st.session_state[f"second_ms_value_{qid}"] = second_ms

        send_second = st.button("Enviar segundo intento", key=f"send_second_{qid}", type="primary")
        if send_second:
            if abs(second_ms - q.get("correct_ms", 0)) <= q.get("tolerance_ms", 5):
                # Segundo intento correcto
                register_result(q, "correct_second_try")
                st.session_state[f"solved_success_{qid}"] = True
                st.session_state[f"show_success_message_{qid}"] = True  # Nueva bandera
            else:
                # Segundo intento incorrecto
                register_result(q, "failed_second_try")
                st.session_state[f"failed_second_attempt_{qid}"] = True
                st.session_state[f"show_error_message_{qid}"] = True  # Nueva bandera
                
            st.rerun()

        # Mostrar mensajes después del rerun
        if st.session_state.get(f"show_success_message_{qid}"):
            st.success(f"✅ ¡Excelente! Lo resolviste correctamente. El valor era {q.get('correct_ms')} ms.")
            # Opcional: limpiar el mensaje después de mostrarlo
            # st.session_state[f"show_success_message_{qid}"] = False

        if st.session_state.get(f"show_error_message_{qid}"):
            st.error(f"❌ Segundo intento incorrecto. Respuesta correcta: {q.get('correct_ms')} ms.")
            
            # Mostrar imagen corregida si existe en los datos
            corrected_image_path = q.get("corrected_image")
            if corrected_image_path:
                try:
                    corrected_img = load_image(corrected_image_path)
                    if corrected_img:
                        st.image(corrected_img, caption="📋 Imagen de referencia con la solución correcta", use_column_width=True)
                    else:
                        st.warning("No se pudo cargar la imagen corregida de referencia.")
                except Exception as e:
                    st.warning(f"No se pudo mostrar la imagen corregida: {e}")
            else:
                st.info("💡 Revisa tus marcas en el ECG. Asegúrate de medir desde el inicio hasta el final del intervalo correctamente.")
            
            # Opcional: limpiar el mensaje después de mostrarlo
            # st.session_state[f"show_error_message_{qid}"] = False




    # Botón único de continuar (solo aparece si ya resolvió o falló segundo intento)
    if st.session_state.get(f"solved_success_{qid}") or st.session_state.get(f"failed_second_attempt_{qid}"):
        st.markdown("---")
        st.subheader("¿Qué quieres hacer ahora?")
        
        # Determinar opciones disponibles
        same_topic_available = find_next_index_same_topic(visuals, current_idx) is not None
        next_topic_available = find_next_index_next_topic(visuals, current_idx) is not None
        
        # Si acertó a la primera, ofrecer cambiar de tema
        if st.session_state.get(f"solved_success_{qid}") and "correct_first_try" in [attempt.get("result") for attempt in st.session_state["progress"]["attempts"] if attempt.get("id") == qid]:
            
            if next_topic_available and same_topic_available:
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📚 Otra pregunta del mismo tema", 
                            key=f"same_topic_btn_{qid}",  # Cambiado
                            use_container_width=True,
                            type="secondary"):
                        next_idx = find_next_index_same_topic(visuals, current_idx)
                        reset_question_state(qid)
                        st.session_state["visual_idx"] = next_idx
                        
                with col2:
                    if st.button("🚀 Avanzar al siguiente tema", 
                            key=f"next_topic_btn_{qid}",  # Cambiado
                            use_container_width=True,
                            type="secondary"):
                        next_idx = find_next_index_next_topic(visuals, current_idx)
                        reset_question_state(qid)
                        st.session_state["visual_idx"] = next_idx
                        
                        
            elif next_topic_available:
                if st.button("🚀 Avanzar al siguiente tema", 
                        key=f"next_topic_solo_{qid}",  # Cambiado
                        use_container_width=True,
                        type="secondary"):
                    next_idx = find_next_index_next_topic(visuals, current_idx)
                    reset_question_state(qid)
                    st.session_state["visual_idx"] = next_idx
                
                    
            elif same_topic_available:
                if st.button("📚 Otra pregunta del mismo tema", 
                        key=f"same_topic_solo_{qid}",  # Cambiado
                        use_container_width=True,
                        type="secondary"):
                    next_idx = find_next_index_same_topic(visuals, current_idx)
                    reset_question_state(qid)
                    st.session_state["visual_idx"] = next_idx
                    
        
        # Si acertó en el segundo intento o falló ambos, solo ofrecer misma opción
        else:
            if same_topic_available:
                if st.button("➡️ Continuar con otra pregunta", 
                        key=f"continue_same_{qid}", 
                        use_container_width=True,
                        type="secondary"):
                    next_idx = find_next_index_same_topic(visuals, current_idx)
                    reset_question_state(qid)
                    st.session_state["visual_idx"] = next_idx
                    st.rerun()
                    
            elif next_topic_available:
                if st.button("➡️ Continuar al siguiente tema", 
                        key=f"continue_next_{qid}", 
                        use_container_width=True,
                        type="secondary"):
                    next_idx = find_next_index_next_topic(visuals, current_idx)
                    reset_question_state(qid)
                    st.session_state["visual_idx"] = next_idx
                    st.rerun()
                    
            else:
                if st.button("🏁 Finalizar módulo", 
                        key=f"finish_{qid}", 
                        use_container_width=True,
                        type="secondary"):
                    st.session_state["progress"]["completed"] = True
                    st.session_state["visual_idx"] = len(visuals)
                    st.rerun()

    # Mostrar progreso actual
    if "progress" in st.session_state and "by_topic" in st.session_state["progress"]:
        st.sidebar.markdown("### 📊 Progreso")
        for topic, stats in st.session_state["progress"]["by_topic"].items():
            total = stats["ok"] + stats["fail"]
            if total > 0:
                percentage = (stats["ok"] / total) * 100
                st.sidebar.write(f"**{topic}**: {stats['ok']}/{total} ({percentage:.1f}%)")