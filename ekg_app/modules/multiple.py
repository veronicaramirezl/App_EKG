import streamlit as st

def register_result_mc(q, selected):
    """Guarda resultado en la estructura global de progreso."""
    topic = q.get("topic", "Teoría ECG")

    result = "correct" if selected == q["correct_answer"] else "fail"

    # Registrar intento total
    st.session_state["progress"]["attempts"].append({
        "id": q["id"],
        "topic": topic,
        "result": result
    })

    # Registrar por tema
    if topic not in st.session_state["progress"]["by_topic"]:
        st.session_state["progress"]["by_topic"][topic] = {"ok": 0, "fail": 0}

    if result == "correct":
        st.session_state["progress"]["by_topic"][topic]["ok"] += 1
    else:
        st.session_state["progress"]["by_topic"][topic]["fail"] += 1


def render(data_list):
    """Renderiza todo el módulo de preguntas de selección múltiple."""
    if "mc_idx" not in st.session_state:
        st.session_state["mc_idx"] = 0

    idx = st.session_state["mc_idx"]

    # Si ya no hay más preguntas
    if idx >= len(data_list):
        st.success("🎉 ¡Completaste todas las preguntas teóricas!")
        st.session_state["progress"]["completed"] = True
        return

    q = data_list[idx]

    st.header("📝 Pregunta Teórica")
    st.markdown(f"### {q['question']}")

    options = list(q["options"].keys())

    # Mantener selección por pregunta
    selected_key = f"mc_sel_{q['id']}"
    selected = st.radio(
        "Selecciona la respuesta:",
        options,
        index=None,
        key=selected_key
    )

    # Estado: ¿ya respondió esta pregunta?
    answered_key = f"mc_answered_{q['id']}"
    if answered_key not in st.session_state:
        st.session_state[answered_key] = False

    # Mostrar botón solo si NO ha respondido todavía
    if not st.session_state[answered_key]:
        if st.button("Comprobar", key=f"btn_{q['id']}"):
            if not selected:
                st.warning("Selecciona una opción antes de continuar.")
                return
            
            st.session_state[answered_key] = True
            register_result_mc(q, selected)
            st.experimental_rerun()

    # Cuando ya respondió → mostrar explicación
    else:
        explanation = q["options"][selected]
        correct = (selected == q["correct_answer"])

        if correct:
            st.success(f"✅ Correcto: {explanation}")
        else:
            st.error(f"❌ Incorrecto: {explanation}")
            st.info(f"👉 La respuesta correcta era: **{q['correct_answer']}**")
        
        st.markdown("---")
        if st.button("➡️ Siguiente pregunta", key=f"next_{q['id']}"):
            st.session_state["mc_idx"] += 1
            st.experimental_rerun()
