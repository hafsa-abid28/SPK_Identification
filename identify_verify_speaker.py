"""
Script to identify/verify speakers with support for all audio formats.

TWO MODES:
1. IDENTIFY MODE: Find which registered speaker is talking (returns best match)
2. VERIFY MODE: Check if audio matches a specific speaker

Usage:
    # Identify who is speaking
    python identify_verify_speaker.py identify <audio_file>
    
    # Verify against specific speaker
    python identify_verify_speaker.py verify <speaker_code> <audio_file>

Examples:
    python identify_verify_speaker.py identify test_audio/unknown.mp3
    python identify_verify_speaker.py verify SPK_JOHN test_audio/test.wav
"""
from speaker_recognition import identify_speaker, verify_speaker, load_speaker_db
from pydub import AudioSegment
import os
import sys
import tempfile
import numpy as np

def convert_to_wav(audio_path, output_wav, max_duration_seconds=50):
    """
    Convert any audio format (MP3, WAV, M4A, OGG, etc.) to 16kHz mono WAV.
    Trims to first N seconds for faster processing.
    """
    try:
        audio = AudioSegment.from_file(audio_path)
        
        # Trim to max duration (in milliseconds)
        if len(audio) > max_duration_seconds * 1000:
            print(f"Trimming audio from {len(audio)/1000:.1f}s to {max_duration_seconds}s...")
            audio = audio[:max_duration_seconds * 1000]
        
        audio = audio.set_frame_rate(16000)
        audio = audio.set_channels(1)
        audio.export(output_wav, format="wav")
        return True
    except Exception as e:
        print(f"Error converting audio: {e}")
        return False

def run_identify_mode(audio_file):
    """Identify which registered speaker is talking (always returns best match)."""
    print("Loading speaker database...")
    speaker_db = load_speaker_db()
    
    if not speaker_db:
        print("No registered speakers found!")
        print("Please register speakers first using Register_Speaker.py")
        return
    
    print(f"Loaded {len(speaker_db)} registered speakers: {list(speaker_db.keys())}")
    print(f"Analyzing audio: {audio_file}")
    
    # Create temporary WAV file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
        temp_wav_path = tmp_wav.name
    
    try:
        # Convert to 16kHz WAV
        print("Converting audio to 16kHz WAV format...")
        if not convert_to_wav(audio_file, temp_wav_path):
            return
        
        # Identify speaker (use high threshold to always get best match)
        print("Identifying speaker...")
        speaker_code, score = identify_speaker(temp_wav_path, speaker_db, threshold=999)
        
        # Map speaker code to friendly name
        speaker_map = {
            "SPK_JOHN": "John",
            "SPK_JANE": "Jane"
        }
        speaker_name = speaker_map.get(speaker_code, speaker_code)
        
        print("\n" + "="*50)
        print(f"✓ RESULT: This is {speaker_name}")
        print(f"   Speaker Code: {speaker_code}")
        print(f"   Confidence Score: {score:.4f} (lower is better)")
        print("="*50)
        
    finally:
        if os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)

def run_verify_mode(speaker_code, audio_file):
    """Verify if audio matches a specific speaker."""
    print(f"Loading speaker: {speaker_code}")
    speaker_db = load_speaker_db()
    
    if speaker_code not in speaker_db:
        print(f"Error: Speaker '{speaker_code}' not found in database!")
        print(f"Available speakers: {list(speaker_db.keys())}")
        return
    
    reference_emb = speaker_db[speaker_code]
    print(f"Verifying audio against: {speaker_code}")
    print(f"Audio file: {audio_file}")
    
    # Create temporary WAV file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
        temp_wav_path = tmp_wav.name
    
    try:
        # Convert to 16kHz WAV
        print("Converting audio to 16kHz WAV format...")
        if not convert_to_wav(audio_file, temp_wav_path):
            return
        
        # Verify speaker
        print("Verifying speaker...")
        is_match, score = verify_speaker(temp_wav_path, reference_emb)
        
        print("\n" + "="*50)
        if is_match:
            print(f"✓ VERIFIED: This IS {speaker_code}")
            print(f"   Match Score: {score:.4f} (threshold: 0.75)")
            print("   Voice matches the registered speaker")
        else:
            print(f"❌ REJECTED: This is NOT {speaker_code}")
            print(f"   Match Score: {score:.4f} (threshold: 0.75)")
            print("   Voice does not match the registered speaker")
        print("="*50)
        
    finally:
        if os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)

if __name__ == "__main__":
    # Check arguments
    if len(sys.argv) < 3:
        print("Usage:")
        print("  Identify mode: python identify_verify_speaker.py identify <audio_file>")
        print("  Verify mode:   python identify_verify_speaker.py verify <speaker_code> <audio_file>")
        print("\nExamples:")
        print('  python identify_verify_speaker.py identify test_audio/unknown.mp3')
        print('  python identify_verify_speaker.py verify SPK001 test_audio/test.wav')
        sys.exit(1)
    
    mode = sys.argv[1].lower()
    
    if mode == "identify":
        if len(sys.argv) != 3:
            print("Usage: python identify_verify_speaker.py identify <audio_file>")
            sys.exit(1)
        
        audio_file = sys.argv[2]
        
        if not os.path.exists(audio_file):
            print(f"Error: Audio file '{audio_file}' not found!")
            sys.exit(1)
        
        run_identify_mode(audio_file)
        
    elif mode == "verify":
        if len(sys.argv) != 4:
            print("Usage: python identify_verify_speaker.py verify <speaker_code> <audio_file>")
            sys.exit(1)
        
        speaker_code = sys.argv[2]
        audio_file = sys.argv[3]
        
        if not os.path.exists(audio_file):
            print(f"Error: Audio file '{audio_file}' not found!")
            sys.exit(1)
        
        run_verify_mode(speaker_code, audio_file)
        
    else:
        print(f"Error: Invalid mode '{mode}'. Use 'identify' or 'verify'")
        sys.exit(1)
