"""
Script to register speakers with support for all audio formats (MP3, WAV, M4A, OGG, etc.)

Usage:
    python Register_Speaker.py <speaker_code> <display_name> <audio_file>

Examples:
    python Register_Speaker.py SPK_JOHN "John Doe" audio/john.mp3
    python Register_Speaker.py SPK_JANE "Jane Smith" audio/jane.wav
"""
from speaker_recognition import register_speaker as register_speaker_func
from pydub import AudioSegment
import os
import sys
import tempfile

def convert_to_wav(audio_path, output_wav, max_duration_seconds=50):
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

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python Register_Speaker.py <speaker_code> <display_name> <audio_file>")
        print("\nExamples:")
        print('  python Register_Speaker.py SPK_JOHN "John Doe" audio/john.mp3')
        print('  python Register_Speaker.py SPK_JANE "Jane Smith" audio/jane.mp3')
        sys.exit(1)
    
    speaker_code, display_name, audio_file = sys.argv[1], sys.argv[2], sys.argv[3]
    
    if not os.path.exists(audio_file):
        print(f"Error: Audio file '{audio_file}' not found!")
        sys.exit(1)
    
    print(f"Registering: {display_name} ({speaker_code})")
    print(f"Audio: {audio_file}")
    
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
        temp_wav_path = tmp_wav.name
    
    try:
        print("Converting to 16kHz WAV...")
        if not convert_to_wav(audio_file, temp_wav_path):
            sys.exit(1)
        
        print("Registering in database...")
        register_speaker_func(speaker_code, display_name, temp_wav_path)
        
        print(f"\n✓ {display_name} registered successfully!")
        print(f"  Code: {speaker_code}")
        print(f"  Voiceprint: voiceprints/{speaker_code}.npy")
    finally:
        if os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)
