# Streamlit Deployment Guide

## 🚨 Current Issue
Your Streamlit deployment is failing due to dependency conflicts and complex imports. Here's how to fix it:

## 🔧 Quick Fix Steps

### 1. Use the Simplified App
Replace your current `app.py` with the simplified version:

```bash
# Rename your current app.py to app_backup.py
mv app.py app_backup.py

# Use the simplified version
cp app_simple.py app.py
```

### 2. Update Requirements
The `requirements.txt` file has been updated with compatible versions. Make sure it's in your repository root.

### 3. Add Configuration Files
The following files have been created:
- `.streamlit/config.toml` - Streamlit configuration
- `packages.txt` - System dependencies

### 4. Deploy to Streamlit Cloud

1. **Push your changes to GitHub:**
   ```bash
   git add .
   git commit -m "Fix Streamlit deployment dependencies"
   git push origin main
   ```

2. **In Streamlit Cloud:**
   - Go to your app settings
   - Set the main file path to: `app.py`
   - Set Python version to: `3.9` or `3.10`
   - Deploy

## 📁 File Structure for Deployment

```
your-repo/
├── app.py                    # Main Streamlit app (simplified)
├── requirements.txt          # Python dependencies
├── packages.txt             # System dependencies
├── .streamlit/
│   └── config.toml         # Streamlit configuration
├── assets/                 # Will be created automatically
└── README.md
```

## 🔍 Common Issues and Solutions

### Issue 1: "installer returned a non-zero exit code"
**Cause:** Dependency conflicts or missing system packages
**Solution:** 
- Use the simplified `requirements.txt`
- Ensure `packages.txt` is present
- Use Python 3.9 or 3.10

### Issue 2: "Module not found"
**Cause:** Complex imports from your custom package
**Solution:**
- Use the simplified app that doesn't import complex modules
- Gradually add functionality back

### Issue 3: "FFMPEG not found"
**Cause:** System dependency missing
**Solution:**
- Ensure `packages.txt` includes `ffmpeg`
- The app will work without FFMPEG (with reduced functionality)

## 🚀 Deployment Checklist

- [ ] Use `app_simple.py` as your main app
- [ ] Updated `requirements.txt` is in root directory
- [ ] `packages.txt` is in root directory
- [ ] `.streamlit/config.toml` is present
- [ ] Python version set to 3.9 or 3.10
- [ ] Main file path set to `app.py`

## 🔄 Gradual Feature Addition

Once the basic app is deployed successfully, you can gradually add features:

1. **Phase 1:** Basic UI (current simplified version)
2. **Phase 2:** Add video upload functionality
3. **Phase 3:** Add basic translation features
4. **Phase 4:** Add complex ML models

## 📊 Monitoring Deployment

After deployment, check:
- App loads without errors
- All pages are accessible
- File upload works
- No dependency errors in logs

## 🆘 Troubleshooting

### If deployment still fails:

1. **Check Streamlit Cloud logs** for specific error messages
2. **Remove problematic dependencies** from `requirements.txt`
3. **Test locally** with `streamlit run app.py`
4. **Use minimal requirements** and add gradually

### Local Testing:
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
streamlit run app.py
```

## 📞 Support

If you continue to have issues:
1. Check the Streamlit Cloud logs
2. Share the specific error message
3. Try the minimal version first
4. Gradually add complexity

## 🎯 Next Steps

1. Deploy the simplified version
2. Test all functionality
3. Add features incrementally
4. Monitor performance
5. Optimize as needed

---

**Note:** The simplified version provides a working foundation. You can add your complex ML models and features back once the basic deployment is stable. 