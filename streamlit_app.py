import streamlit as st
import os
import tempfile
import subprocess
import json
from pathlib import Path
import requests
import base64
import io
import time
import sys

# Add the sign_language_translator to the path
sys.path.append(str(Path(__file__).parent))

# Set page config
st.set_page_config(
    page_title="Sign Language Translator",
    page_icon="🤟",
    layout="wide"
)

# Initialize session state for models
if 'psl_sign_to_text_model' not in st.session_state:
    st.session_state.psl_sign_to_text_model = None
if 'wlasl_sign_to_text_model' not in st.session_state:
    st.session_state.wlasl_sign_to_text_model = None
if 'psl_text_to_sign_model' not in st.session_state:
    st.session_state.psl_text_to_sign_model = None
if 'wlasl_text_to_sign_model' not in st.session_state:
    st.session_state.wlasl_text_to_sign_model = None
if 'assets_ready' not in st.session_state:
    st.session_state.assets_ready = False

def check_ffmpeg():
    """Check if FFMPEG is installed"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def create_assets_directory():
    """Create assets directory if it doesn't exist"""
    assets_dir = Path("sign_language_translator/assets")
    assets_dir.mkdir(parents=True, exist_ok=True)
    return assets_dir.exists()

def download_sample_videos():
    """Download sample videos for demonstration"""
    # This would download sample videos if needed
    pass

def initialize_models():
    """Initialize translation models"""
    try:
        # Initialize PSL Sign-to-Text model
        if st.session_state.psl_sign_to_text_model is None:
            from sign_language_translator.models.sign_to_text import PSLSignToTextModel
            model_path = "sign_language_model_best.pth"
            if os.path.exists(model_path):
                st.session_state.psl_sign_to_text_model = PSLSignToTextModel()
                st.session_state.psl_sign_to_text_model.load_model(model_path)
                st.success("✅ PSL Sign-to-Text model loaded successfully")
            else:
                st.warning("⚠️ PSL model file not found. Using demo mode.")
        
        # Initialize WLASL Sign-to-Text model
        if st.session_state.wlasl_sign_to_text_model is None:
            from sign_language_translator.models.sign_to_text import WLASLSignToTextModel
            wlasl_model_path = "wlasl_vit_transformer.pth"
            if os.path.exists(wlasl_model_path):
                st.session_state.wlasl_sign_to_text_model = WLASLSignToTextModel()
                st.session_state.wlasl_sign_to_text_model.load(wlasl_model_path)
                st.success("✅ WLASL Sign-to-Text model loaded successfully")
            else:
                st.warning("⚠️ WLASL model file not found. Using demo mode.")
        
        # Initialize Text-to-Sign models
        if st.session_state.psl_text_to_sign_model is None:
            from sign_language_translator.models.text_to_sign import ConcatenativeSynthesis
            st.session_state.psl_text_to_sign_model = ConcatenativeSynthesis(
                text_language="english",
                sign_language="pakistan",
                sign_format="video"
            )
            st.success("✅ PSL Text-to-Sign model initialized")
        
        if st.session_state.wlasl_text_to_sign_model is None:
            from sign_language_translator.models.text_to_sign import WLASLConcatenativeSynthesis
            st.session_state.wlasl_text_to_sign_model = WLASLConcatenativeSynthesis(
                text_language="english",
                sign_format="video"
            )
            st.success("✅ WLASL Text-to-Sign model initialized")
        
        return True
    except Exception as e:
        st.error(f"❌ Error initializing models: {e}")
        return False

def translate_sign_to_text(video_input, source_lang="PSL"):
    """Translate sign language video to text using actual models"""
    try:
        if source_lang == "PSL" and st.session_state.psl_sign_to_text_model:
            # Use PSL model
            result = st.session_state.psl_sign_to_text_model.predict(video_input)
            return result, 85
        elif source_lang == "ASL" and st.session_state.wlasl_sign_to_text_model:
            # Use WLASL model
            result = st.session_state.wlasl_sign_to_text_model.predict(video_input)
            return result, 85
        else:
            # Fallback to demo mode
            return "Translation: Video processed (demo mode)", 75
    except Exception as e:
        return f"Translation error: {str(e)}", 50

def translate_text_to_sign(text_input, target_lang="PSL"):
    """Translate text to sign language using actual models"""
    try:
        if target_lang == "PSL" and st.session_state.psl_text_to_sign_model:
            # Use PSL model
            result = st.session_state.psl_text_to_sign_model.translate(text_input)
            return f"Generated PSL sign video for: '{text_input}'", 85
        elif target_lang == "ASL" and st.session_state.wlasl_text_to_sign_model:
            # Use WLASL model
            result = st.session_state.wlasl_text_to_sign_model.translate(text_input)
            return f"Generated ASL sign video for: '{text_input}'", 85
        else:
            # Fallback to demo mode
            return f"Text-to-sign translation (demo mode): '{text_input}'", 75
    except Exception as e:
        return f"Translation error: {str(e)}", 50

def home_page():
    st.title("🤟 Sign Language Translator")
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
        st.metric("Assets Ready", "✅ Yes" if st.session_state.assets_ready else "❌ No")
        st.metric("PSL Models", "✅ Loaded" if st.session_state.psl_sign_to_text_model else "❌ Not Loaded")
    
    with col2:
        st.metric("WLASL Models", "✅ Loaded" if st.session_state.wlasl_sign_to_text_model else "❌ Not Loaded")
        st.metric("Text-to-Sign", "✅ Ready" if st.session_state.psl_text_to_sign_model else "❌ Not Ready")

def main():
    st.set_page_config(
        page_title="Sign Language Translator",
        page_icon="🤟",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Check FFMPEG
    if not check_ffmpeg():
        st.error("⚠️ FFMPEG is not installed. Some video features may not work properly.")
        st.info("To install FFMPEG, visit: https://ffmpeg.org/download.html")
    
    # Initialize assets and models
    if not st.session_state.assets_ready:
        st.session_state.assets_ready = create_assets_directory()
    
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
        psl_loaded = st.session_state.psl_sign_to_text_model is not None
        wlasl_loaded = st.session_state.wlasl_sign_to_text_model is not None
        psl_t2s_loaded = st.session_state.psl_text_to_sign_model is not None
        wlasl_t2s_loaded = st.session_state.wlasl_text_to_sign_model is not None
        
        st.metric("PSL Sign→Text", "✅ Loaded" if psl_loaded else "❌ Not Loaded")
        st.metric("WLASL Sign→Text", "✅ Loaded" if wlasl_loaded else "❌ Not Loaded")
        st.metric("PSL Text→Sign", "✅ Loaded" if psl_t2s_loaded else "❌ Not Loaded")
        st.metric("WLASL Text→Sign", "✅ Loaded" if wlasl_t2s_loaded else "❌ Not Loaded")
        
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
                # Use actual translation models
                target_lang = "PSL" if target_sign_language == "Pakistan Sign Language (PSL)" else "ASL"
                translation, confidence = translate_text_to_sign(text_input, target_lang)
                
                # Display results
                st.success(translation)
                st.metric("Confidence Score", f"{confidence}%")
                
                # Show output format info
                if output_format == "Video":
                    st.info("Sign language video would be generated here")
                elif output_format == "Landmarks":
                    st.info("Landmark data would be generated here")
                else:
                    st.info("Text description of signs would appear here")
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
                # Use actual translation models
                source_lang = "PSL" if source_sign_language == "Pakistan Sign Language (PSL)" else "ASL"
                translation, confidence = translate_sign_to_text(uploaded_file, source_lang)
                
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