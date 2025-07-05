# Streamlit Deployment Guide

## 🚨 Current Issue
Your Streamlit deployment is failing due to MediaPipe compatibility issues and Python version constraints. Here's how to fix it:

## 🔧 Quick Fix Steps

### 1. Use the Minimal App
Replace your current `app.py` with the minimal version:

```bash
# Rename your current app.py to app_backup.py
mv app.py app_backup.py

# Use the minimal version
cp app_minimal.py app.py
```

### 2. Use Minimal Requirements
Replace your `requirements.txt` with the minimal version:

```bash
# Backup current requirements
mv requirements.txt requirements_backup.txt

# Use minimal requirements
cp requirements_minimal.txt requirements.txt
```

### 3. Remove packages.txt (Temporarily)
The `packages.txt` file might be causing issues. Remove it temporarily:

```bash
mv packages.txt packages_backup.txt
```

### 4. Deploy to Streamlit Cloud

1. **Push your changes to GitHub:**
   ```bash
   git add .
   git commit -m "Fix MediaPipe compatibility issues"
   git push origin main
   ```

2. **In Streamlit Cloud:**
   - Go to your app settings
   - Set the main file path to: `app.py`
   - Set Python version to: `3.9`
   - Deploy

## 📁 File Structure for Deployment

```
your-repo/
├── app.py                    # Main Streamlit app (minimal)
├── requirements.txt          # Minimal Python dependencies
├── .streamlit/
│   └── config.toml         # Streamlit configuration
├── assets/                 # Will be created automatically
└── README.md
```

## 🔍 Specific Issues and Solutions

### Issue: "Could not find a version that satisfies the requirement mediapipe>=0.10.0"
**Cause:** MediaPipe has strict Python version requirements and is not available for all Python versions
**Solution:** 
- Remove MediaPipe from requirements
- Use only basic Python libraries
- Add MediaPipe back later once basic deployment works

### Issue: "Python version constraints"
**Cause:** Some packages require specific Python versions
**Solution:**
- Use Python 3.9 in Streamlit Cloud
- Use compatible package versions
- Avoid packages with strict version constraints

### Issue: "installer returned a non-zero exit code"
**Cause:** Dependency conflicts during installation
**Solution:**
- Start with minimal dependencies
- Add packages gradually
- Test each addition

## 🚀 Deployment Checklist

- [ ] Use `app_minimal.py` as your main app
- [ ] Use `requirements_minimal.txt` as requirements
- [ ] Remove `packages.txt` temporarily
- [ ] `.streamlit/config.toml` is present
- [ ] Python version set to 3.9
- [ ] Main file path set to `app.py`

## 🔄 Gradual Feature Addition

Once the minimal app is deployed successfully:

1. **Phase 1:** Basic UI (current minimal version) ✅
2. **Phase 2:** Add basic dependencies (numpy, pillow)
3. **Phase 3:** Add video processing (opencv-python)
4. **Phase 4:** Add ML libraries (torch, mediapipe)
5. **Phase 5:** Add your custom models

## 📊 Testing Each Phase

After each phase:
1. Deploy and test
2. Check logs for errors
3. Only proceed if successful
4. Keep backups of working versions

## 🆘 Troubleshooting

### If deployment still fails:

1. **Check Streamlit Cloud logs** for specific error messages
2. **Use even more minimal requirements:**
   ```txt
   streamlit>=1.28.0
   ```
3. **Test locally** with `streamlit run app.py`
4. **Remove all optional dependencies**

### Local Testing:
```bash
# Install minimal dependencies
pip install -r requirements_minimal.txt

# Run locally
streamlit run app_minimal.py
```

## 📞 Support

If you continue to have issues:
1. Check the Streamlit Cloud logs
2. Share the specific error message
3. Try the minimal version first
4. Gradually add complexity

## 🎯 Next Steps

1. Deploy the minimal version
2. Test all functionality
3. Add features incrementally
4. Monitor performance
5. Optimize as needed

## 🔧 Advanced: Adding Back Complex Features

Once the minimal version works:

### Step 1: Add Basic Dependencies
```txt
streamlit>=1.28.0
numpy>=1.21.0,<1.26.0
pillow>=9.0.0
opencv-python>=4.8.0
```

### Step 2: Add ML Dependencies
```txt
torch>=2.0.0
torchvision>=0.15.0
```

### Step 3: Add MediaPipe (Last)
```txt
mediapipe>=0.10.0
```

Test after each step!

---

**Note:** The minimal version provides a working foundation. You can add your complex ML models and features back once the basic deployment is stable. 