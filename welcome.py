# welcome.py
import streamlit as st

def welcome_screen():
    """
    Pantalla de bienvenida que explica la iniciativa y los módulos disponibles
    """
    
    st.markdown("""
    <div style='background: linear-gradient(135deg, #E63946, #ffb8bd); 
                padding: 3rem 2rem; 
                border-radius: 20px; 
                text-align: center;
                box-shadow: 0 15px 50px rgba(230, 57, 70, 0.5);
                margin-bottom: 2rem;'>
        <h1 style='color: white; margin: 0; font-size: 3rem;'>🫀 Aureus Cardio</h1>
        <p style='color: #FFE5E7; font-size: 1.3rem; margin: 1rem 0 0 0; font-weight: 500;'>
            Sistema Avanzado de Entrenamiento en Electrocardiografía
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sección: Sobre la Iniciativa
    st.markdown("## 🎯 Sobre Esta Iniciativa")
    
    st.markdown("""
    <div style='background-color: rgba(230, 57, 70, 0.05); 
                padding: 1.5rem; 
                border-radius: 15px; 
                border-left: 5px solid #E63946;
                margin-bottom: 2rem;'>
        <p style='color: #E5E5E5; font-size: 1.1rem; line-height: 1.8; margin: 0;'>
            <strong>Aureus Cardio</strong> es una plataforma educativa diseñada para mejorar la 
            <strong style='color: #E63946;'>enseñanza y dominio de la electrocardiografía</strong> 
            en estudiantes y profesionales de la salud. 
            <br><br>
            Utilizando metodologías de aprendizaje activo y retroalimentación asistida por IA, 
            nuestro objetivo es que desarrolles habilidades prácticas y confianza en la 
            <strong style='color: #06D6A0;'>interpretación de ECG</strong>, una competencia 
            esencial en la práctica clínica.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Sección: Módulos de Aprendizaje
    st.markdown("## 📚 Módulos de Aprendizaje")
    st.markdown("""
    <p style='color: #B0B0B0; font-size: 1rem; margin-bottom: 2rem;'>
        Selecciona el módulo con el que deseas comenzar. Podrás moverte libremente entre ellos en cualquier momento.
    </p>
    """, unsafe_allow_html=True)
    
    # Módulo 1: Medición Visual
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, rgba(255, 209, 102, 0.15), rgba(255, 165, 0, 0.15)); 
                    padding: 1.5rem; 
                    border-radius: 15px; 
                    border: 2px solid #FFD166;
                    height: 400px;
                    display: flex;
                    flex-direction: column;'>
            <div style='text-align: center; font-size: 3rem; margin-bottom: 1rem;'>📏</div>
            <h3 style='color: #FFD166; text-align: center; margin: 0 0 1rem 0;'>
                Medición de Intervalos
            </h3>
            <p style='color: #E5E5E5; font-size: 0.95rem; line-height: 1.6; flex-grow: 1;'>
                Aprende a medir con precisión los <strong>intervalos y segmentos</strong> del ECG:
                <br><br>
                • Práctica con trazos reales<br>
                • Herramienta de medición interactiva<br>
                • Feedback inmediato sobre tu técnica<br>
                • Dominio de PR, QRS, QT y más
            </p>
            <p style='color: #FFD166; font-size: 0.85rem; text-align: center; margin: 1rem 0 0 0;'>
                ⏱️ Nivel: Fundamental
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Comenzar Módulo Visual", key="btn_visual", use_container_width=True):
            st.session_state["welcome_completed"] = True
            st.session_state["selected_module"] = "📏 Medición de Intervalos"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, rgba(6, 214, 160, 0.15), rgba(4, 138, 129, 0.15)); 
                    padding: 1.5rem; 
                    border-radius: 15px; 
                    border: 2px solid #06D6A0;
                    height: 400px;
                    display: flex;
                    flex-direction: column;'>
            <div style='text-align: center; font-size: 3rem; margin-bottom: 1rem;'>✅</div>
            <h3 style='color: #06D6A0; text-align: center; margin: 0 0 1rem 0;'>
                Selección Múltiple
            </h3>
            <p style='color: #E5E5E5; font-size: 0.95rem; line-height: 1.6; flex-grow: 1;'>
                Evalúa tu conocimiento con <strong>casos clínicos</strong> estructurados:
                <br><br>
                • Preguntas basadas en escenarios reales<br>
                • Análisis de ritmos y arritmias<br>
                • Identificación de patrones ECG<br>
                • Retroalimentación detallada
            </p>
            <p style='color: #06D6A0; font-size: 0.85rem; text-align: center; margin: 1rem 0 0 0;'>
                ⏱️ Nivel: Intermedio
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Comenzar Selección Múltiple", key="btn_multiple", use_container_width=True):
            st.session_state["welcome_completed"] = True
            st.session_state["selected_module"] = "✅ Selección Múltiple"
            st.rerun()
    
    with col3:
        st.markdown("""
        <div style='background: linear-gradient(135deg, rgba(168, 50, 255, 0.15), rgba(108, 92, 231, 0.15)); 
                    padding: 1.5rem; 
                    border-radius: 15px; 
                    border: 2px solid #A832FF;
                    height: 400px;
                    display: flex;
                    flex-direction: column;'>
            <div style='text-align: center; font-size: 3rem; margin-bottom: 1rem;'>🩺</div>
            <h3 style='color: #A832FF; text-align: center; margin: 0 0 1rem 0;'>
                Diagnóstico Completo
            </h3>
            <p style='color: #E5E5E5; font-size: 0.95rem; line-height: 1.6; flex-grow: 1;'>
                Desarrolla tu <strong>razonamiento clínico</strong> con análisis profundos:
                <br><br>
                • Interpretación libre de ECG completos<br>
                • Justificación de tus diagnósticos<br>
                • Evaluación con IA especializada<br>
                • Feedback personalizado y detallado
            </p>
            <p style='color: #A832FF; font-size: 0.85rem; text-align: center; margin: 1rem 0 0 0;'>
                ⏱️ Nivel: Avanzado
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Comenzar Diagnóstico", key="btn_open", use_container_width=True):
            st.session_state["welcome_completed"] = True
            st.session_state["selected_module"] = "🩺 Diagnóstico Completo"
            st.rerun()
    
    st.markdown("---")
    
    # Consejos y Recomendaciones
    st.markdown("## 💡 Consejos para Aprovechar al Máximo")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style='background-color: rgba(6, 214, 160, 0.05); 
                    padding: 1.5rem; 
                    border-radius: 10px; 
                    border-left: 4px solid #06D6A0;'>
            <h4 style='color: #06D6A0; margin-top: 0;'>✨ Durante el Entrenamiento</h4>
            <ul style='color: #E5E5E5; line-height: 1.8;'>
                <li>Tómate tu tiempo para analizar cada caso</li>
                <li>Lee el feedback cuidadosamente</li>
                <li>Practica las áreas donde tengas dificultades</li>
                <li>Usa el API Key de OpenAI para feedback con IA</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background-color: rgba(255, 209, 102, 0.05); 
                    padding: 1.5rem; 
                    border-radius: 10px; 
                    border-left: 4px solid #FFD166;'>
            <h4 style='color: #FFD166; margin-top: 0;'>🎯 Navegación</h4>
            <ul style='color: #E5E5E5; line-height: 1.8;'>
                <li>Puedes cambiar de módulo en cualquier momento</li>
                <li>Tu progreso se guarda automáticamente</li>
                <li>Revisa tu rendimiento en la barra lateral</li>
                <li>Completa todos los módulos para certificación</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Footer motivacional
    st.markdown("""
    <div style='background: linear-gradient(135deg, rgba(230, 57, 70, 0.1), rgba(6, 214, 160, 0.1)); 
                padding: 2rem; 
                border-radius: 15px; 
                text-align: center;
                margin-top: 2rem;'>
        <p style='color: #E5E5E5; font-size: 1.2rem; margin: 0; font-weight: 300;'>
            "La competencia en ECG no es un don, es una habilidad que se desarrolla con práctica deliberada"
        </p>
        <p style='color: #E63946; font-size: 1rem; margin: 1rem 0 0 0; font-weight: 600;'>
            ¡Comienza tu entrenamiento ahora! 🚀
        </p>
    </div>
    """, unsafe_allow_html=True)