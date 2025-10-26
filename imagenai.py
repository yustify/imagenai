import streamlit as st
import requests
import base64
from io import BytesIO
from PIL import Image

# --- Configuración de la API de OpenRouter ---
# Guarda tu API Key de OpenRouter de forma segura
# NUNCA la expongas directamente en el código para producción.
# Para Streamlit Cloud, usa los "Secrets".
# Por ahora, la ponemos aquí para desarrollo local.
OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"] if "OPENROUTER_API_KEY" in st.secrets else "TU_CLAVE_AQUI" # Reemplaza con tu clave para pruebas locales
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/images/generations" # Endpoint para generación de imágenes
# MODEL_NAME = "stability-ai/stable-diffusion-xl-turbo" # Un modelo rápido de texto a imagen
MODEL_NAME = "stability-ai/stable-diffusion-3-medium" # Otro buen modelo para texto a imagen


# --- Título y Descripción de la Aplicación ---
st.set_page_config(
    page_title="Generador de Imágenes con IA",
    page_icon="🎨",
    layout="centered",
    initial_sidebar_state="auto"
)

st.title("🎨 Generador de Imágenes IA")
st.markdown("""
¡Crea imágenes increíbles usando modelos avanzados a través de OpenRouter!
Introduce tus descripciones y personaliza los parámetros para obtener el resultado deseado.
""")
st.info(f"Modelo de IA utilizado: **{MODEL_NAME}**")

# --- Formulario de Entrada para el Usuario ---
with st.form("image_generation_form"):
    st.subheader("1. Describe tu Imagen")
    prompt = st.text_area(
        "¿Qué quieres ver en la imagen? (Sé lo más detallado posible)",
        placeholder="Un astronauta montando un caballo en Marte, estilo fotorrealista, atardecer",
        height=150
    )
    negative_prompt = st.text_area(
        "¿Qué NO quieres ver en la imagen? (Opcional)",
        placeholder="Baja calidad, borroso, marcas de agua, feo, deforme",
        height=70
    )

    st.subheader("2. Parámetros de Generación")
    col1, col2 = st.columns(2)
    with col1:
        width = st.slider("Ancho (px)", 256, 1024, 512, step=64)
    with col2:
        height = st.slider("Alto (px)", 256, 1024, 512, step=64)

    num_images = st.slider("Número de Imágenes", 1, 4, 1)
    guidance_scale = st.slider("Escala de Guía (CFG)", 1.0, 20.0, 7.0, step=0.5)
    steps = st.slider("Pasos de Muestreo", 10, 50, 25, step=5)
    seed = st.number_input("Semilla (para reproducibilidad, 0 para aleatorio)", 0, 999999999, 0)

    submitted = st.form_submit_button("Generar Imagen(es)")

# --- Lógica de Generación de Imagen ---
if submitted:
    if not prompt:
        st.error("Por favor, introduce una descripción para generar la imagen.")
    else:
        st.subheader("✨ Generando tus imágenes...")
        with st.spinner("La generación puede tardar unos segundos..."):
            try:
                headers = {
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://streamlit.app", # Es buena práctica especificar el referente
                    "X-Title": "Mi Generador de Imagen Streamlit", # Un título para tu aplicación en OpenRouter
                }

                payload = {
                    "model": MODEL_NAME,
                    "prompt": prompt,
                    "n": num_images,
                    "size": f"{width}x{height}",
                    "response_format": "b64_json", # Pide la imagen en base64
                    "seed": seed if seed != 0 else None, # Si la semilla es 0, no la enviamos
                    "guidance_scale": guidance_scale,
                    "steps": steps,
                    "negative_prompt": negative_prompt if negative_prompt else None,
                }

                response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=120)

                if response.status_code == 200:
                    data = response.json()
                    if data and "data" in data and data["data"]:
                        st.subheader("🎉 ¡Tus Imágenes Generadas!")
                        for img_data in data["data"]:
                            if "b64_json" in img_data:
                                image_bytes = base64.b64decode(img_data["b64_json"])
                                image = Image.open(BytesIO(image_bytes))
                                st.image(image, caption=prompt, use_column_width=True)
                            else:
                                st.warning("No se recibió formato b64_json para una imagen.")
                    else:
                        st.error("No se recibieron datos de imagen de OpenRouter.")
                        st.json(data) # Mostrar respuesta completa para depuración
                else:
                    st.error(f"Error al conectar con OpenRouter (Código: {response.status_code}).")
                    st.error(f"Mensaje: {response.text}")

            except requests.exceptions.Timeout:
                st.error("La solicitud a OpenRouter ha tardado demasiado y ha expirado. Por favor, inténtalo de nuevo.")
            except Exception as e:
                st.error(f"Ha ocurrido un error inesperado: {e}")
                st.exception(e) # Muestra el traceback completo para depuración

st.markdown("---")
st.markdown("Desarrollado con ❤️ por tu asistente IA.")
