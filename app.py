import os
import base64
import streamlit as st
from dotenv import load_dotenv
from google import genai

load_dotenv()

st.set_page_config(
    page_title="ComicCraft AI",
    page_icon="🎨",
    layout="wide"
)

API_KEY = os.getenv("GEMINI_API_KEY")

TEXT_MODEL = os.getenv(
    "GEMINI_TEXT_MODEL",
    "gemini-3.5-flash-lite"
)

IMAGE_MODEL = os.getenv(
    "GEMINI_IMAGE_MODEL",
    "gemini-3.1-flash-image"
)

if not API_KEY:
    st.error("GEMINI_API_KEY not found in .env file.")
    st.stop()

client = genai.Client(api_key=API_KEY)

st.title("🎨 ComicCraft AI")
st.write("Create a comic story and generate AI artwork using Gemini.")

idea = st.text_area(
    "Story idea",
    "A student discovers a tiny robot that repairs broken things."
)

characters = st.text_input(
    "Characters",
    "Arun and Bolt"
)

style = st.selectbox(
    "Art style",
    [
        "Colorful comic book",
        "Manga-inspired",
        "Cartoon",
        "Graphic novel"
    ]
)

panels = st.slider(
    "Panels",
    2,
    8,
    4
)

if st.button("🚀 Generate Comic Story"):

    prompt = f"""
Create a {panels}-panel comic story.

Story idea:
{idea}

Characters:
{characters}

Art style:
{style}

For every panel provide:

Panel number
Caption
Scene
Dialogue
Image Prompt

Keep the same characters and visual appearance across all panels.
"""

    try:
        response = client.models.generate_content(
            model=TEXT_MODEL,
            contents=prompt
        )

        story = response.text

        st.session_state.story = story

        st.success("Comic story generated successfully!")

    except Exception as e:
        st.error(f"Story generation failed: {e}")


if "story" in st.session_state:

    st.subheader("📖 Comic Script")

    st.text_area(
        "Generated Story",
        st.session_state.story,
        height=500
    )

    st.divider()

    st.subheader("🖼️ Generate Comic Artwork")

    if st.button("🎨 Generate Artwork"):

        image_prompt = f"""
Create ONE high-quality comic-book illustration.

Story:
{st.session_state.story}

Characters:
{characters}

Visual style:
{style}

Create a visually exciting comic panel composition.
Keep the characters visually consistent.
Use expressive faces, dynamic poses, cinematic lighting,
clear comic-book composition, detailed background,
vibrant colors and professional comic illustration quality.

Do not create a photo.
Create illustrated comic artwork.
"""

        try:

            with st.spinner(
                "Gemini is generating your comic artwork..."
            ):

                image_response = client.models.generate_content(
                    model=IMAGE_MODEL,
                    contents=image_prompt,
                    config={
                        "response_modalities": ["IMAGE"],
                        "image_config": {
                            "aspect_ratio": "16:9",
                            "image_size": "1K"
                        }
                    }
                )

            image_data = None

            for part in image_response.parts:

                if getattr(part, "inline_data", None):

                    image_data = part.inline_data.data
                    break

            if image_data:

                if isinstance(image_data, str):
                    image_bytes = base64.b64decode(image_data)
                else:
                    image_bytes = image_data

                st.image(
                    image_bytes,
                    caption="Generated Comic Artwork",
                    use_container_width=True
                )

                st.download_button(
                    label="⬇️ Download Comic Image",
                    data=image_bytes,
                    file_name="comiccraft_output.png",
                    mime="image/png"
                )

                st.success(
                    "🎉 Comic artwork generated successfully!"
                )

            else:
                st.error(
                    "Gemini returned no image. Please try again."
                )

        except Exception as e:

            st.error(
                f"Image generation failed: {e}"
            )

            st.info(
                "Check your Gemini API key, model access and internet connection."
            )