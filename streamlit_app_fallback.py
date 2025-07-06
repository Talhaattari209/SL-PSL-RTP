import streamlit as st
import os
import sys
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
import tempfile
import subprocess

# Page configuration
st.set_page_config(
    page_title="Sign Language Translator (Fallback Mode)",
    page_icon="🤟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'models_initialized' not in st.session_state:
    st.session_state.models_initialized = False
if 'demo_mode' not in st.session_state:
    st.session_state.demo_mode = True

def check_ffmpeg():
    """Check if FFMPEG is available"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def initialize_models():
    """Initialize models (demo mode)"""
    try:
        st.session_state.models_initialized = True
        st.session_state.demo_mode = True
        return True
    except Exception as e:
        st.error(f"❌ Error initializing models: {e}")
        return False

def translate_sign_to_text(video_input, source_lang="PSL"):
    """Translate sign language video to text (demo mode)"""
    try:
        if st.session_state.demo_mode:
            # Demo mode - return placeholder text
            if source_lang == "PSL":
                return "Translation: Hello, how are you? (PSL Demo Mode)", 85
            elif source_lang == "ASL":
                return "Translation: Hello, how are you? (ASL Demo Mode)", 85
            else:
                return "Translation: Video processed (Demo Mode)", 75
        else:
            return "Translation: Model not available", 50
    except Exception as e:
        return f"Translation error: {str(e)}", 50

def translate_text_to_sign(text_input, target_lang="PSL"):
    """Translate text to sign language (demo mode)"""
    try:
        if st.session_state.demo_mode:
            # Demo mode - return placeholder text
            if target_lang == "PSL":
                return f"Generated PSL sign video for: '{text_input}' (Demo Mode)", 85
            elif target_lang == "ASL":
                return f"Generated ASL sign video for: '{text_input}' (Demo Mode)", 85
            else:
                return f"Text-to-sign translation (Demo Mode): '{text_input}'", 75
        else:
            return "Model not available", 50
    except Exception as e:
        return f"Translation error: {str(e)}", 50

def home_page():
    st.title("🤟 Sign Language Translator (Fallback Mode)")
    st.warning("⚠️ **Running in Fallback Mode** - The sign-language-translator package is not available. Using demo functionality.")
    
    st.markdown("Welcome to the Sign Language Translator! This application can translate between text and sign language in multiple directions.")
    
    # Overview cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("📝 **Text to Sign**\n\nConvert written text into sign language videos using PSL or ASL.")
    
    with col2:
        st.info("🎥 **Sign to Text**\n\nConvert sign language videos into written text in English, Urdu, or Hindi.")
    
    with col3:
        st.info("🤟 **Sign to Sign**\n\nTranslate between different sign languages (PSL ↔ ASL).")
    
    # Quick start guide
    st.subheader("🚀 Quick Start")
    st.markdown("""
    1. **Initialize Models**: Click the "🔄 Initialize Models" button in the sidebar
    2. **Choose Translation**: Select your desired translation direction from the navigation
    3. **Input Content**: Enter text or upload/record a video
    4. **Get Results**: Click translate and view your results!
    """)
    
    # System status
    st.subheader("📊 System Status")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Demo Mode", "✅ Active")
        st.metric("Models Status", "✅ Demo Mode")
    
    with col2:
        st.metric("FFMPEG", "✅ Available" if check_ffmpeg() else "❌ Not Available")
        st.metric("Translation", "✅ Demo Mode")

def main():
    # Check FFMPEG
    if not check_ffmpeg():
        st.error("⚠️ FFMPEG is not installed. Some video features may not work properly.")
        st.info("To install FFMPEG, visit: https://ffmpeg.org/download.html")
    
    # Initialize models in sidebar
    with st.sidebar:
        st.title("🤟 Sign Language Translator")
        st.markdown("---")
        
        # Model initialization section
        st.subheader("🔧 Model Status")
        if st.button("🔄 Initialize Models", type="primary"):
            with st.spinner("Loading translation models..."):
                initialize_models()
        
        # Show model status
        st.metric("Demo Mode", "✅ Active")
        st.metric("Translation", "✅ Demo Mode")
        
        st.markdown("---")
    
    # Navigation
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["🏠 Home", "📝 Text to Sign", "🎥 Sign to Text", "ℹ️ About"]
    )
    
    # Display selected page
    if page == "🏠 Home":
        home_page()
    elif page == "📝 Text to Sign":
        text_to_sign_page()
    elif page == "🎥 Sign to Text":
        sign_to_text_page()
    elif page == "ℹ️ About":
        about_page()

def text_to_sign_page():
    st.header("📝 Text to Sign Language")
    
    # Language selection
    col1, col2 = st.columns(2)
    
    with col1:
        source_language = st.selectbox(
            "Source Language",
            ["English", "Urdu", "Hindi"],
            index=0
        )
    
    with col2:
        target_sign_language = st.selectbox(
            "Target Sign Language",
            ["Pakistan Sign Language (PSL)", "American Sign Language (ASL)"],
            index=0
        )
    
    # Text input
    text_input = st.text_area(
        "Enter text to translate:",
        placeholder="Type your text here...",
        height=100
    )
    
    # Translate button
    if st.button("🔄 Translate to Sign Language", type="primary"):
        if text_input.strip():
            with st.spinner("Translating..."):
                # Map language selection to model parameter
                target_lang = "PSL" if "PSL" in target_sign_language else "ASL"
                
                # Get translation
                result, confidence = translate_text_to_sign(text_input, target_lang)
                
                # Display results
                st.success("✅ Translation completed!")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("📝 Translation Result")
                    st.write(result)
                
                with col2:
                    st.subheader("📊 Confidence Score")
                    st.metric("Confidence", f"{confidence}%")
                
                # Demo video placeholder
                st.subheader("🎥 Generated Sign Video")
                st.info("In demo mode, this would show the generated sign language video.")
                st.write("**Demo Mode**: Video generation is simulated for demonstration purposes.")
        else:
            st.error("Please enter some text to translate.")

def sign_to_text_page():
    st.header("🎥 Sign to Text Language")
    
    # Language selection
    col1, col2 = st.columns(2)
    
    with col1:
        source_sign_language = st.selectbox(
            "Source Sign Language",
            ["Pakistan Sign Language (PSL)", "American Sign Language (ASL)"],
            index=0
        )
    
    with col2:
        target_language = st.selectbox(
            "Target Language",
            ["English", "Urdu", "Hindi"],
            index=0
        )
    
    # Video input options
    st.subheader("📹 Video Input")
    
    input_method = st.radio(
        "Choose input method:",
        ["Upload Video File", "Record Video", "Use Sample Video"]
    )
    
    video_input = None
    
    if input_method == "Upload Video File":
        uploaded_file = st.file_uploader(
            "Upload a sign language video:",
            type=['mp4', 'avi', 'mov', 'mkv']
        )
        if uploaded_file is not None:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                video_input = tmp_file.name
            st.success(f"✅ Video uploaded: {uploaded_file.name}")
    
    elif input_method == "Record Video":
        st.info("🎥 Video recording feature would be available here.")
        st.write("**Demo Mode**: Video recording is simulated for demonstration purposes.")
        video_input = "demo_recorded_video.mp4"
    
    elif input_method == "Use Sample Video":
        st.info("📁 Sample video feature would be available here.")
        st.write("**Demo Mode**: Sample videos are simulated for demonstration purposes.")
        video_input = "demo_sample_video.mp4"
    
    # Translate button
    if st.button("🔄 Translate to Text", type="primary"):
        if video_input:
            with st.spinner("Processing video and translating..."):
                # Map language selection to model parameter
                source_lang = "PSL" if "PSL" in source_sign_language else "ASL"
                
                # Get translation
                result, confidence = translate_sign_to_text(video_input, source_lang)
                
                # Display results
                st.success("✅ Translation completed!")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("📝 Translation Result")
                    st.write(result)
                
                with col2:
                    st.subheader("📊 Confidence Score")
                    st.metric("Confidence", f"{confidence}%")
                
                # Video preview placeholder
                st.subheader("🎥 Video Preview")
                st.info("In demo mode, this would show the uploaded/recorded video.")
                st.write("**Demo Mode**: Video preview is simulated for demonstration purposes.")
        else:
            st.error("Please provide a video input first.")

def about_page():
    st.header("ℹ️ About")
    
    st.markdown("""
    ## Sign Language Translator
    
    This application provides translation services between text and sign languages, supporting:
    
    ### Supported Languages
    - **Text Languages**: English, Urdu, Hindi
    - **Sign Languages**: Pakistan Sign Language (PSL), American Sign Language (ASL)
    
    ### Features
    - Text to Sign Language translation
    - Sign Language to Text translation
    - Video upload and recording capabilities
    - Multiple language support
    
    ### Current Status
    - **Mode**: Demo/Fallback Mode
    - **Reason**: The sign-language-translator package is not compatible with Python 3.12
    - **Functionality**: Simulated translations for demonstration purposes
    
    ### Technical Details
    - Built with Streamlit
    - Uses OpenCV for video processing
    - Supports multiple video formats
    - Requires FFMPEG for video operations
    
    ### Future Improvements
    - Full model integration when package compatibility is resolved
    - Real-time video processing
    - Enhanced accuracy with larger training datasets
    - Support for more sign languages
    """)

if __name__ == "__main__":
    main() 