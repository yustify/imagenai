import streamlit as st
import requests
import base64
from io import BytesIO
from PIL import Image

# --- Configuración de la API de OpenRouter ---
# Lee la clave de API desde los secretos de Streamlit
# Para desarrollo local, crea un archivo .streamlit/secrets.toml
# y añade: OPENROUTER_API_KEY="tu_clave_sk-or-v1..."
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "TU_CLAVE_AQUI_PARA_PRUEBAS_LOCALES")

# Endpoint para generación de imágenes (estilo OpenAI)
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/images/generations" 

# Modelo compatible con el endpoint /images/generations
MODEL_NAME = "openai/dall-e-2"

# --- Título y Descripción de la Aplicación ---
st.set_page_config(
    page_title="Generador de Imágenes con IA",
    page_icon="🎨",
    layout="centered",
    initial_sidebar_state="auto"
)

st.title("🎨 Generador de Imágenes IA")
st.markdown("""
¡Crea imágenes increíbles usando DALL-E 2 a través de OpenRouter!
Introduce tu descripción y elige los parámetros para obtener el resultado deseado.
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

    st.subheader("2. Parámetros de Generación")
    
    # DALL-E 2 solo acepta tamaños específicos
    size_options = ["256x256", "512x512", "1024x1024"]
    selected_size = st.selectbox(
        "Dimensiones de la Imagen", 
        size_options, 
        index=1  # Por defecto seleccionamos "512x512"
    )

    num_images = st.slider("Número de Imágenes", 1, 4, 1)

    # Nota: DALL-E 2 no usa 'seed', 'guidance_scale', 'steps' ni 'negative_prompt'.
    # Por lo tanto, esos sliders y campos de texto se han eliminado.

    submitted = st.form_submit_button("Generar Imagen(es)")

# --- Lógica de Generación de Imagen ---
if submitted:
    if not prompt:
        st.error("Por favor, introduce una descripción para generar la imagen.")
    elif OPENROUTER_API_KEY == "TU_CLAVE_AQUI_PARA_PRUEBAS_LOCALES":
        st.error("Por favor, añade tu OPENROUTER_API_KEY a los secretos de Streamlit.")
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

                # Payload ajustado para DALL-E 2
                payload = {
                    "model": MODEL_NAME,
                    "prompt": prompt,
                    "n": num_images,
                    "size": selected_size, # Usamos el string "512x512" directamente
                    "response_format": "b64_json", # Pide la imagen en base64
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
