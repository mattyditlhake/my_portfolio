import os, logging
from .base_uploader import BaseUploader

logger = logging.getLogger(__name__)

class YouTubeUploader(BaseUploader):
    def __init__(self, credentials_file='client_secrets.json'):
        self.credentials_file = credentials_file
        try:
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaFileUpload
        except Exception:
            InstalledAppFlow = None
            build = None
            MediaFileUpload = None
        self._flow = InstalledAppFlow
        self._build = build
        self._MediaFileUpload = MediaFileUpload

    def _get_authenticated_service(self):
        if not os.path.exists(self.credentials_file):
            raise FileNotFoundError('client_secrets.json not found in project root')
        SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
        flow = self._flow.from_client_secrets_file(self.credentials_file, SCOPES)
        creds = flow.run_local_server(port=0)
        youtube = self._build('youtube', 'v3', credentials=creds)
        return youtube

    def upload(self, video_path, caption, title=None, **kwargs):
        if self._build is None:
            return False, {'error': 'google libraries not installed. pip install google-api-python-client google-auth-oauthlib'}
        try:
            youtube = self._get_authenticated_service()
            body = {
                'snippet': {
                    'title': title or os.path.splitext(os.path.basename(video_path))[0],
                    'description': caption,
                },
                'status': {'privacyStatus': 'unlisted'}
            }
            media = self._MediaFileUpload(video_path, chunksize=-1, resumable=True)
            request = youtube.videos().insert(part=','.join(body.keys()), body=body, media_body=media)
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    logger.info('Upload progress: %.2f%%', float(status.progress() * 100))
            return True, response
        except Exception as e:
            logger.exception('YouTube upload failed')
            return False, {'error': str(e)}
