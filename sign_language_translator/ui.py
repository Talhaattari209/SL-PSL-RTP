import streamlit as st
import requests
import tempfile
import os

st.title("Bilingual Sign Language Translator (PSL & WLASL)")

# --- Language Selection ---
language_options = ["PSL", "WLASL"]
input_lang = st.selectbox("Input Language", language_options)
output_lang = st.selectbox("Output Language", language_options)

# --- Conversion Mode ---
conversion_mode = st.radio(
    "Select Conversion Mode:",
    [
        "Sign to Text",
        "Text to Sign",
        "Sign to Sign"
    ]
)

# --- Input Type ---
if conversion_mode == "Text to Sign":
    input_type = "text"
else:
    input_type = st.radio("Input Type", ["Upload Video", "Record Live Video"])

# --- Input Widgets ---
input_text = None
video_file = None
video_file_path = None

if input_type == "text":
    input_text = st.text_area("Enter text (English)")
else:
    if input_type == "Upload Video":
        video_file = st.file_uploader("Upload video", type=["mp4", "avi", "mov"])
    else:
        st.info("Click below to record a short video using your webcam.")
        live_video = st.camera_input("Record Live Video")
        if live_video is not None:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_vid:
                temp_vid.write(live_video.getvalue())
                video_file_path = temp_vid.name
            video_file = open(video_file_path, "rb")

# --- Output Type ---
if conversion_mode == "Sign to Text":
    output_type = "text"
elif conversion_mode == "Text to Sign":
    output_type = "video"
else:  # Sign to Sign
    output_type = "video"

# --- Convert Button ---
if st.button("Convert"):
    files = {}
    data = {
        "conversion_mode": conversion_mode,
        "source_lang": input_lang,
        "target_lang": output_lang,
        "output_type": output_type,
        "input_text": input_text
    }
    if video_file is not None:
        files["video_file"] = video_file
    # Use the ngrok URL from your FastAPI server
    ngrok_url = "http://34.125.176.63:8001"  # Replace with your actual ngrok URL
    response = requests.post(f"{ngrok_url}/convert", data=data, files=files)
    if video_file_path is not None:
        video_file.close()
        os.remove(video_file_path)
    if response.status_code == 200:
        if output_type == "text":
            st.success("Output:")
            st.write(response.json().get("result"))
        elif output_type == "video":
            with open("output.mp4", "wb") as f:
                f.write(response.content)
            st.video("output.mp4")
    else:
        st.error("Error: " + response.text)

# --- User Guidance ---
st.markdown("""
**Features:**
- Choose conversion mode: Sign to Text, Text to Sign, or Sign to Sign
- Select PSL or WLASL for both input and output sign language
- Input via text, video upload, or live webcam recording
- Output as text or video
- Text language: English
""") 