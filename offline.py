import gradio as gr
import pyttsx3
from PyPDF2 import PdfReader
from docx import Document
import tempfile
import os
import time
import uuid

# Initialize Text-to-Speech Engine
engine = pyttsx3.init()

# Language options with codes
language_options = {
    "English (en)": "en",
    "Hindi (hi)": "hi",
    "French (fr)": "fr",
    "Spanish (es)": "es",
    "German (de)": "de",
    "Japanese (ja)": "ja",
    "Chinese (zh)": "zh",
    "Russian (ru)": "ru",
    "Korean (ko)": "ko"
}

# Text-to-Speech Logic
def text_to_speech(text, language, speed):
    if not text:
        return "No text provided!", None

    lang_code = language_options[language]

    # Use pyttsx3 for English
    if lang_code == "en":
        rate = 150 + int((speed - 0.5) * 100)
        engine.setProperty('rate', rate)

        unique_filename = f"speech_output_{uuid.uuid4().hex}.mp3"
        temp_audio_path = os.path.join(tempfile.gettempdir(), unique_filename)
        engine.save_to_file(text, temp_audio_path)
        engine.runAndWait()
        time.sleep(1)

        return f"Speech generated! (Speed: {rate} WPM)", temp_audio_path

    # Use gTTS for other languages
    try:
        tts = gTTS(text=text, lang=lang_code)
        unique_filename = f"speech_output_{uuid.uuid4().hex}.mp3"
        temp_audio_path = os.path.join(tempfile.gettempdir(), unique_filename)
        tts.save(temp_audio_path)
        return f"Speech generated with gTTS for {language}!", temp_audio_path
    except Exception as e:
        return f"Error generating speech with gTTS: {e}", None

# Wrapper to return file for both playback and download
def text_to_speech_with_download(text, language, speed):
    msg, path = text_to_speech(text, language, speed)
    return msg, path, path

# Extract text from PDF, DOCX, or TXT
def extract_text_from_file(uploaded_file):
    if uploaded_file is None:
        return "No file uploaded."

    try:
        ext = os.path.splitext(uploaded_file.name)[1].lower()

        if ext == ".pdf":
            reader = PdfReader(uploaded_file)
            text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
            return text

        elif ext == ".docx":
            doc = Document(uploaded_file)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text

        elif ext == ".txt":
            return uploaded_file.read().decode("utf-8")

        else:
            return "Unsupported file format. Please upload PDF, DOCX, or TXT."

    except Exception as e:
        return f"Error reading file: {e}"

# Gradio UI
with gr.Blocks() as app:
    gr.Markdown("# 🗣 Advanced Text-to-Speech Converter")

    text_input = gr.Textbox(label="Enter Text or Upload a File")
    file_input = gr.File(label="Upload File (PDF, DOCX, TXT)", file_types=[".pdf", ".docx", ".txt"])
    language_input = gr.Dropdown(list(language_options.keys()), label="Select Language", value="English (en)")
    speed_input = gr.Slider(0.5, 2.0, value=1.0, label="Speed Control")

    output_message = gr.Textbox(label="Status")
    audio_output = gr.Audio(label="Generated Speech", autoplay=True, type="filepath")
    download_audio_btn = gr.File(label="Download Speech File")

    btn_tts = gr.Button("Convert to Speech")
    btn_file = gr.Button("Extract Text from File")
    btn_clear = gr.Button("Clear All")

    # Main TTS Logic
    btn_tts.click(
        text_to_speech_with_download,
        inputs=[text_input, language_input, speed_input],
        outputs=[output_message, audio_output, download_audio_btn]
    )

    # Extract from File
    btn_file.click(
        extract_text_from_file,
        inputs=[file_input],
        outputs=[text_input]
    )

    # Clear All
    btn_clear.click(
        lambda: ("", None, "", None),
        outputs=[text_input, audio_output, output_message, download_audio_btn]
    )

# Launch the app
app.launch()
