# Vercel Deployment Guide with Cloud Assets

This guide explains how to deploy your sign language translator on Vercel while accessing assets stored in the cloud.

## 🎯 Overview

When deploying on Vercel, your application runs on cloud servers that cannot access files on your local PC. You need to store your assets in the cloud and access them via URLs.

## 📁 Asset Storage Options

### **Option 1: GitHub Releases (Recommended for Start)**

1. **Create a GitHub Release:**
   ```bash
   # Create a release on GitHub with your assets
   # Go to: https://github.com/Talhaattari209/SL-PSL-RTP/releases
   # Upload your video and landmark files as release assets
   ```

2. **Use the Assets Manager:**
   ```python
   from vercel_assets_manager import VercelAssetsManager
   
   # Initialize manager
   manager = VercelAssetsManager()
   
   # Setup GitHub releases
   manager.setup_cloud_storage("github", 
                              repo="Talhaattari209/SL-PSL-RTP",
                              tag="assets-v1.0")
   
   # Get asset path
   video_path = manager.get_asset_path("psl_videos", "pk-hfad-1_hello.mp4")
   ```

### **Option 2: Google Drive (Free & Easy)**

1. **Upload to Google Drive:**
   - Upload your video and landmark folders to Google Drive
   - Make them publicly accessible
   - Get sharing links

2. **Configure Assets Manager:**
   ```python
   manager.setup_cloud_storage("gdrive",
                              psl_videos="https://drive.google.com/uc?id=YOUR_PSL_FOLDER_ID",
                              wlasl_videos="https://drive.google.com/uc?id=YOUR_WLASL_FOLDER_ID",
                              wlasl_landmarks="https://drive.google.com/uc?id=YOUR_LANDMARKS_FOLDER_ID")
   ```

### **Option 3: AWS S3 (Production)**

1. **Upload to S3:**
   ```bash
   aws s3 cp ./sign_language_translator/assets/video1/videos s3://your-bucket/psl-videos --recursive
   aws s3 cp ./sign_language_translator/assets_WLASL s3://your-bucket/wlasl-assets --recursive
   ```

2. **Configure for Public Access:**
   ```python
   manager.setup_cloud_storage("s3",
                              bucket="your-bucket",
                              region="us-east-1",
                              access_key="YOUR_ACCESS_KEY",
                              secret_key="YOUR_SECRET_KEY")
   ```

## 🚀 Vercel Deployment Setup

### **1. Update your FastAPI app to use cloud assets:**

```python
# app.py
from fastapi import FastAPI
from vercel_assets_manager import VercelAssetsManager
import sign_language_translator as slt

app = FastAPI()

# Initialize assets manager
assets_manager = VercelAssetsManager()

@app.on_event("startup")
async def startup_event():
    """Initialize assets on startup."""
    # Setup cloud storage
    assets_manager.setup_cloud_storage("github", 
                                      repo="Talhaattari209/SL-PSL-RTP",
                                      tag="assets-v1.0")

@app.post("/convert")
async def convert_text_to_sign(text: str, input_language: str, output_language: str):
    """Convert text to sign language using cloud assets."""
    
    if output_language == "PSL":
        # Use PSL concatenative synthesis
        from sign_language_translator.models import ConcatenativeSynthesis
        
        # Create custom asset loader
        def custom_asset_loader(filename):
            return assets_manager.get_asset_path("psl_videos", filename)
        
        model = ConcatenativeSynthesis(
            text_language=input_language,
            sign_language="pakistan-sign-language",
            sign_format="video"
        )
        
        # Override asset loading
        model._get_asset_path = custom_asset_loader
        
        result = model.translate(text)
        return {"result": "PSL sign generated", "video_path": str(result)}
    
    elif output_language == "WLASL":
        # Use WLASL concatenative synthesis
        from sign_language_translator.models import WLASLConcatenativeSynthesis
        
        model = WLASLConcatenativeSynthesis(
            text_language=input_language,
            sign_format="landmarks",
            assets_path=assets_manager.cache_dir  # Use cached assets
        )
        
        result = model.translate(text)
        return {"result": "WLASL landmarks generated", "landmarks": str(result)}
```

### **2. Create vercel.json configuration:**

```json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ],
  "env": {
    "PYTHONPATH": "."
  },
  "functions": {
    "app.py": {
      "maxDuration": 30
    }
  }
}
```

### **3. Update requirements.txt:**

```txt
fastapi
uvicorn
requests
boto3
sign_language_translator
# Add other dependencies
```

## 📋 Step-by-Step Deployment

### **Step 1: Prepare Assets for Cloud**

1. **Create asset packages:**
   ```bash
   # Create compressed packages
   tar -czf psl_videos.tar.gz sign_language_translator/assets/video1/videos/
   tar -czf wlasl_videos.tar.gz sign_language_translator/assets_WLASL/Common_WLASL_videos/
   tar -czf wlasl_landmarks.tar.gz sign_language_translator/assets_WLASL/Augmented_LandMarks/
   ```

2. **Upload to cloud storage:**
   - **GitHub Releases:** Upload as release assets
   - **Google Drive:** Upload and get sharing links
   - **AWS S3:** Upload to S3 bucket

### **Step 2: Configure Assets Manager**

```python
# Create assets_config.json
{
  "storage_type": "cloud",
  "cloud_provider": "github",
  "github_release": {
    "repo": "Talhaattari209/SL-PSL-RTP",
    "tag": "assets-v1.0"
  },
  "cache_duration": 3600,
  "max_cache_size": 1073741824
}
```

### **Step 3: Deploy to Vercel**

1. **Connect GitHub repository:**
   ```bash
   # Vercel will automatically detect your FastAPI app
   # Just connect your GitHub repo in Vercel dashboard
   ```

2. **Set environment variables:**
   - Go to Vercel dashboard → Project Settings → Environment Variables
   - Add any API keys or configuration

3. **Deploy:**
   ```bash
   # Push to GitHub
   git add .
   git commit -m "Add Vercel deployment support"
   git push origin main
   
   # Vercel will automatically deploy
   ```

## 🔧 Asset Loading Strategies

### **Strategy 1: On-Demand Download**
```python
def get_asset_on_demand(filename):
    """Download asset only when needed."""
    return assets_manager.get_asset_path("psl_videos", filename)
```

### **Strategy 2: Preload Critical Assets**
```python
@app.on_event("startup")
async def preload_assets():
    """Preload commonly used assets."""
    common_words = ["hello", "world", "thank", "you"]
    
    for word in common_words:
        filename = f"pk-hfad-1_{word}.mp4"
        assets_manager.get_asset_path("psl_videos", filename)
```

### **Strategy 3: Hybrid Approach**
```python
def get_asset_hybrid(filename):
    """Try local first, then cloud."""
    # Try local
    local_path = f"sign_language_translator/assets/video1/videos/{filename}"
    if os.path.exists(local_path):
        return local_path
    
    # Fallback to cloud
    return assets_manager.get_asset_path("psl_videos", filename)
```

## 🐛 Troubleshooting

### **Error: "Asset not found"**
- Check if asset exists in cloud storage
- Verify URLs in configuration
- Check cache directory permissions

### **Error: "Download timeout"**
- Increase timeout in requests
- Use smaller asset files
- Implement retry logic

### **Error: "Cache full"**
- Clear cache: `manager.clear_cache()`
- Increase cache size in configuration
- Implement LRU cache eviction

### **Performance Issues**
- Use CDN for better download speeds
- Implement asset compression
- Cache frequently used assets

## 📊 Monitoring

```python
# Check cache status
cache_info = manager.get_cache_info()
print(f"Cache size: {cache_info['size'] / 1024 / 1024:.2f} MB")
print(f"Files cached: {cache_info['files']}")

# Monitor asset access
def log_asset_access(asset_type, filename, success):
    print(f"Asset access: {asset_type}/{filename} - {'SUCCESS' if success else 'FAILED'}")
```

This setup allows your Vercel deployment to access all necessary assets while keeping your local files secure and your repository lightweight! 