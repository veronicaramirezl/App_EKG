def load_css():
    return """
    <style>
    .main { background-color: #f8f9fa; }
    h1, h2, h3 { color: #2c3e50; font-family: 'Segoe UI', sans-serif; }
    .stButton>button {
        background-color: #2E86C1; 
        color: white; 
        border-radius: 8px; border: none;
    }
    .stButton>button:hover { background-color: #1B4F72; }
    .success-box {
        padding: 15px; background-color: #d4edda; color: #155724;
        border-radius: 5px; border-left: 5px solid #28a745;
    }
    .error-box {
        padding: 15px; background-color: #f8d7da; color: #721c24;
        border-radius: 5px; border-left: 5px solid #dc3545;
    }
    </style>
    """