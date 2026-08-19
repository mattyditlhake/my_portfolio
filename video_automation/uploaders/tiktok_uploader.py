import os, logging
from .base_uploader import BaseUploader

logger = logging.getLogger(__name__)

class TikTokUploader(BaseUploader):
    """
    TikTok uploader scaffold.

    TikTok's API for uploads is different depending on whether you use:
     - TikTok for Developers (user auth, content upload)
     - TikTok for Business (marketing API)

    There is no single simple token you can paste like Mastodon or Facebook Page tokens.
    You typically need to register an app, use OAuth to get access tokens, and then follow
    a multi-step upload flow (create video, upload file, finalize).

    This class provides a clear place to implement that flow. For now it will raise
    a helpful error explaining what to do.
    """
    def __init__(self, client_key=None, client_secret=None, access_token=None):
        self.client_key = client_key or os.getenv('TIKTOK_CLIENT_KEY')
        self.client_secret = client_secret or os.getenv('TIKTOK_CLIENT_SECRET')
        self.access_token = access_token or os.getenv('TIKTOK_ACCESS_TOKEN')

    def upload(self, video_path, caption, **kwargs):
        # Example guidance rather than a working uploader, because TikTok's developer
        # API requires app registration and an upload flow. Implement the flow like:
        # 1) POST to create an upload session (get an upload_url or upload_id)
        # 2) PUT or POST the video bytes to that upload_url (often chunked)
        # 3) POST to finalize and publish the video with text/caption
        raise NotImplementedError('TikTok upload is not implemented. See README for steps to implement using TikTok for Developers or TikTok for Business API.')
