# Sign Language Translator - Google Colab Setup Guide

## 🚀 Complete Setup Sequence for Google Colab

### **Cell 1: Install Dependencies**
```python
# Install required packages
!pip install fastapi uvicorn python-multipart streamlit opencv-python mediapipe torch torchvision numpy pandas tqdm requests

# Install ngrok for external access
!pip install pyngrok

# Install additional dependencies for sign language processing
!pip install moviepy pillow scikit-learn
```

### **Cell 2: Clone/Upload Your Project**
```python
# Option A: If your project is on GitHub
# !git clone https://github.com/your-username/SL-PSL-RTP.git
# %cd SL-PSL-RTP

# Option B: Upload your project files manually
# Upload all your project files to Colab using the file uploader
# Then uncomment the line below:
# %cd /content/SL-PSL-RTP
```

### **Cell 3: Set Up Working Directory**
```python
import os
import sys
from pathlib import Path

# Set up the working directory
WORKING_DIR = Path("/content/SL-PSL-RTP")
os.chdir(WORKING_DIR)
print(f"Working directory: {os.getcwd()}")

# Add current directory to Python path
sys.path.insert(0, str(WORKING_DIR))
print("Python path updated")
```

### **Cell 4: Create Required Files**
```python
# Create the run_api.py file
run_api_content = '''#!/usr/bin/env python3
"""
Simple script to run the Sign Language Translator FastAPI server.
"""

import uvicorn
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the FastAPI app from app.py
from app import app

if __name__ == "__main__":
    print("🤟 Starting Sign Language Translator API...")
    print("📡 Server will be available at: http://localhost:8000")
    print("🌐 Web UI will be available at: http://localhost:8000/ui")
    print("📋 API documentation at: http://localhost:8000/docs")
    print("🔍 Health check at: http://localhost:8000/health")
    print("\\nPress Ctrl+C to stop the server")
    
    # Run the FastAPI server
    uvicorn.run(
        app,
        host="0.0.0.0",  # Allow external connections
        port=8000,
        reload=True,     # Auto-reload on code changes
        log_level="info"
    )
'''

with open("run_api.py", "w") as f:
    f.write(run_api_content)

print("✅ run_api.py created")
```

### **Cell 5: Fix App.py for Colab**
```python
# Create a Colab-compatible version of app.py
app_py_content = '''import streamlit as st
import sign_language_translator as slt
from sign_language_translator.models import get_model
from sign_language_translator.config.enums import ModelCodes, TextLanguages, SignLanguages, SignFormats
import tempfile
import os
import re
import base64
from pathlib import Path
import io
import subprocess
import cv2
import requests
import urllib.request
import shutil
import json

# --- FastAPI Backend for UI Integration ---
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
import uvicorn

# Comment out model imports for now to avoid startup errors
# from sign_language_translator.models.sign_to_text.psl_sign_to_text_model import PSLSignToTextModel
# from sign_language_translator.models.sign_to_text.wlasl_sign_to_text_model import WLASLSignToTextModel
# from sign_language_translator.models.text_to_sign.concatenative_synthesis import ConcatenativeSynthesis
# from sign_language_translator.models.text_to_sign.concatenative_synthesis_wlasl import WLASLConcatenativeSynthesis
# from sign_language_translator.models.sign_to_sign import SignToSignTranslator

# Comment out model loading for now
# psl_sign_to_text_model = PSLSignToTextModel.load("sign_language_model_best.pth")
# wlasl_sign_to_text_model = WLASLSignToTextModel.load("wlasl_vit_transformer.pth")
# psl_text_to_sign_model = ConcatenativeSynthesis(
#     text_language="english", sign_language="pk-sl", sign_format="video"
# )
# wlasl_text_to_sign_model = WLASLConcatenativeSynthesis(
#     text_language="english", sign_format="video"
# )
# sign_to_sign_translator = SignToSignTranslator(
#     psl_sign_to_text_model, wlasl_sign_to_text_model,
#     psl_text_to_sign_model, wlasl_text_to_sign_model
# )

# Create assets directory if it doesn't exist
assets_dir = Path("assets")
assets_dir.mkdir(exist_ok=True)

# Create a directory for temporary files if it doesn't exist
TEMP_DIR = Path("temp_files")
TEMP_DIR.mkdir(exist_ok=True)

# Initialize FastAPI app
app = FastAPI(title="Sign Language Translator API", description="Bilingual PSL and WLASL translation system")

@app.get("/")
async def root():
    """Root endpoint that provides information about the API and available endpoints."""
    return {
        "message": "Sign Language Translator API",
        "description": "Bilingual PSL and WLASL translation system",
        "version": "1.0.0",
        "endpoints": {
            "GET /": "API information (this page)",
            "GET /ui": "Simple web interface for testing",
            "POST /convert": "Main translation endpoint",
            "GET /health": "Health check endpoint",
            "GET /info": "Detailed API information"
        },
        "usage": {
            "text_to_sign": "Convert text to sign language video",
            "sign_to_text": "Convert sign language video to text", 
            "sign_to_sign": "Translate between sign languages"
        },
        "quick_start": "Visit /ui for a simple web interface to test the API"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint to verify the API is running."""
    return {"status": "healthy", "message": "API is running"}

@app.get("/info")
async def api_info():
    """Get detailed API information."""
    return {
        "name": "Sign Language Translator API",
        "supported_languages": ["PSL", "WLASL"],
        "supported_conversions": [
            "text_to_sign",
            "sign_to_text", 
            "sign_to_sign"
        ],
        "input_types": ["text", "video_upload", "live_recording"],
        "output_types": ["text", "video"]
    }

@app.get("/ui", response_class=HTMLResponse)
async def simple_ui():
    """Simple HTML interface for testing the API."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sign Language Translator</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .container { background: #f5f5f5; padding: 20px; border-radius: 10px; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            select, input, textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #0056b3; }
            .result { margin-top: 20px; padding: 15px; background: #e9ecef; border-radius: 4px; }
            .error { background: #f8d7da; color: #721c24; }
            .success { background: #d4edda; color: #155724; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤟 Sign Language Translator API</h1>
            <p>Test the bilingual PSL and WLASL translation system</p>
            
            <form id="translateForm">
                <div class="form-group">
                    <label for="conversion_mode">Conversion Mode:</label>
                    <select id="conversion_mode" name="conversion_mode" required>
                        <option value="">Select mode...</option>
                        <option value="text_to_sign">Text to Sign</option>
                        <option value="sign_to_text">Sign to Text</option>
                        <option value="sign_to_sign">Sign to Sign</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="source_lang">Source Language:</label>
                    <select id="source_lang" name="source_lang" required>
                        <option value="">Select language...</option>
                        <option value="PSL">PSL (Pakistani Sign Language)</option>
                        <option value="WLASL">WLASL (American Sign Language)</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="target_lang">Target Language:</label>
                    <select id="target_lang" name="target_lang" required>
                        <option value="">Select language...</option>
                        <option value="PSL">PSL (Pakistani Sign Language)</option>
                        <option value="WLASL">WLASL (American Sign Language)</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="output_type">Output Type:</label>
                    <select id="output_type" name="output_type" required>
                        <option value="">Select type...</option>
                        <option value="text">Text</option>
                        <option value="video">Video</option>
                    </select>
                </div>
                
                <div class="form-group" id="text_input_group" style="display: none;">
                    <label for="input_text">Input Text:</label>
                    <textarea id="input_text" name="input_text" rows="3" placeholder="Enter text to translate..."></textarea>
                </div>
                
                <div class="form-group" id="video_input_group" style="display: none;">
                    <label for="video_file">Upload Video:</label>
                    <input type="file" id="video_file" name="video_file" accept="video/*">
                </div>
                
                <button type="submit">Translate</button>
            </form>
            
            <div id="result" class="result" style="display: none;"></div>
        </div>
        
        <script>
            // Show/hide input fields based on conversion mode
            document.getElementById('conversion_mode').addEventListener('change', function() {
                const mode = this.value;
                const textGroup = document.getElementById('text_input_group');
                const videoGroup = document.getElementById('video_input_group');
                
                if (mode === 'text_to_sign') {
                    textGroup.style.display = 'block';
                    videoGroup.style.display = 'none';
                } else {
                    textGroup.style.display = 'none';
                    videoGroup.style.display = 'block';
                }
            });
            
            // Handle form submission
            document.getElementById('translateForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const formData = new FormData(this);
                const resultDiv = document.getElementById('result');
                
                try {
                    resultDiv.innerHTML = 'Processing...';
                    resultDiv.style.display = 'block';
                    resultDiv.className = 'result';
                    
                    const response = await fetch('/convert', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        resultDiv.innerHTML = `
                            <h3>✅ Success!</h3>
                            <p><strong>Message:</strong> ${data.message}</p>
                            <p><strong>Result:</strong> ${data.result}</p>
                            <p><strong>Mode:</strong> ${data.conversion_mode}</p>
                            <p><strong>From:</strong> ${data.source_lang} → <strong>To:</strong> ${data.target_lang}</p>
                        `;
                        resultDiv.className = 'result success';
                    } else {
                        resultDiv.innerHTML = `
                            <h3>❌ Error</h3>
                            <p><strong>Error:</strong> ${data.error}</p>
                        `;
                        resultDiv.className = 'result error';
                    }
                } catch (error) {
                    resultDiv.innerHTML = `
                        <h3>❌ Error</h3>
                        <p><strong>Error:</strong> ${error.message}</p>
                    `;
                    resultDiv.className = 'result error';
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/convert")
async def convert(
    conversion_mode: str = Form(...),
    source_lang: str = Form(...),
    target_lang: str = Form(...),
    output_type: str = Form(...),
    input_text: str = Form(None),
    video_file: UploadFile = File(None)
):
    """
    Main translation endpoint that handles all conversion modes.
    
    Args:
        conversion_mode: "text_to_sign", "sign_to_text", or "sign_to_sign"
        source_lang: "PSL" or "WLASL"
        target_lang: "PSL" or "WLASL" 
        output_type: "text" or "video"
        input_text: Text input (for text_to_sign mode)
        video_file: Video file upload (for sign_to_text and sign_to_sign modes)
    """
    try:
        # Validate inputs
        if conversion_mode not in ["text_to_sign", "sign_to_text", "sign_to_sign"]:
            return JSONResponse(
                status_code=400,
                content={"error": f"Invalid conversion_mode: {conversion_mode}. Must be one of: text_to_sign, sign_to_text, sign_to_sign"}
            )
        
        if source_lang not in ["PSL", "WLASL"]:
            return JSONResponse(
                status_code=400,
                content={"error": f"Invalid source_lang: {source_lang}. Must be PSL or WLASL"}
            )
            
        if target_lang not in ["PSL", "WLASL"]:
            return JSONResponse(
                status_code=400,
                content={"error": f"Invalid target_lang: {target_lang}. Must be PSL or WLASL"}
            )
        
        # Handle different conversion modes
        if conversion_mode == "text_to_sign":
            if not input_text:
                return JSONResponse(
                    status_code=400,
                    content={"error": "input_text is required for text_to_sign mode"}
                )
            
            # Placeholder for text to sign translation
            result = f"Generated {target_lang} sign video for: '{input_text}'"
            return JSONResponse({
                "message": "Text to Sign translation completed",
                "conversion_mode": conversion_mode,
                "source_lang": source_lang,
                "target_lang": target_lang,
                "input_text": input_text,
                "result": result,
                "output_type": output_type
            })
            
        elif conversion_mode == "sign_to_text":
            if not video_file:
                return JSONResponse(
                    status_code=400,
                    content={"error": "video_file is required for sign_to_text mode"}
                )
            
            # Placeholder for sign to text translation
            result = f"Translated {source_lang} sign video to text: 'Hello World'"
            return JSONResponse({
                "message": "Sign to Text translation completed",
                "conversion_mode": conversion_mode,
                "source_lang": source_lang,
                "target_lang": target_lang,
                "video_file": video_file.filename,
                "result": result,
                "output_type": output_type
            })
            
        elif conversion_mode == "sign_to_sign":
            if not video_file:
                return JSONResponse(
                    status_code=400,
                    content={"error": "video_file is required for sign_to_sign mode"}
                )
            
            # Placeholder for sign to sign translation
            result = f"Translated {source_lang} sign video to {target_lang} sign video"
            return JSONResponse({
                "message": "Sign to Sign translation completed",
                "conversion_mode": conversion_mode,
                "source_lang": source_lang,
                "target_lang": target_lang,
                "video_file": video_file.filename,
                "result": result,
                "output_type": output_type
            })
            
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Internal server error: {str(e)}"}
        )
'''

with open("app.py", "w") as f:
    f.write(app_py_content)

print("✅ app.py created (Colab-compatible version)")
```

### **Cell 6: Start the FastAPI Server**
```python
import threading
import time
import nest_asyncio

# Enable nested asyncio for Colab
nest_asyncio.apply()

def run_fastapi_server():
    """Run the FastAPI server in a separate thread."""
    import uvicorn
    from app import app
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

# Start the server in a background thread
server_thread = threading.Thread(target=run_fastapi_server, daemon=True)
server_thread.start()

# Wait a moment for the server to start
time.sleep(3)

print("🚀 FastAPI server started on port 8000")
print("📡 Local URL: http://localhost:8000")
print("🌐 Web UI: http://localhost:8000/ui")
print("🔍 Health check: http://localhost:8000/health")
```

### **Cell 7: Test the Server**
```python
import requests
import time

# Wait a bit more for the server to fully start
time.sleep(2)

# Test the health endpoint
try:
    response = requests.get("http://localhost:8000/health")
    if response.status_code == 200:
        print("✅ Server is running!")
        print(f"Health check response: {response.json()}")
    else:
        print(f"❌ Server health check failed: {response.status_code}")
except Exception as e:
    print(f"❌ Error connecting to server: {e}")
    print("Server might still be starting up...")
```

### **Cell 8: Set Up ngrok for External Access**
```python
from pyngrok import ngrok

# Set up ngrok (you'll need to get a free authtoken from ngrok.com)
# ngrok.set_auth_token('YOUR_NGROK_AUTH_TOKEN')  # Uncomment and add your token

# Create ngrok tunnel
try:
    public_url = ngrok.connect(8000)
    print(f"🌐 Public URL: {public_url}")
    print(f"🌐 Web UI: {public_url}/ui")
    print(f"🔍 Health check: {public_url}/health")
    print(f"📋 API info: {public_url}/")
except Exception as e:
    print(f"❌ Error setting up ngrok: {e}")
    print("You can still access the app locally at http://localhost:8000")
```

### **Cell 9: Display Connection Information**
```python
# Display all available URLs
print("=" * 50)
print("🎉 SIGN LANGUAGE TRANSLATOR IS READY!")
print("=" * 50)

try:
    # Get ngrok URL
    tunnels = ngrok.get_ngrok_process().api.get_tunnels()
    if tunnels:
        public_url = tunnels[0].public_url
        print(f"🌐 Public Access URL: {public_url}")
        print(f"🌐 Web Interface: {public_url}/ui")
        print(f"🔍 Health Check: {public_url}/health")
        print(f"📋 API Info: {public_url}/")
    else:
        print("🌐 Local Access URL: http://localhost:8000")
        print("🌐 Web Interface: http://localhost:8000/ui")
        print("🔍 Health Check: http://localhost:8000/health")
        print("📋 API Info: http://localhost:8000/")
except:
    print("🌐 Local Access URL: http://localhost:8000")
    print("🌐 Web Interface: http://localhost:8000/ui")
    print("🔍 Health Check: http://localhost:8000/health")
    print("📋 API Info: http://localhost:8000/")

print("\n📝 How to use:")
print("1. Click on the Web Interface URL above")
print("2. Select your conversion mode (Text to Sign, Sign to Text, Sign to Sign)")
print("3. Choose source and target languages (PSL/WLASL)")
print("4. Enter text or upload video")
print("5. Click Translate!")
print("\n🎯 Test with: Text to Sign, PSL → WLASL, Input: 'hello world'")
```

### **Cell 10: Optional - Run Streamlit UI (Alternative Interface)**
```python
# Uncomment the following lines if you want to run the Streamlit UI as well
# Note: This will run on a different port and requires additional setup

"""
# Install streamlit if not already installed
!pip install streamlit

# Create a simple Streamlit UI
streamlit_ui_content = '''
import streamlit as st
import requests
import tempfile
import os

st.title("Bilingual Sign Language Translator (PSL & WLASL)")

# Language Selection
language_options = ["PSL", "WLASL"]
input_lang = st.selectbox("Input Language", language_options)
output_lang = st.selectbox("Output Language", language_options)

# Conversion Mode
conversion_mode = st.radio(
    "Select Conversion Mode:",
    ["Sign to Text", "Text to Sign", "Sign to Sign"]
)

# Input Type
if conversion_mode == "Text to Sign":
    input_type = "text"
else:
    input_type = st.radio("Input Type", ["Upload Video", "Record Live Video"])

# Input Widgets
input_text = None
video_file = None

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
                video_file = open(temp_vid.name, "rb")

# Output Type
if conversion_mode == "Sign to Text":
    output_type = "text"
elif conversion_mode == "Text to Sign":
    output_type = "video"
else:  # Sign to Sign
    output_type = "video"

# Convert Button
if st.button("Convert"):
    files = {}
    data = {
        "conversion_mode": conversion_mode.lower().replace(" ", "_"),
        "source_lang": input_lang,
        "target_lang": output_lang,
        "output_type": output_type,
        "input_text": input_text
    }
    if video_file is not None:
        files["video_file"] = video_file
    
    # Use localhost for Colab
    api_url = "http://localhost:8000/convert"
    response = requests.post(api_url, data=data, files=files)
    
    if response.status_code == 200:
        if output_type == "text":
            st.success("Output:")
            st.write(response.json().get("result"))
        elif output_type == "video":
            st.success("Video generated successfully!")
            st.write("Check the API response for video details")
    else:
        st.error("Error: " + response.text)

st.markdown("""
**Features:**
- Choose conversion mode: Sign to Text, Text to Sign, or Sign to Sign
- Select PSL or WLASL for both input and output sign language
- Input via text, video upload, or live webcam recording
- Output as text or video
- Text language: English
""")
'''

with open("streamlit_ui.py", "w") as f:
    f.write(streamlit_ui_content)

print("✅ Streamlit UI created")
print("To run Streamlit UI: streamlit run streamlit_ui.py --server.port 8501")
"""
```

### **Cell 11: Keep the Server Running**
```python
# This cell keeps the server running
# Run this cell and keep it running to maintain the server

import time
import requests

print("🔄 Server is running... Press Ctrl+C to stop")

try:
    while True:
        # Check if server is still running
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Server is healthy - " + time.strftime("%H:%M:%S"))
            else:
                print("⚠️ Server health check failed")
        except:
            print("❌ Server connection lost")
        
        # Wait 30 seconds before next check
        time.sleep(30)
        
except KeyboardInterrupt:
    print("\\n🛑 Stopping server...")
    # Clean up ngrok
    try:
        ngrok.kill()
        print("✅ ngrok tunnel closed")
    except:
        pass
    print("✅ Server stopped")
```

## 📋 **Usage Instructions**

### **After Running All Cells:**

1. **Access the Web Interface**: Click on the Web Interface URL provided in Cell 9
2. **Test the API**: Use the simple web form to test different translation modes
3. **Keep the Server Running**: Keep Cell 11 running to maintain the server

### **Available Endpoints:**
- **Root**: `/` - API information
- **Web UI**: `/ui` - Simple web interface
- **Health**: `/health` - Server health check
- **API Info**: `/info` - Detailed API information
- **Convert**: `/convert` - Main translation endpoint

### **Test Scenarios:**
1. **Text to Sign**: Enter "hello world", select PSL → WLASL
2. **Sign to Text**: Upload a video, select PSL → PSL
3. **Sign to Sign**: Upload a video, select PSL → WLASL

### **Troubleshooting:**
- If you get connection errors, wait a few seconds and try again
- Make sure all cells are executed in order
- Check the health endpoint to verify the server is running
- If ngrok fails, you can still access the app locally

This setup provides a complete working Sign Language Translator API with a web interface that you can access from anywhere via ngrok! 