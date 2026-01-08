"""
Simple test script - just edit the filenames below and run!
"""
from speaker_recognition import register_speaker, load_speaker_db, identify_speaker
from pydub import AudioSegment
import os
import tempfile

# ============================================================
# EDIT THESE SETTINGS
# ============================================================

# Speakers to register (audio_file, speaker_code, display_name)
SPEAKERS_TO_REGISTER = [
    ("sample.mp3", "SPK_JOHN", "John"),
    ("sample2.mp3", "SPK_JANE", "Jane"),
]

# Audio files to test/identify
AUDIO_FILES_TO_TEST = [
    "sample.mp3",
    "sample3.mp3",
]

# Maximum audio duration to process (in seconds)
MAX_AUDIO_DURATION = 50

def convert_to_wav(audio_path, output_wav, max_duration_seconds=MAX_AUDIO_DURATION):
    """Convert any audio format to 16kHz mono WAV (trim to first N seconds)."""
    try:
        audio = AudioSegment.from_file(audio_path)
        
        # Trim to max duration (in milliseconds)
        if len(audio) > max_duration_seconds * 1000:
            print(f"   Trimming audio from {len(audio)/1000:.1f}s to {max_duration_seconds}s...")
            audio = audio[:max_duration_seconds * 1000]
        
        audio = audio.set_frame_rate(16000).set_channels(1)
        audio.export(output_wav, format="wav")
        return True
    except Exception as e:
        print(f"Error converting audio: {e}")
        return False

def register_speakers():
    """Register all speakers from SPEAKERS_TO_REGISTER list."""
    print("="*60)
    print("REGISTERING SPEAKERS")
    print("="*60)
    
    for audio_file, speaker_code, display_name in SPEAKERS_TO_REGISTER:
        if not os.path.exists(audio_file):
            print(f"\n⚠ Error: {audio_file} not found! Skipping...")
            continue
        
        print(f"\nRegistering: {display_name} ({speaker_code})")
        print(f"Audio: {audio_file}")
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
            temp_wav_path = tmp_wav.name
        
        try:
            print("Converting to 16kHz WAV...")
            if not convert_to_wav(audio_file, temp_wav_path):
                continue
            
            print("Registering in database...")
            register_speaker(speaker_code, display_name, temp_wav_path)
            
            print(f"✓ {display_name} registered successfully!")
            print(f"  Code: {speaker_code}")
            print(f"  Voiceprint: voiceprints/{speaker_code}.npy")
        finally:
            if os.path.exists(temp_wav_path):
                os.remove(temp_wav_path)

def test_identification():
    """Test identification on all files in AUDIO_FILES_TO_TEST list."""
    print("\n" + "="*60)
    print("TESTING SPEAKER IDENTIFICATION")
    print("="*60)
    
    # Load speaker database
    print("\nLoading speaker database...")
    speaker_db = load_speaker_db()
    
    if not speaker_db:
        print("No registered speakers found!")
        return
    
    print(f"Loaded {len(speaker_db)} registered speakers: {list(speaker_db.keys())}")
    
    # Map speaker codes to friendly names
    speaker_map = {
        "SPK_JOHN": "John",
        "SPK_JANE": "Jane"
    }
    
    # Test each audio file
    for audio_file in AUDIO_FILES_TO_TEST:
        if not os.path.exists(audio_file):
            print(f"\n⚠ {audio_file} not found - skipping")
            continue
        
        print(f"\n{'='*60}")
        print(f"Testing: {audio_file}")
        print('='*60)
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
            temp_wav_path = tmp_wav.name
        
        try:
            print("Converting to 16kHz WAV...")
            if not convert_to_wav(audio_file, temp_wav_path):
                continue
            
            print("Identifying speaker...")
            # Get best match (use high threshold to always get result)
            speaker_code, score = identify_speaker(temp_wav_path, speaker_db, threshold=999)
            
            # Get friendly name
            speaker_name = speaker_map.get(speaker_code, speaker_code)
            
            print(f"✓ RESULT: This is {speaker_name}")
            print(f"   Speaker Code: {speaker_code}")
            print(f"   Confidence Score: {score:.4f} ")
        except Exception as e:
            print(f"Error during identification: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if os.path.exists(temp_wav_path):
                os.remove(temp_wav_path)

if __name__ == "__main__":
    print("\n" + "="*60)
    print("SPEAKER RECOGNITION TEST")
    print("="*60)
    print("\nThis will:")
    print("1. Register speakers from SPEAKERS_TO_REGISTER list")
    print("2. Test/identify audio files from AUDIO_FILES_TO_TEST list")
    print("="*60)
    
    input("\nPress Enter to start...")
    
    # Step 1: Register speakers
    register_speakers()
    
    # Step 2: Test identification
    test_identification()
    
    print("\n" + "="*60)
    print("TEST COMPLETED")
    print("="*60)
