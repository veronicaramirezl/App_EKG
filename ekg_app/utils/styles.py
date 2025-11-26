def load_css():
    """
    Retorna CSS personalizado para CardioSim Pro
    Diseño compacto, elegante y altamente legible
    """
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&family=Inter:wght@400;500&display=swap');

    :root{
        --primary-red: #E63946;
        --soft-red: #FF8B94;
        --bg-main: #FAFAFA;
        --bg-card: #FFFFFF;
        --text-dark: #22272A; /* texto más oscuro para legibilidad */
        --text-muted: #586067;
        --border: #E6E9EC;
        --shadow: rgba(0,0,0,0.06);
        --gradient: linear-gradient(135deg,#E63946 0%,#FF8B94 100%);
    }

    /* Fondo global y tipografia */
    .stApp{
        background: linear-gradient(180deg,#FAFAFA 0%, #FFF8F9 100%);
        font-family: 'Poppins', sans-serif;
        color: var(--text-dark);
    }

    /* Sidebar: compacto y legible */
    [data-testid="stSidebar"]{
        background: #FFFFFF;
        border-right: 1px solid var(--border);
        padding: 1rem 0.75rem;
    }
    [data-testid="stSidebar"] .stMarkdown h1{
        color: var(--primary-red);
        font-size: 1.25rem;
        font-weight: 600;
        text-align: center;
        margin: 0.4rem 0 1rem 0;
    }
    [data-testid="stSidebar"] label{
        color: var(--text-dark) !important;
        font-weight: 500;
        font-size: 0.95rem;
    }
    [data-testid="stSidebar"] [data-testid^="stBlock"]{
        padding: 0.75rem;
        border-radius: 10px;
        background-color: #FFF9FA;
        margin-bottom: 1rem;
        border: 1px solid rgba(230,57,70,0.06);
    }

    /* Texto general */
    .stMarkdown, .element-container, p, li, span {
        color: var(--text-dark) !important;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    strong, b { font-weight: 600; color: var(--text-dark); }

    /* Encabezados más contenidos para evitar espacios grandes */
    h1{ font-size: 1.9rem; margin: 0.25rem 0 0.6rem 0; font-weight: 700; }
    h2{ font-size: 1.25rem; margin: 1rem 0 0.6rem 0; padding-bottom: 0.35rem; color: var(--primary-red); border-bottom: 2px solid rgba(230,57,70,0.06); }
    h3{ font-size: 1.05rem; margin: 0.6rem 0; color: var(--soft-red); }

    /* Banner - reducido para ocupar menos espacio pero seguir destacado */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"]:first-child{
        background: var(--gradient);
        padding: 1.4rem 1rem;
        border-radius: 14px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(230,57,70,0.12);
        margin-bottom: 1.25rem;
        border: 1px solid rgba(255,255,255,0.18);
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.4rem;
    }
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"]:first-child h1{
        color: #fff !important;
        font-size: 1.6rem;
        margin: 0;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.12);
    }
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"]:first-child p{
        color: rgba(255,255,255,0.95) !important;
        font-size: 0.98rem;
        margin: 0;
        max-width: 760px;
    }

    /* Tarjetas de contenido - más compactas */
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"]:not(:first-child){
        background-color: var(--bg-card);
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 4px 16px var(--shadow);
        border: 1px solid var(--border);
        margin-bottom: 0.9rem;
    }

    .info-card{
        padding: 0.9rem 1rem;
        border-radius: 12px;
        border-left: 4px solid var(--primary-red);
        background: linear-gradient(90deg,#FFFFFF 0%, #FFF9FA 100%);
        box-shadow: 0 4px 14px var(--shadow);
        margin-bottom: 1rem;
    }

    /* Alerts y notificaciones */
    .stAlert{
        background-color: var(--bg-card) !important;
        border-radius: 10px;
        padding: 0.8rem !important;
        box-shadow: 0 2px 10px var(--shadow);
        border: 1px solid var(--border);
    }

    /* Botones - compactos */
    .stButton > button{
        background: var(--gradient);
        color: #fff;
        border-radius: 10px;
        padding: 0.55rem 1.4rem;
        font-weight: 600;
        font-size: 0.95rem;
        box-shadow: 0 6px 16px rgba(230,57,70,0.16);
        transition: transform 0.18s ease, box-shadow 0.18s ease;
    }
    .stButton > button:hover{
        transform: translateY(-2px);
        box-shadow: 0 10px 26px rgba(230,57,70,0.22);
    }

    /* Inputs - mayor contraste y menos alto */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea textarea {
        background-color: var(--bg-card) !important;
        color: var(--text-dark) !important;
        border: 1.5px solid var(--border) !important;
        border-radius: 10px;
        padding: 0.6rem;
        font-size: 0.95rem;
        font-family: 'Inter', sans-serif;
    }
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea textarea:focus {
        border-color: var(--primary-red) !important;
        box-shadow: 0 0 0 3px rgba(230,57,70,0.06);
        outline: none;
    }

    /* Canvas y gráficos - borde moderado */
    canvas{
        border: 2px solid rgba(230,57,70,0.12) !important;
        border-radius: 12px;
        box-shadow: 0 8px 26px rgba(0,0,0,0.06);
        background-color: white;
    }

    hr{
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(230,57,70,0.06), transparent);
        margin: 1.2rem 0;
    }

    /* Ajustes para reducir espacios globales entre bloques */
    .main [data-testid="stVerticalBlock"] { padding-top: 6px; }
    .stApp .block-container { padding-top: 0.6rem; padding-bottom: 0.6rem; }
    .stApp .css-1d391kg { margin-bottom: 0.5rem; } /* reduce gaps en versiones de streamlit */
    .stApp .css-ffhzg2 { margin-bottom: 0.5rem; } /* backup para otras clases */
    </style>
    """
