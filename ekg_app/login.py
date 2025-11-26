import os
from PIL import Image
import streamlit as st

def login_screen():

    # El CSS para el centrado del texto contenedor
    st.markdown("""
    <style>
        /* Estilo para el contenedor que centra todo el contenido de la pantalla */
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
            max-width: 550px; /* Ancho máximo para el formulario */
            margin-left: auto;
            margin-right: auto;
            padding: 10px;
            border: 1px solid #f0f2f6;
            border-radius: 8px;
        }
        /* Color rojo para el asterisco de obligatorio */
        label span {
            color: red;
        }
    </style>
    """, unsafe_allow_html=True)

    # Creamos un único DIV que contendrá el Título y el Texto
    st.markdown('<div class="centered-content-container">', unsafe_allow_html=True)
    
    # ----------- TÍTULO -----------
    st.markdown("<h1>Bienvenido/a a</h1>", unsafe_allow_html=True)

    # ----------- LOGO (Centrado con st.columns y tamaño fijo) -----------
    c1, c2, c3 = st.columns([1, 1.11, 1]) 
    
    with c2: 
        try:
            logo = Image.open("assets/logo/logo.png")
            st.image(logo, width=600) 
        except FileNotFoundError:
            st.error("Error: No se encontró el logo en la ruta relativa 'assets/logo/logo.png'.")

    # ----------- TEXTO -----------
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

    # Cerramos el DIV que centra el texto
    st.markdown('</div>', unsafe_allow_html=True)

    # ----------- FORMULARIO DE LOGIN Y DATOS DEMOGRÁFICOS -----------     
    with st.form("login_form", clear_on_submit=False):
        st.subheader("Datos de Acceso e Investigación 📝")
        
        # 1. DATOS BÁSICOS
        name = st.text_input("Nombre completo *")
        dni = st.text_input("Cédula *")
        
        st.write("---")
        st.markdown("##### Información Académica y Demográfica (Obligatoria)")
        
        # 2. DATOS DEMOGRÁFICOS RELEVANTES
        
        # Fila 1: Sexo y País
        col_sexo, col_pais = st.columns(2)
        with col_sexo:
            sex = st.selectbox("Sexo *", ["", "Femenino", "Masculino", "Otro", "Prefiero no decir"])
        with col_pais:
            country = st.text_input("País de Residencia *")
            
        # Nivel de Formación General
        level = st.selectbox(
            "Nivel de Formación *", 
            ["", "Estudiante de Medicina Pregrado", "Internado/Rural", "Residente (Especialización)", "Graduado/Especialista"]
        )
        
        # CAMPO DE SEMESTRE MODIFICADO - MÁS SIMPLE
        term = None
        
        if level == "Graduado/Especialista":
            # Para graduados, establecer automáticamente como "Graduado"
            term = "Graduado"
            st.info("🔹 Nivel: Graduado/Especialista - El campo de semestre se ha establecido automáticamente")
            
        elif level in ["Estudiante de Medicina Pregrado", "Internado/Rural", "Residente (Especialización)"]:
            # Para estudiantes, mostrar selector de semestre
            term = st.selectbox(
                "Semestre actual *",
                ["", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14"],
                help="Selecciona el semestre que estás cursando actualmente (1 a 14)"
            )
        else:
            # Cuando no hay nivel seleccionado
            st.write("Selecciona tu nivel de formación para ver las opciones de semestre")
            
        university = st.text_input("Universidad/Institución *")
        
        # 3. EXPERIENCIA
        st.write("---")
        st.markdown("##### Experiencia y Recursos de Aprendizaje (Obligatorio)")

        experience = st.selectbox(
            "Experiencia previa en lectura de ECG (Auto-percepción) *",
            ["", "Principiante (Nula o muy baja)", "Intermedia (Clases teóricas/pocas prácticas)", "Avanzada (Práctica clínica regular)"]
        )
        
        formal_training = st.radio(
            "¿Has completado formalmente una asignatura o módulo de Cardiología/ECG en tu currículo? *",
            ["", "Sí", "No"]
        )
        
        clinical_frequency = st.selectbox(
            "¿Con qué frecuencia lees o revisas ECGs en un entorno clínico (prácticas, internado, residencia)? *",
            ["", "Nunca o Casi Nunca", "Mensualmente", "Semanalmente", "Diariamente"]
        )
        
        # 4. ACEPTACIÓN DE POLÍTICAS
        st.write("---")
        accept = st.checkbox(
            "Acepto el tratamiento de datos **anónimos** con fines académicos y de investigación (Ley 1581 de 2012 de Colombia) *"
        )
        
        # 5. BOTÓN DE ENVÍO (Centrado)
        b1, b2, b3 = st.columns([1, 2, 1])
        with b2:
            submit = st.form_submit_button("Ingresar")

    if submit:
        # Lógica de VALIDACIÓN MÁS ESTRICTA para campos obligatorios
        
        # Validar campos de texto/selectbox
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
        
        # 1. Comprobar campos de texto y selectbox vacíos
        if any(value == "" or value == [] or value is None for key, value in required_fields.items()):
            st.error("Por favor, llena **todos los campos obligatorios** marcados con (*).")
            return
            
        # 2. Validación específica para el campo de semestre
        if level == "Graduado/Especialista":
            # Para graduados, el término es automáticamente "Graduado"
            pass  # Ya está establecido arriba
            
        elif level in ["Estudiante de Medicina Pregrado", "Internado/Rural", "Residente (Especialización)"]:
            # Para otros niveles, debe tener un semestre seleccionado
            if not term or term == "":
                st.error("Debes seleccionar un semestre válido entre 1 y 14.")
                return
        else:
            st.error("Debes seleccionar un nivel de formación válido.")
            return

        # 3. Comprobar checkbox de aceptación
        if not accept:
            st.error("Debes aceptar la política de tratamiento de datos para continuar.")
            return
            
        # Si todo es válido, almacenar y continuar
        st.session_state["user_data"] = {
            "name": name, 
            "dni": dni,
            "sex": sex,
            "country": country,
            "level": level,
            "term": term, # Guardará el número (1-14) o la palabra "Graduado"
            "university": university,
            "experience": experience,
            "formal_training": formal_training,
            "clinical_frequency": clinical_frequency
        }
        st.success("✅ Datos guardados correctamente. Redirigiendo...")
        st.experimental_rerun()