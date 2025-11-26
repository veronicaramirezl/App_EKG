import openai
import os
from PIL import Image, ImageDraw
import google.generativeai as genai

import google.generativeai as genai
import openai

def get_ai_visual_feedback(api_key, img_base64, user_measurement, correct_ms, tolerance, instruction, explanation=""):
    """Envía la imagen con las marcas del estudiante a Gemini para revisión visual."""
    import google.generativeai as genai
    import PIL.Image
    import io
    import base64
    
    # Configurar Gemini
    genai.configure(api_key=api_key)
    
    # Convertir base64 a imagen PIL
    img_data = base64.b64decode(img_base64)
    img_pil = PIL.Image.open(io.BytesIO(img_data))
    
    # Crear el modelo Gemini (usando Gemini 1.5 Flash o Pro para imágenes)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""tu Eres un profesor experto en electrocardiografía. Revisa visualmente las marcas que el estudiante hizo en el ECG.

el mensaje debe ser conciso pero facil de entender. Debes dirigirte al estudiante en segunda persona.
El estudiante debe {instruction}.

Ha marcado puntos en la imagen y midió {user_measurement} ms.
El valor correcto es {correct_ms} ms (tolerancia: ±{tolerance} ms).

su razonamiento para haberlo hecho asi es este: {explanation}

Analiza la imagen y, sin decir nunca la respuesta exacta, responde a las siguientes preguntas:
Si hay errores, explica QUÉ está mal y CÓMO corregirlo (sin dar la respuesta exacta). donde fue el error? tal vez la marca no fue adecuad, tal vez si fue adecuada pero la medición fue incorrecta, etc.

Sé específico sobre la ubicación de los puntos en el complejo ECG."""

    try:
        # Enviar imagen y prompt a Gemini
        response = model.generate_content([prompt, img_pil])
        return response.text
    except Exception as e:
        return f"Error con Gemini: {str(e)}"
    
def get_ai_feedback(api_key, system_prompt, user_input, model="gemini"):

    if not api_key:
        return "⚠️ Necesitas ingresar tu API Key."

    # === Gemini ===
    if model == "gemini":
        try:
            genai.configure(api_key=api_key)
            llm = genai.GenerativeModel("gemini-2.5-flash")
            response = llm.generate_content(
                system_prompt + "\n\n" + user_input
            )
            return response.text
        except Exception as e:
            return f"❌ Error con Gemini: {str(e)}"

    # === OpenAI (fallback) ===
    if model == "openai":
        try:
            client = openai.OpenAI(api_key=api_key)
            r = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ]
            )
            return r.choices[0].message.content
        except Exception as e:
            return f"❌ Error con OpenAI: {str(e)}"


def load_image(image_name):
    """Busca la imagen en ekg_app/assets/images usando ruta absoluta."""
    base_path = os.path.dirname(os.path.abspath(__file__))  # carpeta utils/
    project_root = os.path.dirname(base_path)               # sube a ekg_app/
    images_path = os.path.join(project_root, "assets", "images")
    path = os.path.join(images_path, image_name)

    if os.path.exists(path):
        return Image.open(path)

    # Placeholder si no existe
    img = Image.new('RGB', (600, 300), color=(240, 240, 240))
    d = ImageDraw.Draw(img)
    d.text((10, 150), f"Imagen no encontrada:\n{path}", fill=(0, 0, 0))
    return img