"""Vercel entrypoint for the video automation FastAPI application."""

from video_automation.api import app

__all__ = ["app"]
