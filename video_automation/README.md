# Video Poster Automation — TikTok, Facebook, YouTube

This project is a starter automation to upload videos to:
- TikTok (scaffold + instructions)
- Facebook (Page video upload implementation)
- YouTube (OAuth + resumable upload implementation)

IMPORTANT:
- TikTok API policies and endpoints change frequently. The included TikTok uploader is a scaffold with instructions and placeholders. You'll need to register for TikTok for Developers (or TikTok For Business) and follow their upload flow.
- For Facebook, you need a Page ID and Page Access Token with `pages_manage_posts` and `pages_read_engagement` permissions.
- For YouTube, you must enable YouTube Data API v3 and place `client_secrets.json` in project root.

Quick start:
1. Create a virtualenv and install requirements:
   ```
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Edit `.env` and add credentials:
   - FACEBOOK_PAGE_ID, FACEBOOK_PAGE_ACCESS_TOKEN
   - TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_ACCESS_TOKEN (if available)
   - Place `client_secrets.json` for YouTube
3. Put videos in `videos/` and captions in `captions/`
4. Example upload:
   ```
   python main.py --platform facebook --video videos/test.mp4 --caption captions/test.txt
   ```

---

## === NEW: Web UI for Video Posting ===

A new FastAPI-based web interface has been added for easier multi-platform uploads!

### Features:
- 🎨 **Beautiful Web Interface** - Intuitive UI for uploading videos
- 📱 **Multi-Platform Support** - Upload to Facebook, YouTube, or TikTok from one place
- 📁 **File Management** - Upload videos, captions, images, and credentials
- 🔐 **Secure Credentials** - Enter platform credentials directly in the UI (not stored on disk)
- ✅ **Real-time Feedback** - Status updates during upload process
- 🗑️ **Auto Cleanup** - Temporary files are automatically cleaned up after upload

### Installation:

1. Install new FastAPI dependencies:
   ```
   pip install -r requirements.txt
   ```
   (Already includes fastapi, uvicorn, python-multipart, aiofiles)

### Usage:

#### Method 1: Using the startup script (Recommended)
```
python start_ui.py
```

#### Method 2: Direct uvicorn command
```
uvicorn api:app --reload
```

### Access the UI:
- **Main Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

### How to Use the Web UI:

1. **Select Platform**
   - Click on Facebook, YouTube, or TikTok button

2. **Enter Credentials**
   - Facebook: Enter Page ID and Page Access Token
   - YouTube: Upload your client_secrets.json file
   - TikTok: Enter your Access Token

3. **Upload Content**
   - Select your video file (.mp4, .mov, .avi, etc.)
   - Enter caption/description text
   - (Optional) Add a custom title
   - (Optional) Upload additional images

4. **Submit**
   - Click "Upload to Selected Platform"
   - Watch for real-time status updates
   - Success message appears when complete

### Files Added:
- `api.py` - Main FastAPI application with all endpoints and HTML UI
- `start_ui.py` - Convenient startup script for the server
- Updated `requirements.txt` - Added FastAPI dependencies

All changes are marked with `=== NEW ===` comments for easy identification.

### API Endpoints:

- `GET /` - Serves the main HTML UI
- `POST /api/upload` - Handles file uploads and posting
- `GET /api/health` - Health check endpoint

### Environment Variables:

You can still use `.env` file for default credentials:
```
FACEBOOK_PAGE_ID=your_page_id
FACEBOOK_PAGE_ACCESS_TOKEN=your_token
TIKTOK_ACCESS_TOKEN=your_token
TIKTOK_CLIENT_KEY=your_key
TIKTOK_CLIENT_SECRET=your_secret
```

### Troubleshooting:

- **"Address already in use"** - Another process is using port 8000. Use a different port:
  ```
  uvicorn api:app --port 8001
  ```
- **Module not found errors** - Make sure you've installed all requirements:
  ```
  pip install -r requirements.txt
  ```
- **Upload fails** - Check the browser console (F12) for error details and ensure credentials are correct

