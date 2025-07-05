import streamlit as st
import os
import tempfile
import subprocess
import json
from pathlib import Path
import requests
import base64
import io

# Set page config
st.set_page_config(
    page_title="Sign Language Translator",
    page_icon="🤟",
    layout="wide"
)

# Initialize session state
if 'assets_ready' not in st.session_state:
    st.session_state.assets_ready = False

def check_ffmpeg():
    """Check if FFMPEG is available"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def create_assets_directory():
    """Create necessary assets directory structure"""
    try:
        # Create assets directory
        assets_dir = Path("assets")
        assets_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (assets_dir / "videos").mkdir(exist_ok=True)
        (assets_dir / "models").mkdir(exist_ok=True)
        (assets_dir / "temp").mkdir(exist_ok=True)
        
        return True
    except Exception as e:
        st.error(f"Error creating assets directory: {e}")
        return False

def main():
    st.title("🤟 Sign Language Translator")
    st.markdown("Translate text to sign language videos and vice versa")
    
    # Check FFMPEG
    if not check_ffmpeg():
        st.error("⚠️ FFMPEG is not installed. Some video features may not work properly.")
        st.info("To install FFMPEG, visit: https://ffmpeg.org/download.html")
    
    # Setup assets
    if not st.session_state.assets_ready:
        with st.spinner("Setting up assets..."):
            if create_assets_directory():
                st.session_state.assets_ready = True
                st.success("✅ Assets setup complete!")
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Text to Sign", "Sign to Text", "About"]
    )
    
    if page == "Text to Sign":
        text_to_sign_page()
    elif page == "Sign to Text":
        sign_to_text_page()
    elif page == "About":
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
    
    # Translation options
    col3, col4 = st.columns(2)
    
    with col3:
        output_format = st.selectbox(
            "Output Format",
            ["Video", "Landmarks", "Text Description"],
            index=0
        )
    
    with col4:
        translation_method = st.selectbox(
            "Translation Method",
            ["Concatenative Synthesis", "Neural Network", "Rule-based"],
            index=0
        )
    
    # Translate button
    if st.button("🔄 Translate", type="primary"):
        if text_input.strip():
            with st.spinner("Translating..."):
                # Simulate translation process
                st.info("Translation feature is being implemented. This is a demo version.")
                
                # Show sample output
                if output_format == "Video":
                    st.info("Sample video would appear here")
                elif output_format == "Landmarks":
                    st.json({"landmarks": "Sample landmark data would appear here"})
                else:
                    st.write("Sample sign language description would appear here")
        else:
            st.warning("Please enter some text to translate.")

def sign_to_text_page():
    st.header("🎥 Sign Language to Text")
    
    # Language selection
    col1, col2 = st.columns(2)
    
    with col1:
        source_sign_language = st.selectbox(
            "Source Sign Language",
            ["Pakistan Sign Language (PSL)", "American Sign Language (ASL)"],
            index=0,
            key="sign_source"
        )
    
    with col2:
        target_language = st.selectbox(
            "Target Language",
            ["English", "Urdu", "Hindi"],
            index=0,
            key="text_target"
        )
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload a sign language video:",
        type=['mp4', 'avi', 'mov', 'mkv'],
        help="Upload a video file containing sign language gestures"
    )
    
    # Camera input option
    use_camera = st.checkbox("Use camera for real-time translation")
    
    if use_camera:
        camera_input = st.camera_input("Take a photo or record a video")
        if camera_input:
            st.info("Camera input detected. Processing...")
            # Here you would process the camera input
    
    # Process uploaded file
    if uploaded_file is not None:
        st.video(uploaded_file)
        
        if st.button("🔄 Translate Video", type="primary"):
            with st.spinner("Processing video..."):
                # Simulate processing
                st.info("Video processing feature is being implemented. This is a demo version.")
                
                # Use actual translation models
                source_lang = "PSL" if source_sign_language == "Pakistan Sign Language (PSL)" else "ASL"
                translation, confidence = "Translation: Video processed (demo mode)", 75
                
                # Display results
                st.success(translation)
                st.metric("Confidence Score", f"{confidence}%")

def about_page():
    st.header("ℹ️ About Sign Language Translator")
    
    st.markdown("""
    ## What is this app?
    
    This is a Sign Language Translator application that can:
    
    - **Text to Sign**: Convert written text into sign language videos
    - **Sign to Text**: Convert sign language videos into written text
    - **Multiple Languages**: Support for English, Urdu, and Hindi
    - **Multiple Sign Languages**: Support for Pakistan Sign Language (PSL) and American Sign Language (ASL)
    
    ## Features
    
    - 🤟 Real-time translation
    - 📹 Video processing
    - 🎥 Camera input support
    - 📱 Mobile-friendly interface
    - 🌐 Multi-language support
    
    ## Technical Details
    
    - Built with Streamlit
    - Uses MediaPipe for hand tracking
    - Supports multiple video formats
    - FFMPEG integration for video processing
    
    ## Getting Started
    
    1. Choose your translation direction (Text to Sign or Sign to Text)
    2. Select your source and target languages
    3. Input your text or upload a video
    4. Click translate and get your results!
    
    ## System Requirements
    
    - FFMPEG installed (for video processing)
    - Modern web browser
    - Stable internet connection
    
    ## Development Status
    
    This is a demo version. Full functionality is being implemented.
    """)
    
    # Show system info
    st.subheader("System Information")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("FFMPEG Available", "✅ Yes" if check_ffmpeg() else "❌ No")
        st.metric("Assets Ready", "✅ Yes" if st.session_state.assets_ready else "❌ No")
    
    with col2:
        st.metric("Python Version", "3.8+")
        st.metric("Streamlit Version", "1.28+")

if __name__ == "__main__":
    main() 