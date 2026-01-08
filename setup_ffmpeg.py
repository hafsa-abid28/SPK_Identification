"""
FFmpeg Setup Script - Downloads and configures FFmpeg locally for this project
"""
import os
import urllib.request
import zipfile
import sys

FFMPEG_URL = "https://github.com/GyanD/codexffmpeg/releases/download/7.1/ffmpeg-7.1-essentials_build.zip"
FFMPEG_ZIP = "ffmpeg.zip"
FFMPEG_DIR = "ffmpeg"
extracted_dir = None  # Track the actual extracted directory name

def download_ffmpeg():
    """Download FFmpeg if not already present."""
    if os.path.exists(FFMPEG_DIR):
        print("✓ FFmpeg directory already exists")
        return True
    
    print("Downloading FFmpeg (this may take a minute)...")
    try:
        urllib.request.urlretrieve(FFMPEG_URL, FFMPEG_ZIP)
        print("✓ Download complete")
        return True
    except Exception as e:
        print(f"Error downloading FFmpeg: {e}")
        return False

def extract_ffmpeg():
    """Extract FFmpeg zip file."""
    global extracted_dir
    
    if not os.path.exists(FFMPEG_ZIP):
        print("Error: FFmpeg zip file not found")
        return False
    
    print("Extracting FFmpeg...")
    try:
        with zipfile.ZipFile(FFMPEG_ZIP, 'r') as zip_ref:
            zip_ref.extractall(".")
        
        # Find extracted folder
        for item in os.listdir("."):
            if item.startswith("ffmpeg-") and os.path.isdir(item):
                extracted_dir = item
                break
        
        # Clean up zip file
        if os.path.exists(FFMPEG_ZIP):
            os.remove(FFMPEG_ZIP)
        print("✓ Extraction complete")
        return True
    except Exception as e:
        print(f"Error extracting FFmpeg: {e}")
        return False

def setup_ffmpeg_path():
    """Add FFmpeg to system PATH for this session."""
    ffmpeg_folder = extracted_dir if extracted_dir else FFMPEG_DIR
    ffmpeg_bin = os.path.abspath(os.path.join(ffmpeg_folder, "bin"))
    
    if not os.path.exists(ffmpeg_bin):
        print(f"Error: FFmpeg bin directory not found at {ffmpeg_bin}")
        return False
    
    # Add to PATH for current process
    os.environ["PATH"] = ffmpeg_bin + os.pathsep + os.environ["PATH"]
    
    print(f"✓ FFmpeg added to PATH: {ffmpeg_bin}")
    print("\nFFmpeg is now ready to use!")
    return ffmpeg_bin

if __name__ == "__main__":
    print("="*60)
    print("FFmpeg Setup for Speaker Recognition")
    print("="*60)
    print()
    
    if not download_ffmpeg():
        sys.exit(1)
    
    if not os.path.exists(FFMPEG_DIR) and not extracted_dir:
        if not extract_ffmpeg():
            sys.exit(1)
    
    ffmpeg_bin = setup_ffmpeg_path()
    if not ffmpeg_bin:
        sys.exit(1)
    
    print()
    print("="*60)
    print("✓ FFmpeg setup complete!")
    print("="*60)
    print(f"\nFFmpeg location: {ffmpeg_bin}")
    print("\nTo use FFmpeg, run demo with:")
    print(f'  $env:PATH = "{ffmpeg_bin};$env:PATH"; python demo.py')
