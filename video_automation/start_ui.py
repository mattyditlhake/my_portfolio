#!/usr/bin/env python3
"""
=== NEW FILE: FastAPI UI Startup Script ===
This script starts the FastAPI web server for the Video Poster UI.
Run with: python start_ui.py
Or from terminal: uvicorn api:app --reload
"""

import subprocess
import sys
import webbrowser
import time
import logging

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def start_server():
    """
    === Start the FastAPI server ===
    Launches uvicorn server with auto-reload for development
    """
    logger.info("=" * 70)
    logger.info("[NEW] Starting Video Poster FastAPI UI Server")
    logger.info("=" * 70)
    logger.info("Server will start at: http://localhost:8000")
    logger.info("API documentation at: http://localhost:8000/docs")
    logger.info("Press Ctrl+C to stop the server")
    logger.info("=" * 70)
    
    try:
        # === Run FastAPI server with uvicorn ===
        subprocess.run(
            [sys.executable, "-m", "uvicorn", "api:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
            check=True
        )
    except KeyboardInterrupt:
        logger.info("\n[NEW] Server shutdown requested")
    except Exception as e:
        logger.error(f"[NEW] Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_server()
