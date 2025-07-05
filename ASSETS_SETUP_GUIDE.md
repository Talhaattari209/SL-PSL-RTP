# Assets Setup Guide for Concatenative Synthesis

This guide explains how to connect your video assets for the concatenative synthesis system.

## 🎯 Overview

The concatenative synthesis system needs access to:
1. **PSL Videos**: `sign_language_translator/assets/video1/videos/`
2. **WLASL Videos**: `sign_language_translator/assets_WLASL/Common_WLASL_videos/`
3. **WLASL Landmarks**: `sign_language_translator/assets_WLASL/Augmented_LandMarks/Processed_Landmarks_WLASL/`

## 📁 Option 1: Set Custom Assets Directory (Recommended)

If your video assets are stored elsewhere, you can set a custom path:

```python
import sign_language_translator as slt

# Set custom assets directory
slt.Assets.set_root_dir("/path/to/your/assets")

# Now use concatenative synthesis
from sign_language_translator.models import ConcatenativeSynthesis

model = ConcatenativeSynthesis(
    text_language="urdu",
    sign_language="pakistan-sign-language", 
    sign_format="video"
)

result = model.translate("hello")
```

## 🔗 Option 2: Create Symbolic Links

Create symbolic links to your video folders:

### Windows:
```cmd
# Create symbolic link for PSL videos
mklink /D "sign_language_translator\assets\video1\videos" "C:\path\to\your\psl\videos"

# Create symbolic link for WLASL videos  
mklink /D "sign_language_translator\assets_WLASL\Common_WLASL_videos" "C:\path\to\your\wlasl\videos"

# Create symbolic link for WLASL landmarks
mklink /D "sign_language_translator\assets_WLASL\Augmented_LandMarks\Processed_Landmarks_WLASL" "C:\path\to\your\wlasl\landmarks"
```

### Linux/Mac:
```bash
# Create symbolic link for PSL videos
ln -s /path/to/your/psl/videos sign_language_translator/assets/video1/videos

# Create symbolic link for WLASL videos
ln -s /path/to/your/wlasl/videos sign_language_translator/assets_WLASL/Common_WLASL_videos

# Create symbolic link for WLASL landmarks
ln -s /path/to/your/wlasl/landmarks sign_language_translator/assets_WLASL/Augmented_LandMarks/Processed_Landmarks_WLASL
```

## ⬇️ Option 3: Download Assets

If you have URLs configured, download assets automatically:

```python
import sign_language_translator as slt

# Download PSL videos
psl_videos = slt.Assets.download("videos/pk-.*mp4")
print(f"Downloaded {len(psl_videos)} PSL videos")

# Download WLASL videos
wlasl_videos = slt.Assets.download("videos/wlasl-.*mp4") 
print(f"Downloaded {len(wlasl_videos)} WLASL videos")
```

## 🚀 Option 4: Use the Setup Script

Run the provided setup script:

```bash
python setup_assets.py
```

This interactive script will guide you through all options.

## 📋 Usage Examples

### PSL Text-to-Sign (Video Output)
```python
from sign_language_translator.models import ConcatenativeSynthesis

# Create PSL model
model = ConcatenativeSynthesis(
    text_language="urdu",
    sign_language="pakistan-sign-language",
    sign_format="video"
)

# Translate text to sign video
result = model.translate("hello world")
result.save("output_psl.mp4")
```

### WLASL Text-to-Sign (Landmarks Output)
```python
from sign_language_translator.models import WLASLConcatenativeSynthesis

# Create WLASL model with custom assets path
model = WLASLConcatenativeSynthesis(
    text_language="english",
    sign_format="landmarks",
    assets_path="/path/to/wlasl/assets"
)

# Translate text to landmarks
result = model.translate("hello world")
```

### PSL Text-to-Sign (Landmarks Output)
```python
from sign_language_translator.models import ConcatenativeSynthesis

# Create PSL model for landmarks
model = ConcatenativeSynthesis(
    text_language="urdu",
    sign_language="pakistan-sign-language",
    sign_format="landmarks",
    sign_embedding_model="mediapipe-world"
)

# Translate text to landmarks
result = model.translate("hello world")
```

## 🔧 Configuration Files

### URLs Configuration
The system uses URL files to download assets. Check these files:
- `sign_language_translator/config/urls.json` - Primary URLs
- `sign_language_translator/config/pk-dictionary-urls.json` - PSL video URLs
- `sign_language_translator/config/archive-urls.json` - Archive URLs

### Asset Structure
Expected directory structure:
```
assets/
├── videos/
│   ├── pk-hfad-1_airplane.mp4
│   ├── pk-hfad-1_hello.mp4
│   └── ...
├── landmarks/
│   ├── pk-hfad-1_airplane.landmarks-mediapipe-world.csv
│   └── ...
└── checksum.json

assets_WLASL/
├── Common_WLASL_videos/
│   ├── hello.mp4
│   ├── world.mp4
│   └── ...
├── Augmented_LandMarks/
│   └── Processed_Landmarks_WLASL/
└── mappings/
    ├── psl_to_wlasl_mapping.json
    └── filtered_wlasl.json
```

## 🐛 Troubleshooting

### Error: "No video assets found"
- Check if video files exist in the expected directories
- Verify file naming convention (e.g., `pk-hfad-1_word.mp4`)
- Use `slt.Assets.get_ids("videos/*.mp4")` to list available videos

### Error: "Assets directory not found"
- Set custom assets directory using `slt.Assets.set_root_dir()`
- Create symbolic links to your video folders
- Check file permissions

### Error: "No matching sign for word"
- Verify the word exists in your vocabulary
- Check the sign language mapping files
- Use `model.get_available_glosses()` to see available words

## 📝 CLI Usage

You can also use the command-line interface:

```bash
# PSL Text-to-Sign
slt psl-text-to-sign "hello world" --text-language urdu --sign-format video

# WLASL Text-to-Sign  
slt wlasl-text-to-sign "hello world" --sign-format landmarks --assets-path /path/to/assets
```

## 🔄 Updating Assets

To update or reload assets:

```python
import sign_language_translator as slt

# Reload URL configurations
slt.Assets.reload()

# Load all URL files
slt.Assets.load_all_urls()

# Delete outdated assets
slt.Assets.delete_out_of_date_assets()
```

This setup ensures your concatenative synthesis system can access all necessary video assets for generating sign language translations. 