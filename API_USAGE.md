# Sign Language Translator API - Usage Guide

## 🚀 Quick Start

### Option 1: Run the API Server
```bash
# Start the FastAPI server
python run_api.py
```

### Option 2: Use ngrok for external access
```bash
# Start the API server
python run_api.py

# In another terminal, expose with ngrok
ngrok http 8000
```

## 🌐 Available Endpoints

### 1. Root Endpoint
- **URL**: `GET /`
- **Description**: API information and available endpoints
- **Example**: Visit your ngrok URL (e.g., `https://abc123.ngrok.io/`)

### 2. Web Interface
- **URL**: `GET /ui`
- **Description**: Simple web form to test the API
- **Example**: Visit `https://abc123.ngrok.io/ui`

### 3. Health Check
- **URL**: `GET /health`
- **Description**: Check if the API is running
- **Example**: `https://abc123.ngrok.io/health`

### 4. API Information
- **URL**: `GET /info`
- **Description**: Detailed API information
- **Example**: `https://abc123.ngrok.io/info`

### 5. Main Translation Endpoint
- **URL**: `POST /convert`
- **Description**: Perform sign language translations

## 📝 How to Use

### Using the Web Interface (Recommended)

1. **Start the server**: `python run_api.py`
2. **Expose with ngrok**: `ngrok http 8000`
3. **Open the web interface**: Visit `https://YOUR_NGROK_URL/ui`
4. **Select options**:
   - Conversion Mode: Text to Sign, Sign to Text, or Sign to Sign
   - Source Language: PSL or WLASL
   - Target Language: PSL or WLASL
   - Output Type: Text or Video
5. **Enter input**: Text or upload video
6. **Click Translate**: See the results

### Using the API Directly

#### Text to Sign Translation
```bash
curl -X POST "https://YOUR_NGROK_URL/convert" \
  -F "conversion_mode=text_to_sign" \
  -F "source_lang=PSL" \
  -F "target_lang=WLASL" \
  -F "output_type=video" \
  -F "input_text=hello world"
```

#### Sign to Text Translation
```bash
curl -X POST "https://YOUR_NGROK_URL/convert" \
  -F "conversion_mode=sign_to_text" \
  -F "source_lang=PSL" \
  -F "target_lang=PSL" \
  -F "output_type=text" \
  -F "video_file=@your_video.mp4"
```

#### Sign to Sign Translation
```bash
curl -X POST "https://YOUR_NGROK_URL/convert" \
  -F "conversion_mode=sign_to_sign" \
  -F "source_lang=PSL" \
  -F "target_lang=WLASL" \
  -F "output_type=video" \
  -F "video_file=@your_video.mp4"
```

## 🔧 Troubleshooting

### "Not Found" Error
- Make sure the FastAPI server is running
- Check that you're using the correct ngrok URL
- Try visiting `/ui` for the web interface

### Connection Refused
- Ensure the FastAPI server is running on port 8000
- Check that ngrok is pointing to the correct port
- Verify firewall settings

### Import Errors
- Make sure all dependencies are installed
- Check that you're in the correct directory
- Try running `pip install -r requirements.txt`

## 📋 Supported Features

### Conversion Modes
- ✅ **Text to Sign**: Convert English text to sign language videos
- ✅ **Sign to Text**: Convert sign language videos to text
- ✅ **Sign to Sign**: Translate between PSL and WLASL

### Languages
- ✅ **PSL**: Pakistani Sign Language
- ✅ **WLASL**: American Sign Language (WLASL dataset)

### Input Types
- ✅ **Text**: English text input
- ✅ **Video Upload**: Upload sign language videos
- ✅ **Live Recording**: Record videos using webcam (via Streamlit UI)

### Output Types
- ✅ **Text**: Translated text output
- ✅ **Video**: Generated sign language videos

## 🎯 Example Workflows

### 1. Text to Sign (PSL)
1. Select "Text to Sign" mode
2. Choose PSL as target language
3. Enter text: "hello world"
4. Get PSL sign video

### 2. Sign to Text (WLASL)
1. Select "Sign to Text" mode
2. Choose WLASL as source language
3. Upload WLASL sign video
4. Get English text translation

### 3. Sign to Sign (PSL → WLASL)
1. Select "Sign to Sign" mode
2. Choose PSL as source, WLASL as target
3. Upload PSL sign video
4. Get WLASL sign video

## 🔗 Integration with Streamlit UI

The Streamlit UI (`sign_language_translator/ui.py`) can also connect to this API:

1. Update the ngrok URL in `ui.py` line 58
2. Run the Streamlit UI: `streamlit run sign_language_translator/ui.py`
3. Use the full-featured interface with live video recording

## 📞 Support

If you encounter issues:
1. Check the server logs for error messages
2. Verify all endpoints are accessible
3. Test with the web interface first
4. Check the health endpoint: `/health` 