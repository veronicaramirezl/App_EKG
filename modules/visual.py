import streamlit as st
import streamlit.components.v1 as components
from utils.helpers import load_image, get_ai_feedback
from PIL import Image
import io
import base64

# ---------- UTILS ----------
def pil_to_base64(img):
    """Convierte PIL Image a base64 para mostrar en HTML."""
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

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
    keys = [f"ai_feedback_{qid}", f"user_ms_{qid}",
            f"attempt_failed_{qid}", f"solved_success_{qid}", 
            f"second_ms_value_{qid}", f"first_expl_sent_{qid}", 
            f"logic_{qid}", f"failed_second_attempt_{qid}",
            f"show_success_message_{qid}", f"show_error_message_{qid}"]
    for k in keys:
        if k in st.session_state:
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

def create_canvas_component(img_base64, width, height, locked=False):
    """Crea un componente HTML con canvas centrado, botón visible y selección de herramienta con líneas dinámicas."""
    cursor_style = "not-allowed" if locked else "crosshair"
    pointer_events = "none" if locked else "auto"
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                margin: 0;
                padding: 0;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
            }}
            #canvasContainer {{
                position: relative;
                width: {width}px;
                display: inline-block;
            }}
            #bgImage {{
                display: block;
                width: 100%;
                height: auto;
                pointer-events: none;
            }}
            #drawCanvas {{
                position: absolute;
                top: 0;
                left: 0;
                width: {width}px;
                height: {height}px;
                cursor: {cursor_style};
                pointer-events: {pointer_events};
            }}
            #controls {{
                display: flex;
                justify-content: flex-start;
                margin-top: 8px;
                gap: 10px;
            }}
            #toolSelect, #clearBtn {{
                padding: 6px 12px;
                font-size: 14px;
                border-radius: 4px;
                cursor: pointer;
            }}
            #clearBtn {{
                background: #ff4444;
                color: white;
                border: none;
            }}
        </style>
    </head>
    <body>
        <div id="canvasContainer">
            <img id="bgImage" src="data:image/png;base64,{img_base64}" width="{width}" height="{height}">
            <canvas id="drawCanvas" width="{width}" height="{height}"></canvas>
            <div id="controls">
                {"<select id='toolSelect'><option value='circle'>Círculo</option><option value='line'>Línea</option></select>" if not locked else ""}
                {"<button id='clearBtn'>🗑️ Limpiar marcas</button>" if not locked else ""}
            </div>
        </div>
        
        <script>
            const canvas = document.getElementById('drawCanvas');
            const ctx = canvas.getContext('2d');
            const locked = {str(locked).lower()};
            let circles = [];
            let lines = [];
            let currentTool = "circle";
            let lineStart = null;

            const toolSelect = document.getElementById('toolSelect');
            toolSelect?.addEventListener('change', (e) => {{
                currentTool = e.target.value;
                lineStart = null;
            }});

            function drawCircle(x, y) {{
                ctx.beginPath();
                ctx.arc(x, y, 3, 0, 2 * Math.PI);
                ctx.fillStyle = 'rgba(255, 0, 0, 0.3)';
                ctx.fill();
                ctx.strokeStyle = '#FF0000';
                ctx.lineWidth = 3;
                ctx.stroke();
            }}

            function drawLines() {{
                ctx.strokeStyle = '#FF0000';
                ctx.lineWidth = 3;
                lines.forEach(line => {{
                    ctx.beginPath();
                    ctx.moveTo(line.x1, line.y1);
                    ctx.lineTo(line.x2, line.y2);
                    ctx.stroke();
                }});
            }}

            function redrawAll(tempLine=null) {{
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                drawLines();
                circles.forEach(c => drawCircle(c.x, c.y));
                if(tempLine) {{
                    ctx.beginPath();
                    ctx.moveTo(tempLine.x1, tempLine.y1);
                    ctx.lineTo(tempLine.x2, tempLine.y2);
                    ctx.strokeStyle = '#FF0000';
                    ctx.lineWidth = 1;
                    ctx.stroke();
                }}
            }}

            function getCanvasOffsetScale() {{
                const rect = canvas.getBoundingClientRect();
                const scaleX = canvas.width / rect.width;
                const scaleY = canvas.height / rect.height;
                return {{ rect, scaleX, scaleY }};
            }}

            if (!locked) {{
                function handlePointer(x, y) {{
                    if(currentTool === "circle") {{
                        circles.push({{x, y}});
                    }} else if(currentTool === "line") {{
                        if(lineStart === null) {{
                            lineStart = {{x, y}};
                        }} else {{
                            lines.push({{x1: lineStart.x, y1: lineStart.y, x2: x, y2: y}});
                            lineStart = null;
                        }}
                    }}
                    redrawAll();
                }}

                canvas.addEventListener('mousedown', e => {{
                    const {{ rect, scaleX, scaleY }} = getCanvasOffsetScale();
                    const x = (e.clientX - rect.left) * scaleX;
                    const y = (e.clientY - rect.top) * scaleY;
                    handlePointer(x, y);
                }});

                canvas.addEventListener('mousemove', e => {{
                    if(currentTool === "line" && lineStart) {{
                        const {{ rect, scaleX, scaleY }} = getCanvasOffsetScale();
                        const x = (e.clientX - rect.left) * scaleX;
                        const y = (e.clientY - rect.top) * scaleY;
                        redrawAll({{x1: lineStart.x, y1: lineStart.y, x2: x, y2: y}});
                    }}
                }});

                canvas.addEventListener('touchstart', e => {{
                    e.preventDefault();
                    const touch = e.touches[0];
                    const {{ rect, scaleX, scaleY }} = getCanvasOffsetScale();
                    const x = (touch.clientX - rect.left) * scaleX;
                    const y = (touch.clientY - rect.top) * scaleY;
                    handlePointer(x, y);
                }});

                const clearBtn = document.getElementById('clearBtn');
                clearBtn?.addEventListener('click', () => {{
                    circles = [];
                    lines = [];
                    lineStart = null;
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                }});
            }}
        </script>
    </body>
    </html>
    """
    return html_code

# ---------- RENDER MODULE ----------
def render(data_db, api_key):
    """Módulo visual con dibujo libre usando HTML Canvas puro."""
    
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
        st.markdown("""
        <h1 style='text-align: center; margin-top: 50px;'>Módulo de Medición de Intervalos en ECG</h1>
        """, unsafe_allow_html=True)
        st.markdown("""
        **Instrucciones:**
        1. Dibuja círculos o líneas para guiarte en el ECG. Puedes marcar el inicio y fin del intervalo o contar la cuadricula, lo que necesites.
        2. Escribe tu medición en milisegundos o en lpm según se indique.
        3. La IA revisará tu explicación  y te dará feedback en caso de que necesites ayuda. Después podrás intentar de nuevo.
        """)

    st.markdown(f"<h2 style='margin-top:40px; margin-bottom:20px;'>📏 {q.get('title')}</h2>", unsafe_allow_html=True)
    st.info(q.get("instruction", ""))

    # Cargar imagen
    img = load_image(q.get("image"))
    if img is None:
        st.error(f"No se pudo cargar la imagen: {q.get('image')}")
        st.stop()

    locked = st.session_state[f"solved_success_{qid}"]
    
    # Convertir imagen a base64
    img_base64 = pil_to_base64(img)
    
    # Mostrar canvas HTML
    canvas_html = create_canvas_component(img_base64, img.width, img.height, locked)
    components.html(canvas_html, height=img.height + 60, scrolling=False)

    st.markdown("---")

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

    # Feedback IA después del primer intento fallido (SOLO CON EXPLICACIÓN DE TEXTO)
    if st.session_state.get(f"attempt_failed_{qid}") and not st.session_state.get(f"first_expl_sent_{qid}"):
        st.markdown("---")
        explanation = st.text_area(
            "Explica cómo llegaste a tu respuesta (ej: conté 3 cuadritos grandes y cada uno mide 200ms):", 
            key=f"logic_input_{qid}",
            height=100
        )
        if st.button("Enviar explicación y pedir feedback", key=f"btn_explain_{qid}", type="secondary"):
            if not explanation.strip():
                st.warning("Escribe tu explicación antes de pedir feedback.")
            else:
                st.session_state[f"logic_{qid}"] = explanation
                st.session_state[f"first_expl_sent_{qid}"] = True
                
                # IMPORTANTE: Solo enviamos la explicación de texto, NO la imagen
                with st.spinner("🤖 La IA está revisando tu explicación..."):
                    try:
                        # Aquí llamamos a una función simplificada que solo usa texto
                        ai_fb = get_ai_feedback(
                            api_key=api_key,
                            instruction=q.get("instruction"),
                            user_input=explanation,
                            system_prompt=f"""Tu eres un profesor experto en electrocardiografía. Revisa el ejercicio que le proponemos al estudiante. El mensaje debe ser conciso pero fácil de entender. Debes dirigirte al estudiante en segunda persona.

                    El estudiante debe {q.get('instruction')}.

                    Ha marcado puntos en la imagen y midió {user_ms} ms. El valor correcto es {q.get('correct_ms')} ms (tolerancia: ±{q.get('tolerance_ms')} ms).

                    Su razonamiento para haberlo hecho así es el siguiente: {explanation}

                    Analiza la imagen y, sin decir nunca la respuesta exacta, responde a las siguientes preguntas:
                    - Si hay errores, explica QUÉ está mal y CÓMO corregirlo (sin dar la respuesta exacta). 
                    - Dónde fue el error? Tal vez la marca no fue adecuada, tal vez sí fue adecuada pero la medición fue incorrecta, etc.
                    - Dale una pista para que pueda mejorar su medición, tal vez diciendo que se quedo corto o se pasó pero sin dar la respuesta exacta.

                    Sé específico sobre la ubicación de los puntos en el complejo ECG.
                    """,
                            context=f"El estudiante midió {user_ms} ms pero la respuesta correcta es {q.get('correct_ms')} ms."
                        )
                        st.session_state[f"ai_feedback_{qid}"] = ai_fb
                    except Exception as e:
                        st.session_state[f"ai_feedback_{qid}"] = f"Error llamando a la IA: {e}"

                    st.rerun()


    # Segundo intento
    if st.session_state.get(f"first_expl_sent_{qid}"):
        st.markdown("---")
        st.markdown("### 💡 Retroalimentación del profesor (IA)")
        st.info(st.session_state.get(f"ai_feedback_{qid}", "Sin feedback disponible."))
        
        st.markdown("### 🔄 Segundo intento")
        st.write("Basándote en el feedback, ingresa tu nueva medición:")

        second_ms = st.number_input(
            "Segundo intento (ms)",
            min_value=1,
            max_value=2000,
            step=1,
            value=st.session_state.get(f"second_ms_value_{qid}", 1),
            key=f"second_input_{qid}"
        )
        st.session_state[f"second_ms_value_{qid}"] = second_ms

        if st.button("Enviar segundo intento", key=f"send_second_{qid}", type="primary"):
            if abs(second_ms - q.get("correct_ms", 0)) <= q.get("tolerance_ms", 5):
                register_result(q, "correct_second_try")
                st.session_state[f"solved_success_{qid}"] = True
                st.session_state[f"show_success_message_{qid}"] = True
            else:
                register_result(q, "failed_second_try")
                st.session_state[f"failed_second_attempt_{qid}"] = True
                st.session_state[f"show_error_message_{qid}"] = True
            st.rerun()

        # Mensajes post-segundo intento
        if st.session_state.get(f"show_success_message_{qid}"):
            st.success(f"✅ ¡Excelente! Lo resolviste correctamente. El valor era {q.get('correct_ms')} ms.")

        if st.session_state.get(f"show_error_message_{qid}"):
            st.error(f"❌ Segundo intento incorrecto. Respuesta correcta: {q.get('correct_ms')} ms.")
            
            corrected_image_path = q.get("corrected_image")
            if corrected_image_path:
                try:
                    corrected_img = load_image(corrected_image_path)
                    if corrected_img:
                        st.image(corrected_img, caption="📋 Imagen de referencia con la solución correcta", use_container_width=True)
                except:
                    pass

    # Botones de navegación
    if st.session_state.get(f"solved_success_{qid}") or st.session_state.get(f"failed_second_attempt_{qid}"):
        
        same_topic_available = find_next_index_same_topic(visuals, current_idx) is not None
        next_topic_available = find_next_index_next_topic(visuals, current_idx) is not None
        
        # Si acertó a la primera
        attempts = [a for a in st.session_state["progress"]["attempts"] if a.get("id") == qid]
        first_try_success = any("correct_first_try" == a.get("result") for a in attempts)
        
        if st.session_state.get(f"solved_success_{qid}") and first_try_success:
            st.success(f"✅ ¡Excelente! Respuesta correcta a la primera. El valor correcto era {q.get('correct_ms')} ms.")
            st.markdown("---")
            st.subheader("¿Qué quieres hacer ahora?")
            if next_topic_available and same_topic_available:
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📚 Otra pregunta del mismo tema", key=f"same_{qid}", use_container_width=True):
                        next_idx = find_next_index_same_topic(visuals, current_idx)
                        reset_question_state(qid)
                        st.session_state["visual_idx"] = next_idx
                        st.rerun()
                with col2:
                    if st.button("🚀 Avanzar al siguiente tema", key=f"next_{qid}", use_container_width=True):
                        next_idx = find_next_index_next_topic(visuals, current_idx)
                        reset_question_state(qid)
                        st.session_state["visual_idx"] = next_idx
                        st.rerun()
            elif next_topic_available:
                if st.button("🚀 Avanzar al siguiente tema", key=f"next_solo_{qid}", use_container_width=True):
                    next_idx = find_next_index_next_topic(visuals, current_idx)
                    reset_question_state(qid)
                    st.session_state["visual_idx"] = next_idx
                    st.rerun()
            elif same_topic_available:
                if st.button("📚 Otra pregunta del mismo tema", key=f"same_solo_{qid}", use_container_width=True):
                    next_idx = find_next_index_same_topic(visuals, current_idx)
                    reset_question_state(qid)
                    st.session_state["visual_idx"] = next_idx
                    st.rerun()
        else:
            # Acertó en segundo intento o falló ambos
            if same_topic_available:
                if st.button("➡️ Continuar", key=f"cont_{qid}", use_container_width=True):
                    next_idx = find_next_index_same_topic(visuals, current_idx)
                    reset_question_state(qid)
                    st.session_state["visual_idx"] = next_idx
                    st.rerun()
            elif next_topic_available:
                if st.button("➡️ Continuar al siguiente tema", key=f"cont_next_{qid}", use_container_width=True):
                    next_idx = find_next_index_next_topic(visuals, current_idx)
                    reset_question_state(qid)
                    st.session_state["visual_idx"] = next_idx
                    st.rerun()
            else:
                if st.button("🏁 Finalizar módulo", key=f"finish_{qid}", use_container_width=True):
                    st.session_state["progress"]["completed"] = True
                    st.session_state["visual_idx"] = len(visuals)
                    st.rerun()

