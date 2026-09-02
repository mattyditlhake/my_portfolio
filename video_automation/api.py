#!/usr/bin/env python3
"""
=== NEW FILE: FastAPI Web UI for Video Poster ===
This file provides a web-based interface to upload videos and captions to multiple social media platforms.
Integrates with existing uploaders (Facebook, YouTube, TikTok) via REST API endpoints.
Run with: uvicorn api:app --reload
Access at: http://localhost:8000
"""

import os
import logging
import shutil
from pathlib import Path
from typing import Optional
from datetime import datetime

# === FastAPI imports for web framework ===
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

# === Import existing uploaders from the project ===
from video_automation.uploaders.facebook_uploader import FacebookUploader
from video_automation.uploaders.youtube_uploader import YouTubeUploader
from video_automation.uploaders.tiktok_uploader import TikTokUploader
#from video_automation.uploaders.facebook_uploader import FacebookUploader
#from video_automation.uploaders.youtube_uploader import YouTubeUploader
#from video_automation.uploaders.tiktok_uploader import TikTokUploader


# === Load environment variables ===
load_dotenv()

# === Configure logging ===
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# === Initialize FastAPI app ===
app = FastAPI(title="Video Poster UI", version="1.0.0")

# === Configuration: Map platform names to uploader classes ===
UPLOADERS = {
    'facebook': FacebookUploader,
    'youtube': YouTubeUploader,
    'tiktok': TikTokUploader,
}

# === Create temporary upload directory if it doesn't exist ===
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "temp_uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
logger.info(f"Upload directory: {UPLOAD_DIR.absolute()}")


# === HTML Template for the Web UI ===
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Video Poster - Multi-Platform Upload</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            padding: 40px;
        }
        
        h1 {
            color: #333;
            margin-bottom: 10px;
            text-align: center;
        }
        
        .subtitle {
            color: #666;
            text-align: center;
            margin-bottom: 30px;
            font-size: 14px;
        }
        
        /* === Platform Selection Section === */
        .section {
            margin-bottom: 30px;
        }
        
        .section-title {
            font-size: 18px;
            font-weight: 600;
            color: #333;
            margin-bottom: 15px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        
        .platform-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        /* === Platform Selection Buttons === */
        .platform-btn {
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 8px;
            background: white;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s ease;
            color: #333;
        }
        
        .platform-btn:hover {
            border-color: #667eea;
            background: #f0f4ff;
            transform: translateY(-2px);
        }
        
        .platform-btn.active {
            background: #667eea;
            color: white;
            border-color: #667eea;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        /* === Form Elements === */
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        
        input[type="text"],
        input[type="file"],
        textarea {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
            font-family: inherit;
            transition: border-color 0.3s ease;
        }
        
        input[type="text"]:focus,
        input[type="file"]:focus,
        textarea:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        textarea {
            resize: vertical;
            min-height: 100px;
        }
        
        /* === File Upload Display === */
        .file-inputs {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
        
        @media (max-width: 600px) {
            .file-inputs {
                grid-template-columns: 1fr;
            }
        }
        
        .file-input-group {
            display: flex;
            flex-direction: column;
        }
        
        .file-name {
            font-size: 12px;
            color: #666;
            margin-top: 5px;
            padding: 8px;
            background: #f5f5f5;
            border-radius: 4px;
            min-height: 20px;
        }
        
        /* === Buttons === */
        .button-group {
            display: flex;
            gap: 10px;
            justify-content: center;
            margin-top: 30px;
        }
        
        button {
            padding: 12px 30px;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn-submit {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 14px 40px;
            flex: 1;
            max-width: 300px;
        }
        
        .btn-submit:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        .btn-submit:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .btn-reset {
            background: #ddd;
            color: #333;
        }
        
        .btn-reset:hover {
            background: #ccc;
        }
        
        /* === Status Messages === */
        .status {
            padding: 15px;
            border-radius: 6px;
            margin-top: 20px;
            display: none;
        }
        
        .status.show {
            display: block;
        }
        
        .status.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .status.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .status.info {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        
        .status.loading {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .spinner {
            border: 3px solid rgba(0,0,0,0.1);
            border-radius: 50%;
            border-top: 3px solid #667eea;
            width: 20px;
            height: 20px;
            animation: spin 0.8s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* === Platform-specific styling === */
        .platform-info {
            background: #f9f9f9;
            padding: 15px;
            border-left: 4px solid #667eea;
            border-radius: 4px;
            margin-bottom: 20px;
            font-size: 14px;
            color: #666;
        }
        
        .required {
            color: #e74c3c;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- === Header Section === -->
        <h1>🎬 Video Poster</h1>
        <p class="subtitle">Upload videos to multiple social media platforms</p>
        
        <!-- === Main Form === -->
        <form id="uploadForm" enctype="multipart/form-data">
            <!-- === Step 1: Select Platform === -->
            <div class="section">
                <div class="section-title">Step 1: Select Platform</div>
                <div class="platform-grid">
                    <button type="button" class="platform-btn" id="selectAllPlatforms">
                        All Platforms
                    </button>
                    <button type="button" class="platform-btn" data-platform="facebook">
                        📘 Facebook
                    </button>
                    <button type="button" class="platform-btn" data-platform="youtube">
                        🎥 YouTube
                    </button>
                    <button type="button" class="platform-btn" data-platform="tiktok">
                        🎵 TikTok
                    </button>
                </div>
                
                <div class="platform-info" style="display: block;">
                    Select one or more platforms. If you select all platforms, fill in the credentials for every selected platform.
                </div>

                <!-- === Platform Information Display === -->
                <div id="platformInfo" class="platform-info" style="display: none;"></div>
            </div>
            
            <!-- === Step 2: API Credentials === -->
            <div class="section">
                <div class="section-title">Step 2: API Credentials</div>
                
                <!-- === Facebook Credentials === -->
                <div id="facebook-creds" class="platform-creds" style="display: none;">
                    <div class="form-group">
                        <label>Facebook Page ID <span class="required">*</span></label>
                        <input type="text" name="facebook_page_id" placeholder="Enter your Facebook Page ID">
                    </div>
                    <div class="form-group">
                        <label>Facebook Page Access Token <span class="required">*</span></label>
                        <input type="text" name="facebook_access_token" placeholder="Enter your Facebook Page Access Token">
                    </div>
                </div>
                
                <!-- === YouTube Credentials === -->
                <div id="youtube-creds" class="platform-creds" style="display: none;">
                    <div class="form-group">
                        <label>Upload client_secrets.json <span class="required">*</span></label>
                        <input type="file" name="youtube_credentials" accept=".json">
                        <div class="file-name" id="youtube-creds-file">No file selected</div>
                    </div>
                </div>
                
                <!-- === TikTok Credentials === -->
                <div id="tiktok-creds" class="platform-creds" style="display: none;">
                    <div class="form-group">
                        <label>TikTok Access Token <span class="required">*</span></label>
                        <input type="text" name="tiktok_access_token" placeholder="Enter your TikTok Access Token">
                    </div>
                </div>
            </div>
            
            <!-- === Step 3: Upload Files === -->
            <div class="section">
                <div class="section-title">Step 3: Upload Content</div>
                
                <!-- === Video File Input === -->
                <div class="form-group">
                    <label>Video File (.mp4, .mov, .avi) <span class="required">*</span></label>
                    <input type="file" name="video_file" accept="video/*" required>
                    <div class="file-name" id="video-file">No file selected</div>
                </div>
                
                <!-- === Caption Input === -->
                <div class="form-group">
                    <label>Caption/Description <span class="required">*</span></label>
                    <textarea name="caption" placeholder="Enter caption or description for your video" required></textarea>
                </div>
                
                <!-- === Optional: Title and Additional Files === -->
                <div class="form-group">
                    <label>Video Title (Optional, defaults to filename)</label>
                    <input type="text" name="title" placeholder="Enter video title">
                </div>
                
                <div class="form-group">
                    <label>Additional Files (images, jpg, png, etc) <span class="required">Optional</span></label>
                    <input type="file" name="additional_files" multiple accept="image/*">
                    <div class="file-name" id="additional-files">No files selected</div>
                </div>
            </div>
            
            <!-- === Step 4: Submit === -->
            <div class="button-group">
                <button type="button" class="btn-reset" onclick="resetForm()">Clear Form</button>
                <button type="submit" class="btn-submit" id="submitBtn">Upload to Selected Platform(s)</button>
            </div>
        </form>
        
        <!-- === Status Display Area === -->
        <div id="statusMessage" class="status"></div>
    </div>
    
    <!-- === JavaScript Logic === -->
    <script>
        // === Global state to track selected platforms ===
        let selectedPlatforms = new Set();
        
        // === Platform button event listeners ===
        document.querySelectorAll('.platform-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                if (this.id === 'selectAllPlatforms') {
                    selectedPlatforms = new Set(['facebook', 'youtube', 'tiktok']);
                    document.querySelectorAll('.platform-btn[data-platform]').forEach(button => {
                        button.classList.add('active');
                        document.getElementById(`${button.dataset.platform}-creds`).style.display = 'block';
                    });
                    this.classList.add('active');
                    updatePlatformInfo();
                    return;
                }

                const platform = this.dataset.platform;
                if (selectedPlatforms.has(platform)) {
                    selectedPlatforms.delete(platform);
                    this.classList.remove('active');
                    document.getElementById(`${platform}-creds`).style.display = 'none';
                    document.getElementById('selectAllPlatforms').classList.remove('active');
                } else {
                    selectedPlatforms.add(platform);
                    this.classList.add('active');
                    document.getElementById(`${platform}-creds`).style.display = 'block';
                    if (selectedPlatforms.size === 3) {
                        document.getElementById('selectAllPlatforms').classList.add('active');
                    }
                }

                // Update platform info
                updatePlatformInfo();
            });
        });
        
        // === Update platform information display ===
        function updatePlatformInfo() {
            const infoDiv = document.getElementById('platformInfo');
            const messages = {
                facebook: 'Get your credentials from <a href="https://developers.facebook.com/" target="_blank">Facebook Developers</a>',
                youtube: 'Download your client_secrets.json from <a href="https://console.cloud.google.com/" target="_blank">Google Cloud Console</a>',
                tiktok: 'Get your access token from <a href="https://developer.tiktok.com/" target="_blank">TikTok Developer Platform</a>'
            };
            const selected = Array.from(selectedPlatforms);
            infoDiv.innerHTML = selected.map(platform => messages[platform]).join('<br>');
            infoDiv.style.display = selected.length ? 'block' : 'none';
        }
        
        // === File input change listeners to display file names ===
        document.querySelector('input[name="video_file"]').addEventListener('change', function() {
            document.getElementById('video-file').textContent = this.files[0]?.name || 'No file selected';
        });
        
        document.querySelector('input[name="youtube_credentials"]').addEventListener('change', function() {
            document.getElementById('youtube-creds-file').textContent = this.files[0]?.name || 'No file selected';
        });
        
        document.querySelector('input[name="additional_files"]').addEventListener('change', function() {
            const count = this.files.length;
            document.getElementById('additional-files').textContent = 
                count > 0 ? `${count} file(s) selected` : 'No files selected';
        });
        
        // === Show status message ===
        function showStatus(message, type) {
            const statusDiv = document.getElementById('statusMessage');
            statusDiv.className = `status show ${type}`;
            statusDiv.textContent = message;
        }
        
        function showStatusWithSpinner(message) {
            const statusDiv = document.getElementById('statusMessage');
            statusDiv.className = 'status show loading';
            statusDiv.innerHTML = `<div class="spinner"></div> <span>${message}</span>`;
        }
        
        // === Form submission handler ===
        document.getElementById('uploadForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // === Validation ===
            if (selectedPlatforms.size === 0) {
                showStatus('Please select at least one platform', 'error');
                return;
            }
            
            const formData = new FormData(this);
            
            // === Add selected platforms to form data ===
            formData.append('platforms', Array.from(selectedPlatforms).join(','));
            
            try {
                showStatusWithSpinner('Uploading to ' + Array.from(selectedPlatforms).join(', ') + '...');
                
                // === Send form data to backend endpoint ===
                const response = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    const details = result.results
                        ? Object.entries(result.results).map(([platform, item]) => `${platform}: ${item.success ? 'success' : 'failed'}`).join(' | ')
                        : result.message;
                    showStatus('Upload complete. ' + details, result.status === 'success' ? 'success' : 'error');
                    // === Clear form after successful upload ===
                    document.getElementById('uploadForm').reset();
                    document.querySelectorAll('.platform-btn').forEach(b => b.classList.remove('active'));
                    document.querySelectorAll('.platform-creds').forEach(c => c.style.display = 'none');
                    document.getElementById('platformInfo').style.display = 'none';
                    selectedPlatforms.clear();
                } else {
                    showStatus('❌ Error: ' + (result.detail || 'Upload failed'), 'error');
                }
            } catch (error) {
                showStatus('❌ Network error: ' + error.message, 'error');
            }
        });
        
        // === Reset form function ===
        function resetForm() {
            document.getElementById('uploadForm').reset();
            document.querySelectorAll('.platform-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.platform-creds').forEach(c => c.style.display = 'none');
            document.getElementById('platformInfo').style.display = 'none';
            document.getElementById('statusMessage').className = 'status';
            document.getElementById('video-file').textContent = 'No file selected';
            document.getElementById('youtube-creds-file').textContent = 'No file selected';
            document.getElementById('additional-files').textContent = 'No files selected';
            selectedPlatforms.clear();
        }
    </script>
</body>
</html>
"""


# === REST API ENDPOINTS ===

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    """
    === NEW ENDPOINT: Serve the main HTML UI ===
    GET / - Returns the HTML interface for the web UI
    """
    return HTML_TEMPLATE


@app.post("/api/upload")
async def upload_and_post(
    platform: Optional[str] = Form(None),
    platforms: Optional[str] = Form(None),
    video_file: UploadFile = File(...),
    caption: str = Form(...),
    title: Optional[str] = Form(None),
    facebook_page_id: Optional[str] = Form(None),
    facebook_access_token: Optional[str] = Form(None),
    youtube_credentials: Optional[UploadFile] = File(None),
    tiktok_access_token: Optional[str] = Form(None),
    additional_files: Optional[list] = File(None),
):
    """
    === NEW ENDPOINT: Main upload endpoint ===
    POST /api/upload - Handles file uploads and posts to selected platform
    
    Validates credentials, saves temporary files, and calls appropriate uploader.
    Cleans up temporary files after upload completes.
    """
    
    try:
        # === Validate platform selection ===
        selected_platforms = [
            item.strip().lower()
            for item in (platforms or platform or "").split(",")
            if item.strip()
        ]
        if not selected_platforms:
            raise HTTPException(status_code=400, detail="Select at least one platform")

        invalid_platforms = [item for item in selected_platforms if item not in UPLOADERS]
        if invalid_platforms:
            raise HTTPException(status_code=400, detail=f"Invalid platform(s): {', '.join(invalid_platforms)}")

        logger.info(f"[NEW] Upload request for platforms: {', '.join(selected_platforms)}")

        # === Create session-specific upload directory ===
        session_dir = UPLOAD_DIR / f"multi_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        session_dir.mkdir(exist_ok=True)
        
        try:
            # === Save uploaded video file ===
            video_path = session_dir / video_file.filename
            with open(video_path, "wb") as f:
                content = await video_file.read()
                f.write(content)
            logger.info(f"[NEW] Video file saved: {video_path}")
            
            youtube_creds_path = None
            if 'youtube' in selected_platforms:
                if not youtube_credentials:
                    raise HTTPException(status_code=400, detail="YouTube credentials file (client_secrets.json) is required")

                youtube_creds_path = session_dir / "client_secrets.json"
                with open(youtube_creds_path, "wb") as f:
                    content = await youtube_credentials.read()
                    f.write(content)
                logger.info(f"[NEW] YouTube credentials saved: {youtube_creds_path}")

            results = {}
            for selected_platform in selected_platforms:
                try:
                    uploader_cls = UPLOADERS[selected_platform]

                    if selected_platform == 'facebook':
                        if not facebook_page_id or not facebook_access_token:
                            raise ValueError("Facebook Page ID and Access Token are required")
                        uploader = uploader_cls(page_id=facebook_page_id, access_token=facebook_access_token)
                        logger.info(f"[NEW] Facebook uploader initialized with Page ID: {facebook_page_id}")
                    elif selected_platform == 'youtube':
                        uploader = uploader_cls(credentials_file=str(youtube_creds_path))
                        logger.info("[NEW] YouTube uploader initialized")
                    elif selected_platform == 'tiktok':
                        if not tiktok_access_token:
                            raise ValueError("TikTok Access Token is required")
                        uploader = uploader_cls(access_token=tiktok_access_token)
                        logger.info("[NEW] TikTok uploader initialized")
                    else:
                        raise ValueError(f"Invalid platform: {selected_platform}")

                    # === Call upload method from the existing uploader ===
                    logger.info(f"[NEW] Starting upload to {selected_platform}...")
                    success, meta = uploader.upload(
                        video_path=str(video_path),
                        caption=caption,
                        title=title or video_file.filename
                    )

                    results[selected_platform] = {
                        "success": bool(success),
                        "metadata": str(meta)[:500],
                    }

                    if not success:
                        logger.error(f"[NEW] Upload failed for {selected_platform}: {meta}")
                    else:
                        logger.info(f"[NEW] Upload successful to {selected_platform}. Metadata: {meta}")
                except Exception as exc:
                    logger.exception(f"[NEW] Upload failed for {selected_platform}")
                    results[selected_platform] = {
                        "success": False,
                        "error": str(exc),
                    }

            all_success = all(item["success"] for item in results.values())

            # === Return per-platform response ===
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success" if all_success else "partial_failure",
                    "platforms": selected_platforms,
                    "message": "Upload process complete",
                    "results": results,
                }
            )
        
        finally:
            # === Clean up temporary session directory ===
            logger.info(f"[NEW] Cleaning up temporary files in: {session_dir}")
            shutil.rmtree(session_dir, ignore_errors=True)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[NEW] Unexpected error during upload: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


# === Health check endpoint ===
@app.get("/api/health")
async def health_check():
    """
    === NEW ENDPOINT: Health check ===
    GET /api/health - Simple endpoint to verify the API is running
    """
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "available_platforms": list(UPLOADERS.keys())
        }
    )


# === Error handler for detailed error information ===
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    === NEW: Global error handler ===
    Catches all unhandled exceptions and returns formatted JSON response
    """
    logger.error(f"[NEW] Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred"}
    )


if __name__ == "__main__":
    import uvicorn
    
    logger.info("=" * 60)
    logger.info("[NEW] Starting FastAPI Video Poster UI Server")
    logger.info("=" * 60)
    logger.info("Access the UI at: http://localhost:8000")
    logger.info("API documentation at: http://localhost:8000/docs")
    logger.info("=" * 60)
    
    # === Run FastAPI server ===
    uvicorn.run(app, host="0.0.0.0", port=8000)
