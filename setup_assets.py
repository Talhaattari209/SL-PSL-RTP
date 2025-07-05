#!/usr/bin/env python3
"""
Setup script for configuring assets for the sign language translator.
This script helps you set up the assets directory for concatenative synthesis.
"""

import os
import sys
from pathlib import Path

def setup_assets():
    """Setup assets directory for the sign language translator."""
    
    print("🔧 Setting up assets for Sign Language Translator")
    print("=" * 50)
    
    # Get the current directory
    current_dir = Path(__file__).parent
    print(f"Current directory: {current_dir}")
    
    # Option 1: Set custom assets directory
    print("\n📁 Option 1: Set Custom Assets Directory")
    print("If your video assets are stored elsewhere, you can set a custom path.")
    
    custom_path = input("Enter custom assets path (or press Enter to skip): ").strip()
    
    if custom_path:
        custom_path = Path(custom_path).resolve()
        if custom_path.exists():
            print(f"✅ Assets directory found: {custom_path}")
            
            # Set the assets directory
            import sign_language_translator as slt
            slt.Assets.set_root_dir(str(custom_path))
            print(f"✅ Assets directory set to: {custom_path}")
        else:
            print(f"❌ Directory not found: {custom_path}")
    
    # Option 2: Create symbolic links
    print("\n🔗 Option 2: Create Symbolic Links")
    print("Create symbolic links to your video folders.")
    
    # Check if video folders exist locally
    psl_videos = current_dir / "sign_language_translator" / "assets" / "video1" / "videos"
    wlasl_videos = current_dir / "sign_language_translator" / "assets_WLASL" / "Common_WLASL_videos"
    wlasl_landmarks = current_dir / "sign_language_translator" / "assets_WLASL" / "Augmented_LandMarks" / "Processed_Landmarks_WLASL"
    
    print(f"PSL videos path: {psl_videos}")
    print(f"WLASL videos path: {wlasl_videos}")
    print(f"WLASL landmarks path: {wlasl_landmarks}")
    
    if not psl_videos.exists():
        psl_source = input("Enter path to PSL videos folder: ").strip()
        if psl_source and Path(psl_source).exists():
            try:
                if os.name == 'nt':  # Windows
                    import subprocess
                    subprocess.run(['mklink', '/D', str(psl_videos), psl_source], shell=True)
                else:  # Unix/Linux/Mac
                    psl_videos.parent.mkdir(parents=True, exist_ok=True)
                    os.symlink(psl_source, psl_videos)
                print(f"✅ Symbolic link created for PSL videos")
            except Exception as e:
                print(f"❌ Error creating symbolic link: {e}")
    
    if not wlasl_videos.exists():
        wlasl_source = input("Enter path to WLASL videos folder: ").strip()
        if wlasl_source and Path(wlasl_source).exists():
            try:
                if os.name == 'nt':  # Windows
                    import subprocess
                    subprocess.run(['mklink', '/D', str(wlasl_videos), wlasl_source], shell=True)
                else:  # Unix/Linux/Mac
                    wlasl_videos.parent.mkdir(parents=True, exist_ok=True)
                    os.symlink(wlasl_source, wlasl_videos)
                print(f"✅ Symbolic link created for WLASL videos")
            except Exception as e:
                print(f"❌ Error creating symbolic link: {e}")
    
    if not wlasl_landmarks.exists():
        wlasl_landmarks_source = input("Enter path to WLASL landmarks folder: ").strip()
        if wlasl_landmarks_source and Path(wlasl_landmarks_source).exists():
            try:
                if os.name == 'nt':  # Windows
                    import subprocess
                    subprocess.run(['mklink', '/D', str(wlasl_landmarks), wlasl_landmarks_source], shell=True)
                else:  # Unix/Linux/Mac
                    wlasl_landmarks.parent.mkdir(parents=True, exist_ok=True)
                    os.symlink(wlasl_landmarks_source, wlasl_landmarks)
                print(f"✅ Symbolic link created for WLASL landmarks")
            except Exception as e:
                print(f"❌ Error creating symbolic link: {e}")
    
    # Option 3: Download assets
    print("\n⬇️  Option 3: Download Assets")
    print("Download assets from the configured URLs.")
    
    download_choice = input("Download assets? (y/n): ").strip().lower()
    if download_choice == 'y':
        try:
            import sign_language_translator as slt
            
            # Download PSL videos
            print("Downloading PSL videos...")
            psl_videos = slt.Assets.download("videos/pk-.*mp4")
            print(f"✅ Downloaded {len(psl_videos)} PSL videos")
            
            # Download WLASL videos (if URLs are configured)
            print("Downloading WLASL videos...")
            wlasl_videos = slt.Assets.download("videos/wlasl-.*mp4")
            print(f"✅ Downloaded {len(wlasl_videos)} WLASL videos")
            
        except Exception as e:
            print(f"❌ Error downloading assets: {e}")
    
    print("\n✅ Asset setup complete!")
    print("\n📝 Usage Examples:")
    print("1. PSL Text-to-Sign:")
    print("   from sign_language_translator.models import ConcatenativeSynthesis")
    print("   model = ConcatenativeSynthesis(text_language='urdu', sign_language='pakistan-sign-language', sign_format='video')")
    print("   result = model.translate('hello')")
    print()
    print("2. WLASL Text-to-Sign:")
    print("   from sign_language_translator.models import WLASLConcatenativeSynthesis")
    print("   model = WLASLConcatenativeSynthesis(text_language='english', sign_format='landmarks')")
    print("   result = model.translate('hello')")

if __name__ == "__main__":
    setup_assets() 