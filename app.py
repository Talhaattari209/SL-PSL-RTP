import streamlit as st
import sign_language_translator as slt
from sign_language_translator.models import get_model
from sign_language_translator.config.enums import ModelCodes, TextLanguages, SignLanguages, SignFormats
import tempfile
import os
import re
import base64
from pathlib import Path
import io

st.set_page_config(
    page_title="Sign Language Translator",
    page_icon="🤟",
    layout="wide"
)

# Create a directory for temporary files if it doesn't exist
TEMP_DIR = Path("temp_files")
TEMP_DIR.mkdir(exist_ok=True)

st.title("Sign Language Translator")
st.write("Translate text to sign language videos or vice versa")

# Initialize session state
if 'translator' not in st.session_state:
    st.session_state.translator = None
if 'embedding_model' not in st.session_state:
    st.session_state.embedding_model = None
if 'disambiguation_map' not in st.session_state:
    st.session_state.disambiguation_map = {}
if 'assets_downloaded' not in st.session_state:
    st.session_state.assets_downloaded = False

# Helper function to extract options from error message
def extract_options_from_error(error_msg):
    match = re.search(r"Try from \[(.*?)\]", str(error_msg))
    if match:
        options_str = match.group(1)
        # Split by comma and clean up the quotes
        options = [opt.strip().strip("'") for opt in options_str.split(',')]
        return options
    return []

# Helper function to download required assets
def ensure_assets_downloaded():
    if not st.session_state.assets_downloaded:
        with st.spinner("Downloading required assets... This may take a few minutes..."):
            try:
                # Download all required assets
                slt.Assets.download(r".*urls\.json")  # Download URL mappings
                slt.Assets.download(r".*\.mp4")  # Download video files
                st.session_state.assets_downloaded = True
                st.success("Assets downloaded successfully!")
            except Exception as e:
                st.error(f"Error downloading assets: {str(e)}")
                return False
    return True

# Helper function to clean up old temporary files
def cleanup_temp_files():
    if TEMP_DIR.exists():
        for file in TEMP_DIR.glob("*"):
            try:
                if file.is_file():
                    file.unlink()
            except Exception:
                pass

# Sidebar for model selection
with st.sidebar:
    st.header("Model Configuration")
    
    # Model selection
    model_code = st.selectbox(
        "Select Translation Model",
        ["text-to-sign", "sign-to-text"],
        help="Choose the translation direction"
    )
    
    # Language selection
    text_lang = st.selectbox(
        "Text Language",
        [TextLanguages.ENGLISH.value, TextLanguages.URDU.value],
        help="Select the text language"
    )
    
    sign_lang = st.selectbox(
        "Sign Language",
        [SignLanguages.PAKISTAN_SIGN_LANGUAGE.value],
        help="Select the sign language"
    )
    
    sign_format = st.selectbox(
        "Sign Format",
        [SignFormats.VIDEO.value, SignFormats.LANDMARKS.value],
        help="Select the sign format"
    )
    
    # Initialize translator
    if st.button("Initialize Translator"):
        try:
            # First ensure assets are downloaded
            if model_code == "text-to-sign" and not ensure_assets_downloaded():
                st.error("Failed to download required assets. Please try again.")
            else:
                if model_code == "text-to-sign":
                    st.session_state.translator = slt.models.ConcatenativeSynthesis(
                        text_language=text_lang,
                        sign_language=sign_lang,
                        sign_format=sign_format
                    )
                    st.success("Text-to-Sign translator initialized successfully!")
                else:  # sign-to-text
                    # Initialize MediaPipe model for landmark extraction
                    st.session_state.embedding_model = slt.models.MediaPipeLandmarksModel()
                    st.success("Sign-to-Text processor initialized successfully!")
        except Exception as e:
            st.error(f"Error initializing: {str(e)}")

# Clean up old temporary files at the start of each run
cleanup_temp_files()

# Main content area
if (model_code == "text-to-sign" and st.session_state.translator is None) or \
   (model_code == "sign-to-text" and st.session_state.embedding_model is None):
    st.warning("Please initialize the translator from the sidebar first.")
else:
    # Input section
    st.header("Translation")
    
    if model_code == "text-to-sign":
        # Text to Sign translation
        input_text = st.text_area("Enter text to translate", height=100)
        
        # Show disambiguation options if needed
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("Translate"):
                if input_text:
                    # Ensure assets are downloaded before translation
                    if ensure_assets_downloaded():
                        try:
                            with st.spinner("Translating..."):
                                try:
                                    # Try translation
                                    sign = st.session_state.translator.translate(input_text)
                                    
                                    # Get the video data
                                    video_data = io.BytesIO()
                                    sign.save(video_data)
                                    video_bytes = video_data.getvalue()
                                    
                                    # Display using Streamlit
                                    st.video(video_bytes)
                                    
                                    # Clear disambiguation map if translation successful
                                    st.session_state.disambiguation_map = {}
                                        
                                except Exception as e:
                                    error_msg = str(e)
                                    if "is ambiguous" in error_msg:
                                        # Extract the ambiguous word
                                        word = error_msg.split("'")[1]
                                        options = extract_options_from_error(error_msg)
                                        if options:
                                            st.warning(f"Please select the correct form for the word '{word}'")
                                            # Store options for the word
                                            st.session_state.disambiguation_map[word] = options
                                    else:
                                        # For debugging
                                        st.error(f"Translation error: {str(e)}")
                                        st.write("Available assets:", list(slt.Assets.FILE_TO_URL.keys()))
                                        # Print more debug info
                                        st.write("Asset directory:", slt.Assets.get_root_dir())
                                        st.write("Current working directory:", os.getcwd())
                        except Exception as e:
                            st.error(f"Translation error: {str(e)}")
                else:
                    st.warning("Please enter some text to translate")
        
        # Show disambiguation options in sidebar
        with col2:
            if st.session_state.disambiguation_map:
                st.subheader("Word Forms")
                for word, options in st.session_state.disambiguation_map.items():
                    selected = st.radio(f"Select form for '{word}'", options)
                    # Replace the ambiguous word with the selected form
                    input_text = input_text.replace(word, selected)
    
    else:  # sign-to-text
        # Sign to Text translation
        uploaded_file = st.file_uploader("Upload a sign language video", type=["mp4", "avi", "mov"])
        
        if uploaded_file is not None:
            if st.button("Process"):
                try:
                    with st.spinner("Processing video..."):
                        # Load video directly from uploaded file
                        video_bytes = uploaded_file.getvalue()
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
                            tmp_file.write(video_bytes)
                            video = slt.Video(tmp_file.name)
                            
                            # Extract landmarks using MediaPipe
                            landmarks = st.session_state.embedding_model.embed(video.iter_frames())
                            
                            # Display the landmarks visualization
                            landmarks_viz = slt.Landmarks(landmarks.reshape((-1, 75, 5)), 
                                                       connections="mediapipe-world")
                            
                            # Save landmarks visualization to bytes
                            viz_data = io.BytesIO()
                            landmarks_viz.save_animation(viz_data)
                            st.image(viz_data.getvalue(), caption="Extracted Landmarks")
                            
                            # Display the extracted landmarks data
                            st.write("Extracted Landmarks Shape:", landmarks.shape)
                            st.write("Note: Sign-to-text translation model is not yet available. This shows the landmark extraction step.")
                            
                            # Clean up
                            os.unlink(tmp_file.name)
                        
                except Exception as e:
                    st.error(f"Processing error: {str(e)}") 