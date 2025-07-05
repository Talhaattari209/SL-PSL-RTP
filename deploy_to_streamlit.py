#!/usr/bin/env python3
"""
Deployment script for Streamlit Cloud
This script ensures the correct minimal files are used for deployment.
"""

import os
import shutil
from pathlib import Path

def setup_deployment():
    """Setup files for Streamlit Cloud deployment"""
    
    print("🚀 Setting up Streamlit Cloud deployment...")
    
    # 1. Ensure app.py is the minimal version
    if not Path("app.py").exists():
        print("❌ app.py not found!")
        return False
    
    # 2. Create minimal requirements.txt
    with open("requirements.txt", "w") as f:
        f.write("streamlit>=1.28.0\n")
    print("✅ Created minimal requirements.txt")
    
    # 3. Remove packages.txt if it exists
    if Path("packages.txt").exists():
        os.rename("packages.txt", "packages_backup.txt")
        print("✅ Moved packages.txt to packages_backup.txt")
    
    # 4. Ensure .streamlit directory exists
    streamlit_dir = Path(".streamlit")
    streamlit_dir.mkdir(exist_ok=True)
    
    # 5. Create minimal config.toml
    config_content = """[global]
developmentMode = false

[server]
headless = true
enableCORS = false
enableXsrfProtection = false
port = 8501

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[client]
showErrorDetails = false
"""
    
    with open(streamlit_dir / "config.toml", "w") as f:
        f.write(config_content)
    print("✅ Created .streamlit/config.toml")
    
    # 6. Create .gitignore for deployment
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Streamlit
.streamlit/secrets.toml

# Assets (will be created at runtime)
assets/
temp_files/

# Backup files
*_backup.*
*_old.*
"""
    
    with open(".gitignore", "w") as f:
        f.write(gitignore_content)
    print("✅ Created .gitignore")
    
    print("\n✅ Deployment setup complete!")
    print("\n📋 Next steps:")
    print("1. Commit and push your changes:")
    print("   git add .")
    print("   git commit -m 'Setup minimal Streamlit deployment'")
    print("   git push origin main")
    print("\n2. In Streamlit Cloud:")
    print("   - Set main file path to: app.py")
    print("   - Set Python version to: 3.9")
    print("   - Deploy")
    
    return True

if __name__ == "__main__":
    setup_deployment() 