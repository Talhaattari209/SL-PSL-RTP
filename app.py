import streamlit as st
import sign_language_translator as slt
from sign_language_translator.models import get_model
from sign_language_translator.config.enums import ModelCodes, TextLanguages, SignLanguages, SignFormats
import tempfile
import os

st.set_page_config(
    page_title="Sign Language Translator",
    page_icon="🤟",
    layout="wide"
)

st.title("Sign Language Translator")
st.write("Translate text to sign language videos or vice versa")

# Initialize session state
if 'translator' not in st.session_state:
    st.session_state.translator = None
if 'embedding_model' not in st.session_state:
    st.session_state.embedding_model = None

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
        
        if st.button("Translate"):
            if input_text:
                try:
                    with st.spinner("Translating..."):
                        # Create a temporary directory for the output
                        with tempfile.TemporaryDirectory() as temp_dir:
                            output_path = os.path.join(temp_dir, "output.mp4")
                            
                            # Perform translation
                            sign = st.session_state.translator.translate(input_text)
                            sign.save(output_path, overwrite=True)
                            
                            # Display the video
                            st.video(output_path)
                except Exception as e:
                    st.error(f"Translation error: {str(e)}")
            else:
                st.warning("Please enter some text to translate")
    
    else:  # sign-to-text
        # Sign to Text translation
        uploaded_file = st.file_uploader("Upload a sign language video", type=["mp4", "avi", "mov"])
        
        if uploaded_file is not None:
            # Save uploaded file to temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                video_path = tmp_file.name
            
            if st.button("Process"):
                try:
                    with st.spinner("Processing video..."):
                        # Load video and extract features
                        video = slt.Video(video_path)
                        
                        # Extract landmarks using MediaPipe
                        landmarks = st.session_state.embedding_model.embed(video.iter_frames())
                        
                        # Display the landmarks visualization
                        landmarks_viz = slt.Landmarks(landmarks.reshape((-1, 75, 5)), 
                                                   connections="mediapipe-world")
                        
                        # Save landmarks visualization as GIF
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".gif") as viz_file:
                            landmarks_viz.save_animation(viz_file.name, overwrite=True)
                            st.image(viz_file.name, caption="Extracted Landmarks")
                            os.unlink(viz_file.name)
                        
                        # Display the extracted landmarks data
                        st.write("Extracted Landmarks Shape:", landmarks.shape)
                        st.write("Note: Sign-to-text translation model is not yet available. This shows the landmark extraction step.")
                        
                except Exception as e:
                    st.error(f"Processing error: {str(e)}")
                finally:
                    # Clean up temporary file
                    os.unlink(video_path) 