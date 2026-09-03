import os

video_path = r"C:\Users\rafey\Desktop\My Computer\1 Companies\2 Culture Spotlight\Automation\video_poster_tfb\videos\test.mp4"

# Check if file exists
if os.path.exists(video_path):
    file_size = os.path.getsize(video_path)
    file_size_mb = file_size / (1024 * 1024)
     
    print(f"✓ Video file found")
    print(f"File size: {file_size_mb:.2f} MB ({file_size} bytes)")
    print(f"File extension: {os.path.splitext(video_path)[1]}")
    
    # Try to read first few bytes to check if file is accessible
    try:
        with open(video_path, 'rb') as f:
            first_bytes = f.read(12)
            print(f"First bytes (hex): {first_bytes.hex()}")
            
            # Check MP4 signature
            if first_bytes[4:8] == b'ftyp':
                print("✓ Valid MP4 file signature detected")
            else:
                print("✗ WARNING: File doesn't appear to be a valid MP4")
    except Exception as e:
        print(f"✗ Error reading file: {e}")
else:
    print(f"✗ File not found at: {video_path}")