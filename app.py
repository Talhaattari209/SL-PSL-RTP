import streamlit as st
from sign_language_translator import Translator
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
        ["english", "urdu"],
        help="Select the text language"
    )
    
    sign_lang = st.selectbox(
        "Sign Language",
        ["psl"],
        help="Select the sign language"
    )
    
    sign_format = st.selectbox(
        "Sign Format",
        ["video", "landmarks"],
        help="Select the sign format"
    )
    
    # Initialize translator
    if st.button("Initialize Translator"):
        try:
            st.session_state.translator = Translator(
                model_code=model_code,
                text_lang=text_lang,
                sign_lang=sign_lang,
                sign_format=sign_format
            )
            st.success("Translator initialized successfully!")
        except Exception as e:
            st.error(f"Error initializing translator: {str(e)}")

# Main content area
if st.session_state.translator is None:
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
                            st.session_state.translator.translate(
                                inputs=[input_text],
                                output_dir=temp_dir,
                                save_format="mp4",
                                display=False
                            )
                            
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
            
            if st.button("Translate"):
                try:
                    with st.spinner("Translating..."):
                        # Perform translation
                        result = st.session_state.translator.translate(
                            inputs=[video_path],
                            display=False
                        )
                        
                        # Display the result
                        st.write("Translation:")
                        st.write(result)
                except Exception as e:
                    st.error(f"Translation error: {str(e)}")
                finally:
                    # Clean up temporary file
                    os.unlink(video_path) 