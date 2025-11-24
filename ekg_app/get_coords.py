import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import os

st.set_page_config(layout="wide")

st.title("📍 Obtener coordenadas X usando Canvas")

image_path = "assets/images/ej_1.png"

img = Image.open(image_path)

st.write("### 1️⃣ Haz dos clics en los puntos donde inicia y termina el intervalo que quieres medir")
st.write("- Primer clic → inicio de P")
st.write("- Segundo clic → inicio de QRS")

canvas_result = st_canvas(
    background_image=img,
    height=300,
    width=600,
    drawing_mode="point",
    point_display_radius=5,
    stroke_color="red",
    key="coord_canvas"
)

if canvas_result.json_data is not None:
    objs = canvas_result.json_data["objects"]

    if len(objs) >= 1:
        st.subheader("📍 Coordenadas detectadas")
        for i, obj in enumerate(objs):
            x = obj["left"]
            y = obj["top"]
            st.write(f"**Punto {i+1}: x = {x:.0f}, y = {y:.0f}**")

    if len(objs) == 2:
        x1 = objs[0]["left"]
        x2 = objs[1]["left"]
        st.success(f"Zona válida propuesta: x_min = {min(x1, x2):.0f}, x_max = {max(x1, x2):.0f}")
