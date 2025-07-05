#!/usr/bin/env python3
"""
Assets Manager for Vercel Deployment
Handles cloud storage, local caching, and fallback options for sign language assets.
"""

import os
import json
import tempfile
import requests
from pathlib import Path
from typing import Dict, Optional, List
import hashlib
import time

class VercelAssetsManager:
    """Manages assets for Vercel deployment with cloud storage support."""
    
    def __init__(self, config_path: str = "assets_config.json"):
        """
        Initialize the assets manager.
        
        Args:
            config_path: Path to configuration file with asset URLs
        """
        self.config_path = config_path
        self.cache_dir = Path(tempfile.gettempdir()) / "slt_assets_cache"
        self.cache_dir.mkdir(exist_ok=True)
        
        # Load configuration
        self.config = self._load_config()
        
        # Asset type mappings
        self.asset_types = {
            "psl_videos": "videos/pk-*.mp4",
            "wlasl_videos": "videos/wlasl-*.mp4", 
            "wlasl_landmarks": "landmarks/*.pkl"
        }
    
    def _load_config(self) -> Dict:
        """Load assets configuration from file."""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
        else:
            # Default configuration
            return {
                "storage_type": "local",  # local, cloud, hybrid
                "cloud_provider": "github",  # github, gdrive, s3, cdn
                "base_urls": {
                    "psl_videos": "",
                    "wlasl_videos": "",
                    "wlasl_landmarks": ""
                },
                "github_release": {
                    "repo": "Talhaattari209/SL-PSL-RTP",
                    "tag": "assets-v1.0"
                },
                "cache_duration": 3600,  # 1 hour
                "max_cache_size": 1024 * 1024 * 1024  # 1GB
            }
    
    def _save_config(self):
        """Save current configuration to file."""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def setup_cloud_storage(self, storage_type: str, **kwargs):
        """
        Setup cloud storage configuration.
        
        Args:
            storage_type: Type of storage (github, gdrive, s3, cdn)
            **kwargs: Storage-specific configuration
        """
        self.config["storage_type"] = "cloud"
        self.config["cloud_provider"] = storage_type
        
        if storage_type == "github":
            self.config["github_release"].update(kwargs)
        elif storage_type == "gdrive":
            self.config["base_urls"].update(kwargs)
        elif storage_type == "s3":
            self.config["s3_config"] = kwargs
        elif storage_type == "cdn":
            self.config["base_urls"].update(kwargs)
        
        self._save_config()
    
    def get_asset_url(self, asset_type: str, filename: str) -> str:
        """Get the URL for a specific asset."""
        provider = self.config["cloud_provider"]
        
        if provider == "github":
            repo = self.config["github_release"]["repo"]
            tag = self.config["github_release"]["tag"]
            return f"https://github.com/{repo}/releases/download/{tag}/{filename}"
        
        elif provider == "gdrive":
            base_url = self.config["base_urls"].get(asset_type, "")
            return f"{base_url}/{filename}"
        
        elif provider == "cdn":
            base_url = self.config["base_urls"].get(asset_type, "")
            return f"{base_url}/{filename}"
        
        else:
            raise ValueError(f"Unsupported cloud provider: {provider}")
    
    def download_asset(self, asset_type: str, filename: str, force_download: bool = False) -> str:
        """
        Download an asset from cloud storage with caching.
        
        Args:
            asset_type: Type of asset (psl_videos, wlasl_videos, wlasl_landmarks)
            filename: Name of the file to download
            force_download: Force download even if cached
            
        Returns:
            Path to the downloaded file
        """
        # Check cache first
        cache_key = hashlib.md5(f"{asset_type}_{filename}".encode()).hexdigest()
        cache_file = self.cache_dir / f"{cache_key}_{filename}"
        
        if not force_download and cache_file.exists():
            # Check if cache is still valid
            if time.time() - cache_file.stat().st_mtime < self.config["cache_duration"]:
                return str(cache_file)
        
        # Download from cloud
        url = self.get_asset_url(asset_type, filename)
        
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Save to cache
            with open(cache_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return str(cache_file)
            
        except Exception as e:
            print(f"Error downloading {filename}: {e}")
            return None
    
    def get_asset_path(self, asset_type: str, filename: str) -> Optional[str]:
        """
        Get the path to an asset, downloading if necessary.
        
        Args:
            asset_type: Type of asset
            filename: Name of the file
            
        Returns:
            Path to the asset file or None if not found
        """
        if self.config["storage_type"] == "local":
            # Local file system
            local_paths = {
                "psl_videos": "sign_language_translator/assets/video1/videos",
                "wlasl_videos": "sign_language_translator/assets_WLASL/Common_WLASL_videos",
                "wlasl_landmarks": "sign_language_translator/assets_WLASL/Augmented_LandMarks/Processed_Landmarks_WLASL"
            }
            
            base_path = Path(local_paths.get(asset_type, ""))
            full_path = base_path / filename
            
            if full_path.exists():
                return str(full_path)
            else:
                print(f"Local asset not found: {full_path}")
                return None
        
        elif self.config["storage_type"] == "cloud":
            # Cloud storage
            return self.download_asset(asset_type, filename)
        
        else:
            raise ValueError(f"Unsupported storage type: {self.config['storage_type']}")
    
    def list_available_assets(self, asset_type: str) -> List[str]:
        """List available assets for a given type."""
        if self.config["storage_type"] == "local":
            local_paths = {
                "psl_videos": "sign_language_translator/assets/video1/videos",
                "wlasl_videos": "sign_language_translator/assets_WLASL/Common_WLASL_videos",
                "wlasl_landmarks": "sign_language_translator/assets_WLASL/Augmented_LandMarks/Processed_Landmarks_WLASL"
            }
            
            base_path = Path(local_paths.get(asset_type, ""))
            if base_path.exists():
                return [f.name for f in base_path.iterdir() if f.is_file()]
            return []
        
        elif self.config["storage_type"] == "cloud":
            # For cloud storage, you might need to maintain a manifest file
            manifest_url = self.get_asset_url(asset_type, "manifest.json")
            try:
                response = requests.get(manifest_url)
                manifest = response.json()
                return manifest.get(asset_type, [])
            except:
                return []
        
        return []
    
    def clear_cache(self):
        """Clear the asset cache."""
        import shutil
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        print("Cache cleared successfully")
    
    def get_cache_info(self) -> Dict:
        """Get information about the cache."""
        if not self.cache_dir.exists():
            return {"size": 0, "files": 0}
        
        total_size = 0
        file_count = 0
        
        for file_path in self.cache_dir.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
                file_count += 1
        
        return {
            "size": total_size,
            "files": file_count,
            "cache_dir": str(self.cache_dir)
        }

# Integration with sign_language_translator
def setup_vercel_assets():
    """Setup assets manager for Vercel deployment."""
    manager = VercelAssetsManager()
    
    # Example: Setup GitHub releases
    manager.setup_cloud_storage("github", 
                               repo="Talhaattari209/SL-PSL-RTP",
                               tag="assets-v1.0")
    
    return manager

# Usage example
if __name__ == "__main__":
    # Initialize manager
    manager = VercelAssetsManager()
    
    # Setup cloud storage (choose one)
    print("Setting up cloud storage...")
    
    # Option 1: GitHub Releases
    manager.setup_cloud_storage("github", 
                               repo="Talhaattari209/SL-PSL-RTP",
                               tag="assets-v1.0")
    
    # Option 2: Google Drive
    # manager.setup_cloud_storage("gdrive",
    #                            psl_videos="https://drive.google.com/uc?id=YOUR_ID",
    #                            wlasl_videos="https://drive.google.com/uc?id=YOUR_ID",
    #                            wlasl_landmarks="https://drive.google.com/uc?id=YOUR_ID")
    
    # Option 3: CDN
    # manager.setup_cloud_storage("cdn",
    #                            psl_videos="https://your-cdn.com/psl-videos",
    #                            wlasl_videos="https://your-cdn.com/wlasl-videos",
    #                            wlasl_landmarks="https://your-cdn.com/wlasl-landmarks")
    
    print("✅ Assets manager configured successfully!")
    print(f"Cache directory: {manager.cache_dir}")
    print(f"Configuration saved to: {manager.config_path}") 