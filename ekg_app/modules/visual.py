import streamlit as st
from streamlit_drawable_canvas import st_canvas
from utils.helpers import load_image, get_ai_feedback
import time

# ---------- UTILS ----------
import io
from PIL import Image

def image_to_bytes(pil_img):
    buffer = io.BytesIO()
    pil_img.save(buffer, format="PNG")
    return buffer.getvalue()

def register_result(q, result):
    """Registra el resultado del estudiante en el sistema de progreso."""
    topic = q.get("topic", "General")

    # Registrar intento general
    st.session_state["progress"]["attempts"].append({
        "id": q["id"],
        "topic": topic,
        "result": result
    })

    # Contar por tema
    if topic not in st.session_state["progress"]["by_topic"]:
        st.session_state["progress"]["by_topic"][topic] = {"ok": 0, "fail": 0}

    if "correct" in result:
        st.session_state["progress"]["by_topic"][topic]["ok"] += 1
    else:
        st.session_state["progress"]["by_topic"][topic]["fail"] += 1

def reset_question_state(qid):
    """Remueve keys relacionadas con una pregunta para reiniciar estado."""
    keys = [f"first_expl_sent_{qid}", f"ai_feedback_{qid}", f"user_ms_{qid}",
            f"canvas_{qid}", f"points_{qid}", f"logic_{qid}", f"attempt_failed_{qid}", 
            f"failed_second_attempt_{qid}", f"second_ms_value_{qid}",
            f"solved_success_{qid}"]
    for key in list(st.session_state.keys()):
        if key.startswith(f"canvas_{qid}") or f"canvas_{qid}" in key:
            keys.append(key)
    for k in keys:
        if k in st.session_state:
            del st.session_state[k]

def find_next_index_same_topic(visuals, current_idx):
    """Busca el siguiente ejercicio del mismo topic."""
    if current_idx is None:
        return None
    current_topic = visuals[current_idx].get("topic")
    for i in range(current_idx + 1, len(visuals)):
        if visuals[i].get("topic") == current_topic:
            return i
    return None

def find_next_index_next_topic(visuals, current_idx):
    """Devuelve el primer índice que pertenezca a un topic distinto."""
    if current_idx is None:
        return 0 if len(visuals) > 0 else None
    current_topic = visuals[current_idx].get("topic")
    for i in range(current_idx + 1, len(visuals)):
        if visuals[i].get("topic") != current_topic:
            return i
    return None


# ---------- RENDER MODULE ----------

def render(data_db, api_key):
    """
    data_db: contenido completo de data/db.json (dict)
    api_key: str con OpenAI API key (o None)
    """
    if "visual_initialized" not in st.session_state:
        st.session_state.visual_initialized = True
        # Limpiar cualquier estado previo del canvas
        for key in list(st.session_state.keys()):
            if "canvas_" in key:
                del st.session_state[key]
        st.experimental_rerun()
    
    visuals = data_db.get("visual", [])
    
    if len(visuals) == 0:
        st.warning("No hay ejercicios visuales en la base de datos.")
        return

    # Inicializar índice global si no existe
    if "visual_idx" not in st.session_state:
        st.session_state["visual_idx"] = 0

    current_idx = st.session_state["visual_idx"]
    if current_idx >= len(visuals):
        st.session_state["progress"]["completed"] = True
        st.success("🎉 Has terminado todos los ejercicios. ¡Bien hecho!")
        
        # Botón extra para reiniciar si quieren volver a practicar
        if st.button("🔄 Volver a empezar"):
            st.session_state["visual_idx"] = 0
            st.session_state["progress"]["attempts"] = []
            st.session_state["progress"]["by_topic"] = {}
            st.session_state["progress"]["completed"] = False
            st.experimental_rerun()
       
        return

    q = visuals[current_idx]
    qid = q["id"]
    # crea un header general centrado en la parte superior
    if current_idx == 0:
        st.markdown("<h1 style='text-align: center;'>Módulo de Medición de Intervalos en ECG</h1>", unsafe_allow_html=True)
    # Escribe una bienvenida e instrucciones generales
    st.markdown("""
    Bienvenido al módulo de medición de intervalos en ECG. Aquí practicarás cómo identificar y medir correctamente diversos intervalos clave en un electrocardiograma.
    Sigue las instrucciones para cada ejercicio, utiliza el canvas para marcar los puntos relevantes, y recibe retroalimentación personalizada para mejorar tus habilidades.
    """)
    # Inicializar flags por pregunta
    if f"first_expl_sent_{qid}" not in st.session_state:
        st.session_state[f"first_expl_sent_{qid}"] = False
    if f"ai_feedback_{qid}" not in st.session_state:
        st.session_state[f"ai_feedback_{qid}"] = None
    if f"attempt_failed_{qid}" not in st.session_state:
        st.session_state[f"attempt_failed_{qid}"] = False
    
    # --- NUEVO: Flag para saber si ya lo resolvió correctamente ---
    if f"solved_success_{qid}" not in st.session_state:
        st.session_state[f"solved_success_{qid}"] = False
    
    st.header(f"📏 [{q.get('topic','')}] {q.get('title')}")
    st.info(q.get("instruction", ""))

    # ----- CANVAS ----
    
    # Congelamos el canvas en modo 'transform' si ya resolvió para que no mueva los puntos accidentalmente
    col1, col2, col3 = st.columns([1,3,1])
    canvas_key = f"canvas_{qid}"
    
                
    # Cargar imagen primero
    img_path = q.get("image")
    img = load_image(img_path)
    

    if img is None:
        st.error(f"No se pudo cargar la imagen: {img_path}")
        st.stop()

    # Limpieza suave del canvas
    if canvas_key in st.session_state:
        if isinstance(st.session_state[canvas_key], dict):
            st.session_state[canvas_key].pop("image", None)
            st.session_state[canvas_key].pop("objects", None)

    mode = "transform" if st.session_state[f"solved_success_{qid}"] else "circle"

    with col2:
        canvas_result = st_canvas(
            background_image=img.copy(),
            height=img.height,
            width=img.width,
            drawing_mode=mode,
            stroke_width=1,
            stroke_color="red",
            fill_color="rgba(255,0,0,0.7)",
            update_streamlit=True,
            key=canvas_key
    )


    if not (canvas_result and canvas_result.json_data):
        st.warning("Selecciona 2 puntos sobre el ECG (inicio y fin del intervalo).")
        return

    points = canvas_result.json_data.get("objects", [])
    # Imprimir coordenadas
    for i, point in enumerate(points):
        # Para círculos o rectángulos, suelen tener "left" y "top"
        x = point.get("left", None)
        y = point.get("top", None)
        st.write(f"Punto {i+1}: x={x}, y={y}")

    
    # =========================================================================
    # 🌟 MENU DE DECISIÓN (SI YA RESOLVIÓ CORRECTAMENTE)
    # =========================================================================
    if st.session_state[f"solved_success_{qid}"]:
        st.success(f"✅ ¡Correcto! El valor era {q.get('correct_ms')} ms.")
        
        st.markdown("### ¿Qué quieres hacer ahora?")
        
        col1, col2 = st.columns(2)
        
        # Buscar índices futuros
        next_same = find_next_index_same_topic(visuals, current_idx)
        next_topic = find_next_index_next_topic(visuals, current_idx)
        
        # --- OPCIÓN A: Mismo Tema ---
        with col1:
            if next_same is not None:
                st.info(f"Siguen más ejercicios de **{q.get('topic')}**.")
                if st.button(f"Practicar más {q.get('topic')}", type="primary"):
                    reset_question_state(qid)
                    if canvas_key in st.session_state:
                        del st.session_state[canvas_key]
                    st.session_state["visual_idx"] = next_same
                    st.experimental_rerun()
            else:
                st.write(f"Has terminado el tema {q.get('topic')}.")

        # --- OPCIÓN B: Siguiente Tema ---
        with col2:
            if next_topic is not None:
                new_topic_name = visuals[next_topic].get('topic')
                st.info(f"Saltar a **{new_topic_name}**.")
                if st.button(f"Pasar a {new_topic_name}"):
                    reset_question_state(qid)
                    if canvas_key in st.session_state:
                        del st.session_state[canvas_key]
                    st.session_state["visual_idx"] = next_topic
                    st.experimental_rerun()
            else:
                if next_same is None:
                    st.success("¡Has completado todo el módulo!")
                    if st.button("🏁 Finalizar módulo"):
                        # CORRECCIÓN: Avanzar el índice para que se active el resumen
                        st.session_state["visual_idx"] = len(visuals)
                        st.session_state["progress"]["completed"] = True
                        st.experimental_rerun()  # Usar experimental_rerun() en lugar de stop()

        

    # =========================================================================
    # 🔽 FLUJO DE RESPUESTA (Si no ha resuelto)
    # =========================================================================

    if len(points) != 2:
        st.warning("Selecciona exactamente 2 puntos para medir.")
        return

    # Extraer coordenadas X
    x1 = points[0].get("left", 0)
    x2 = points[1].get("left", 0)
    
    # Validar zona amplia (valid_zone_pairs)
    zones = q.get("valid_zone_pairs", [])
    if len(zones) > 0:
        found_valid_pair = False
        for zone in zones:
            xmin = zone.get("x_min", -1e9)
            xmax = zone.get("x_max", 1e9)
            if xmin <= x1 <= xmax and xmin <= x2 <= xmax:
                found_valid_pair = True
                break
        if not found_valid_pair:
            st.error("⚠️ Los dos puntos deben pertenecer al MISMO complejo P–QRS.")
            st.info("Tip: marca el inicio de la P y el inicio del QRS del mismo latido.")
            return

    # Input del estudiante
    user_ms = st.number_input("Escribe cuánto crees que mide el intervalo (ms):", min_value=0, max_value=2000, step=1, key=f"user_ms_{qid}")

    # --- BOTÓN PRIMER INTENTO ---
    if st.button("Enviar respuesta", key=f"btn_send_{qid}"):
        
        diff = abs(user_ms - q.get("correct_ms", 0))
        is_correct = diff <= q.get("tolerance_ms", 0)

        if is_correct:
            register_result(q, "correct_first_try")
            # En lugar de avanzar, activamos el menú de decisión
            st.session_state[f"solved_success_{qid}"] = True
            st.experimental_rerun()

        else:
            # Es incorrecto: activamos la bandera para mostrar explicación
            st.session_state[f"attempt_failed_{qid}"] = True
            st.error("❌ Respuesta incorrecta. Por favor explica cómo llegaste a ese valor.")

    
    # --- FEEDBACK Y SEGUNDO INTENTO ---
    if st.session_state.get(f"attempt_failed_{qid}", False) and not st.session_state.get(f"first_expl_sent_{qid}", False):
        
        explanation = st.text_area("Explica tu razonamiento (primer intento):", key=f"logic_input_{qid}")
        
        if st.button("Enviar explicación (pedir feedback)", key=f"btn_explain_{qid}"):
            if not explanation or not explanation.strip():
                st.warning("Escribe tu explicación antes de pedir feedback.")
            else:
                st.session_state[f"logic_{qid}"] = explanation
                st.session_state[f"first_expl_sent_{qid}"] = True 
                
                with st.spinner("Generando feedback docente..."):
                    if api_key:
                        # TU PROMPT ORIGINAL INTACTO
                        prompt_user = (
                            f"Eres un profesor experto en electrocardiografía. En esta pregunta, el estudiante debe lograr {q.get('question')} "
                            f"Estudiante midió {user_ms} ms en la imagen. "
                            f"Valor correcto: {q.get('correct_ms')} ms. Tolerancia: {q.get('tolerance_ms')} ms.\n\n"
                            f"Lógica del estudiante:\n{explanation}\n\n"
                            "Eres un docente experto: corrige la lógica, explica el error y da una instrucción breve de cómo medir correctamente SIN DECIRLE LA RESPUESTA CORRECTA en ningun momento."
                        )
                        try:
                            ai_fb = get_ai_feedback(api_key, "Eres un profesor experto en electrocardiografía.", prompt_user)
                        except Exception as e:
                            ai_fb = f"Error llamando a la IA: {e}"
                    else:
                        ai_fb = "No se proporcionó API Key. Pista: revisa si ubicaciones de puntos coinciden con inicio P y comienzo QRS."
                    
                    st.session_state[f"ai_feedback_{qid}"] = ai_fb
                
                st.experimental_rerun()

    # --- MOSTRAR FEEDBACK Y SEGUNDO INPUT ---
    if st.session_state.get(f"first_expl_sent_{qid}", False):
        ai_fb = st.session_state.get(f"ai_feedback_{qid}")

        st.markdown("### Retroalimentación docente (IA)")
        st.write(ai_fb or "Sin feedback disponible.")
        st.markdown("---")
        st.info("Segundo intento habilitado. Puedes escribir el nuevo valor.")

        second_ms = st.number_input(
            "Segundo intento (ms)",
            min_value=1, max_value=2000, step=1,
            value=st.session_state.get(f"second_ms_value_{qid}", 1),
            key=f"second_input_{qid}"
        )
        if second_ms:
            st.session_state[f"second_ms_value_{qid}"] = second_ms

        # --- BOTÓN SEGUNDO INTENTO ---
        if st.button("Enviar segundo intento", key=f"send_second_{qid}", type="primary"):

            if abs(second_ms - q.get("correct_ms", 0)) <= q.get("tolerance_ms", 5):
                register_result(q, "correct_second_try")
                # En lugar de avanzar, activamos el menú de decisión
                st.session_state[f"solved_success_{qid}"] = True
                st.experimental_rerun()

            else:
                # Falló el segundo: mostramos solución final
                register_result(q, "failed_second_try")
                st.session_state[f"failed_second_attempt_{qid}"] = True
                # No experimental_rerun, mostramos la solución abajo

        # --- SOLUCIÓN FINAL (SI FALLÓ TODO) ---
        if st.session_state.get(f"failed_second_attempt_{qid}", False):
            st.error(f"Segundo intento incorrecto. Respuesta correcta: {q.get('correct_ms')} ms.")

            if q.get("corrected_image"):
                st.image(load_image(q.get("corrected_image")), caption="Solución visual", use_column_width=True)

            # Botón para continuar (aquí usamos lógica automática o manual, dejaré automática para simplificar el fallo)
            if st.button("Continuar al siguiente →", type="primary", key=f"continue_final_{qid}"):
                next_idx = find_next_index_same_topic(visuals, current_idx)
                if next_idx is None:
                    next_idx = find_next_index_next_topic(visuals, current_idx)

                if next_idx is not None:
                    reset_question_state(qid)
                    if canvas_key in st.session_state:
                        del st.session_state[canvas_key]
                    st.session_state["visual_idx"] = next_idx
                    st.experimental_rerun()
                else:
                    st.success("¡Has terminado todo el módulo!")
                    st.session_state["progress"]["completed"] = True
                    st.session_state["visual_idx"] = len(visuals)
                    st.experimental_rerun()