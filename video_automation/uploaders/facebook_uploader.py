import os, requests, logging, mimetypes
from .base_uploader import BaseUploader

logger = logging.getLogger(__name__)

class FacebookUploader(BaseUploader):
    """Uploads video to a Facebook Page using Graph API (resumable upload).
    Requires:
      - FACEBOOK_PAGE_ID
      - FACEBOOK_PAGE_ACCESS_TOKEN
    """
    def __init__(self, page_id=None, access_token=None, version='v16.0'):
        self.page_id = page_id or os.getenv('FACEBOOK_PAGE_ID')
        self.token = access_token or os.getenv('FACEBOOK_PAGE_ACCESS_TOKEN')
        self.version = version
        if not self.page_id or not self.token:
            raise ValueError('FACEBOOK_PAGE_ID and FACEBOOK_PAGE_ACCESS_TOKEN must be set')
        self.base = f'https://graph-video.facebook.com/{self.version}'

    def upload(self, video_path, caption, **kwargs):
        """Upload video using resumable upload method"""
        
        # Step 1: Initialize upload session
        file_size = os.path.getsize(video_path)
        init_url = f"{self.base}/{self.page_id}/videos"
        
        init_params = {
            'access_token': self.token,
            'upload_phase': 'start',
            'file_size': file_size
        }
        
        try:
            logger.info('Initializing upload session for Facebook Page %s ...', self.page_id)
            r = requests.post(init_url, data=init_params)
            r.raise_for_status()
            
            session_data = r.json()
            upload_session_id = session_data.get('upload_session_id')
            
            if not upload_session_id:
                logger.error('Failed to get upload session ID: %s', session_data)
                return False, {'error': 'Failed to initialize upload session', 'details': session_data}
            
            logger.info('Upload session initialized. Session ID: %s', upload_session_id)
            
            # Step 2: Upload the video file
            transfer_url = f"{self.base}/{self.page_id}/videos"
            
            with open(video_path, 'rb') as video_file:
                transfer_params = {
                    'access_token': self.token,
                    'upload_phase': 'transfer',
                    'upload_session_id': upload_session_id,
                    'start_offset': 0  # ADDED: Start from beginning of file
                }
                
                files = {
                    'video_file_chunk': video_file
                }
                
                logger.info('Uploading video file...')
                r = requests.post(transfer_url, data=transfer_params, files=files)
                r.raise_for_status()
                
                transfer_result = r.json()
                logger.info('Video transfer complete: %s', transfer_result)
            
            # Step 3: Finalize the upload
            finish_url = f"{self.base}/{self.page_id}/videos"
            
            finish_params = {
                'access_token': self.token,
                'upload_phase': 'finish',
                'upload_session_id': upload_session_id,
                'description': caption
            }
            
            logger.info('Finalizing upload...')
            r = requests.post(finish_url, data=finish_params)
            r.raise_for_status()
            
            result = r.json()
            logger.info('Upload successful: %s', result)
            
            return True, result
            
        except requests.exceptions.HTTPError as e:
            try:
                error_detail = r.json()
            except:
                error_detail = r.text
            logger.exception('Facebook upload failed: %s', error_detail)
            return False, {'error': str(e), 'details': error_detail}
        except Exception as e:
            logger.exception('Facebook upload failed')
            return False, {'error': str(e)}