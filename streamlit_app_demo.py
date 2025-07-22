import streamlit as st
import os
import tempfile

# --- Helper Functions for Demo Mode ---

def mock_text_to_sign(text, source_lang, target_lang):
    """Mocks the text-to-sign conversion."""
    st.success(f"**Demo Mode:** Conversion from '{source_lang}' text to '{target_lang}' sign.")
    st.info(f"Input Text: '{text}'")
    st.write("Displaying a placeholder video for the translated sign.")
    
    # Use a sample video from the project assets
    demo_video_path = "sign_language_translator/assets_WLASL/Common_WLASL_videos/Common_WLASL_videos/how.mp4"
    if os.path.exists(demo_video_path):
        st.video(demo_video_path)
    else:
        st.warning(f"Demo video not found at: {demo_video_path}. This would show the sign language video.")
    return "demo_video.mp4"

def mock_sign_to_text(video_file, source_lang, target_lang):
    """Mocks the sign-to-text conversion."""
    st.success(f"**Demo Mode:** Conversion from '{source_lang}' sign to '{target_lang}' text.")
    if video_file:
        st.info(f"Received video: {video_file.name}")
        st.video(video_file)
    st.write("Predicted Text (Gloss):")
    st.code("hello how are you", language="text")
    return "hello how are you"

def mock_sign_to_sign(video_file, source_lang, target_lang):
    """Mocks the sign-to-sign conversion."""
    st.success(f"**Demo Mode:** Conversion from '{source_lang}' sign to '{target_lang}' sign.")
    if video_file:
        st.info(f"Received source video: {video_file.name}")
        st.video(video_file)
    st.write("Displaying a placeholder video for the translated sign.")
    
    demo_video_path = "sign_language_translator/assets_WLASL/Common_WLASL_videos/Common_WLASL_videos/house.mp4"
    if os.path.exists(demo_video_path):
        st.video(demo_video_path)
    else:
        st.warning(f"Demo video not found at: {demo_video_path}. This would show the translated sign language video.")
    return "demo_translation.mp4"

def record_live_video_mock(duration=5):
    """Mocks live video recording."""
    st.info("Live video recording is a placeholder feature in this demo.")
    if st.button("Start Recording (Demo)"):
        with st.spinner(f"Pretending to record for {duration} seconds..."):
            import time
            time.sleep(duration)
        st.success("Recording finished (mocked). A temporary file would be created.")
        # In a real app, this would return the path to the recorded video file.
        # For the demo, we don't need to return anything as the translate button will check for an uploaded file.
    return None

# --- Main Streamlit App UI ---

st.set_page_config(page_title="Sign Language Translator", layout="wide")

st.title("🧏 Sign Language Translator")
st.warning("⚠️ This is a UI demo only. The model backend is not connected. All outputs are placeholders.", icon="🚀")


# --- Sidebar for selections ---
with st.sidebar:
    st.header("Conversion Settings")
    conversion_mode = st.selectbox(
        "Select Conversion Mode",
        ("Text to Sign", "Sign to Text", "Sign to Sign")
    )

    if conversion_mode == "Text to Sign":
        source_lang_text = "English" # Text is always English
        target_lang_sign = st.selectbox("Select Target Sign Language", ("PSL", "WLASL"))
        st.write(f"**Mode:** `{source_lang_text} ➡️ {target_lang_sign} Sign`")
        source_lang, target_lang = source_lang_text, target_lang_sign

    elif conversion_mode == "Sign to Text":
        source_lang_sign = st.selectbox("Select Source Sign Language", ("PSL", "WLASL"))
        target_lang_text = "English"
        st.write(f"**Mode:** `{source_lang_sign} Sign ➡️ {target_lang_text}`")
        source_lang, target_lang = source_lang_sign, target_lang_text

    elif conversion_mode == "Sign to Sign":
        source_lang = st.selectbox("Select Source Sign Language", ("PSL", "WLASL"))
        target_lang = st.selectbox("Select Target Sign Language", ("PSL", "WLASL"), index=1)
        st.write(f"**Mode:** `{source_lang} Sign ➡️ {target_lang} Sign`")


# --- Main panel for I/O ---
col1, col2 = st.columns(2)

if conversion_mode == "Text to Sign":
    with col1:
        st.header("Input Text")
        input_text = st.text_area("Enter English text to translate:", "hello", height=150)
        if st.button("Translate to Sign Video", use_container_width=True, type="primary"):
            if input_text:
                with col2:
                    st.header("Output Video")
                    with st.spinner("Generating sign video... (demo)"):
                        mock_text_to_sign(input_text, "English", target_lang)
            else:
                st.warning("Please enter some text.")

elif conversion_mode in ("Sign to Text", "Sign to Sign"):
    with col1:
        st.header("Input Video")
        input_method = st.radio("Select input method:", ("Upload a video", "Record live video"))

        uploaded_file = None
        if input_method == "Upload a video":
            uploaded_file = st.file_uploader("Choose a video file (.mp4)", type=["mp4"])
        else:
            record_live_video_mock()
            st.info("After 'recording', please upload the file to proceed in this demo.")

        if st.button("Translate", use_container_width=True, type="primary"):
            if uploaded_file:
                with col2:
                    if conversion_mode == "Sign to Text":
                        st.header("Output Text")
                        with st.spinner("Processing video and translating to text... (demo)"):
                            mock_sign_to_text(uploaded_file, source_lang, "English")
                    else: # Sign to Sign
                        st.header("Output Video")
                        with st.spinner("Translating sign video... (demo)"):
                            mock_sign_to_sign(uploaded_file, source_lang, target_lang)
            else:
                st.error("Please upload a video file.") 