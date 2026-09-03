#!/usr/bin/env python3
"""Main entrypoint: upload to facebook, youtube, or tiktok"""
import argparse, logging
from dotenv import load_dotenv
from uploaders.facebook_uploader import FacebookUploader
from uploaders.youtube_uploader import YouTubeUploader
from uploaders.tiktok_uploader import TikTokUploader
from utils.file_loader import load_caption
import os

load_dotenv()
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

UPLOADERS = {
    'facebook': FacebookUploader,
    'youtube': YouTubeUploader,
    'tiktok': TikTokUploader,
}

def run_upload(platform, video_path, caption_text, title=None, dry_run=False):
    uploader_cls = UPLOADERS.get(platform)
    if not uploader_cls:
        logger.error('Unsupported platform: %s', platform)
        return False
    uploader = uploader_cls()
    if dry_run:
        logger.info('Dry run: would upload %s to %s with caption: %s', video_path, platform, caption_text)
        return True
    success, meta = uploader.upload(video_path, caption_text, title=title)
    if success:
        logger.info('Upload succeeded: %s', meta.get('url') or meta.get('id') or str(meta)[:200])
    else:
        logger.error('Upload failed: %s', meta)
    return success

def run_multi_upload(platforms, video_path, caption_text, title=None, dry_run=False):
    """Upload to multiple platforms"""
    results = {}
    for platform in platforms:
        logger.info('Starting upload to %s...', platform)
        success = run_upload(platform, video_path, caption_text, title=title, dry_run=dry_run)
        results[platform] = success
    return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--platform', required=False, choices=list(UPLOADERS.keys()), help='Single platform to upload to')
    parser.add_argument('--platforms', required=False, help='Comma-separated list of platforms (e.g., youtube,facebook,tiktok)')
    parser.add_argument('--all', action='store_true', help='Upload to all available platforms')
    parser.add_argument('--video', required=True)
    parser.add_argument('--caption', required=False)
    parser.add_argument('--caption-text', required=False)
    parser.add_argument('--title', required=False)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    # Determine which platforms to upload to
    platforms = []
    if args.all:
        platforms = list(UPLOADERS.keys())
    elif args.platforms:
        platforms = [p.strip() for p in args.platforms.split(',')]
        invalid = [p for p in platforms if p not in UPLOADERS]
        if invalid:
            logger.error('Invalid platforms: %s', ', '.join(invalid))
            return
    elif args.platform:
        platforms = [args.platform]
    else:
        logger.error('Must specify --platform, --platforms, or --all')
        parser.print_help()
        return

    caption_text = args.caption_text
    if args.caption and not caption_text:
        caption_text = load_caption(args.caption)
    if caption_text is None:
        caption_text = ''
    
    if len(platforms) > 1:
        run_multi_upload(platforms, args.video, caption_text, title=args.title, dry_run=args.dry_run)
    else:
        run_upload(platforms[0], args.video, caption_text, title=args.title, dry_run=args.dry_run)

if __name__ == '__main__':
    main()
