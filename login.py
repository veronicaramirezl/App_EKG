import os
from PIL import Image
import streamlit as st

def login_screen():

    # ---------- CSS ----------
    st.markdown("""
    <style>
        .centered-content-container {
            max-width: 750px; 
            margin-left: auto;
            margin-right: auto;
            padding: 20px;
        }
        h1 {
            text-align: center;
        }
        .centered-content-container p {
            text-align: left;
            padding: 0 15px; 
        }
        .stForm {
            padding: 10px;
            border: 1px solid #f0f2f6;
            border-radius: 8px;
        }
        label span {
            color: red;
        }
    </style>
    """, unsafe_allow_html=True)

    # ---------- CONTENEDOR PRINCIPAL ----------
    st.markdown('<div class="centered-content-container">', unsafe_allow_html=True)
    st.markdown("<h1>Bienvenido/a a</h1>", unsafe_allow_html=True)

    # ---------- LOGO ----------
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        logo_col1, logo_col2, logo_col3 = st.columns([0.7, 4, 1])
        with logo_col2:
            try:
                logo = Image.open("assets/logo/logo.png")
                st.image(logo, width=900)
            except FileNotFoundError:
                st.error("Error: No se encontró el logo en la ruta relativa 'assets/logo/logo.png'.")

    # ---------- TEXTO ----------
    st.markdown("""
    <p style="color:#333; font-size:18px; line-height:1.55; margin-top:15px;">
        Sabemos que interpretar un electrocardiograma puede ser un reto durante la formación médica. <br>
        Esta plataforma integra <b>Inteligencia Artificial</b> para ayudarte a aprender de forma 
        más clara, guiada y personalizada.
    </p>
    <p style="color:#333; font-size:17px; line-height:1.55;">
        Al continuar, aceptas que tus respuestas y datos de uso sean tratados de forma 
        <b>anónima</b> con fines académicos y de investigación,
        conforme a la <b>Ley 1581 de 2012</b> de Protección de Datos Personales en Colombia 
        y sus decretos reglamentarios.
    </p>
    <p style="color:#555; font-size:17px; line-height:1.55; margin-top:10px;">
        ¡Gracias por apoyar este proyecto y contribuir al mejoramiento 
        del aprendizaje del ECG en estudiantes de medicina!
    </p>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ---------- FORMULARIO ----------
    with st.form("login_form", clear_on_submit=False):
        st.subheader("Datos de Acceso e Investigación 📝")
        name = st.text_input("Nombre completo *")
        dni = st.text_input("Cédula *")

        st.write("---")
        st.markdown("##### Información Demográfica y Académica (Obligatoria)")

        col_sexo, col_pais = st.columns(2)
        with col_sexo:
            sex = st.selectbox("Sexo *", ["", "Femenino", "Masculino", "Otro", "Prefiero no decir"])
        with col_pais:
            country = st.text_input("País de Residencia *")

        university = st.text_input("Universidad/Institución *")

        # Nivel de formación dentro del form
        level = st.selectbox(
            "Nivel de Formación *", 
            ["", "Estudiante de Medicina Pregrado (Semestre I-IV)", "Estudiante de Medicina Pregrado (Semestre V-X)", "Internado/Rural", "Residente (Especialización)", "Graduado/Especialista"]
        )


        st.write("---")
        st.markdown("##### Experiencia y Recursos de Aprendizaje (Obligatorio)")

        experience = st.selectbox(
            "Experiencia previa en lectura de ECG (Auto-percepción) *",
            ["", "Principiante (Nula o muy baja)", "Intermedia (Clases teóricas/pocas prácticas)", "Avanzada (Práctica clínica regular)"]
        )

        formal_training = st.radio(
            "¿Has completado formalmente una asignatura o módulo de Cardiología/ECG en tu currículo? *",
            ["Sí", "No"]
        )

        clinical_frequency = st.selectbox(
            "¿Con qué frecuencia lees o revisas ECGs en un entorno clínico (prácticas, internado, residencia)? *",
            ["", "Nunca o Casi Nunca", "Mensualmente", "Semanalmente", "Diariamente"]
        )

        st.write("---")
        accept = st.checkbox(
            "Acepto el tratamiento de datos **anónimos** con fines académicos y de investigación (Ley 1581 de 2012 de Colombia) *"
        )

        b1, b2, b3 = st.columns([1, 2, 1])
        with b1:
            submit = st.form_submit_button("Ingresar")

    # ---------- VALIDACIÓN ----------
    if submit:
        required_fields = {
            "name": name,
            "dni": dni,
            "sex": sex,
            "country": country,
            "level": level,
            "university": university,
            "experience": experience,
            "formal_training": formal_training,
            "clinical_frequency": clinical_frequency,
        }

        if any(value == "" or value is None for key, value in required_fields.items()):
            st.error("Por favor, llena **todos los campos obligatorios** marcados con (*).")
            return


        if not accept:
            st.error("Debes aceptar la política de tratamiento de datos para continuar.")
            return

        st.session_state["user_data"] = {
            "name": name,
            "dni": dni,
            "sex": sex,
            "country": country,
            "level": level,
            "university": university,
            "experience": experience,
            "formal_training": formal_training,
            "clinical_frequency": clinical_frequency
        }

        st.success("✅ Datos validados correctamente. Redirigiendo...")
        st.rerun()
