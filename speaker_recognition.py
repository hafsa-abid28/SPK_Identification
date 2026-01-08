import os
import numpy as np
import torch
import soundfile as sf
from speechbrain.inference.speaker import SpeakerRecognition
import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "database": "mydb",
    "user": "postgres",
    "password": "Pass,822",
    "port": 5432
}

def get_conn():
    """Create and return a PostgreSQL database connection."""
    return psycopg2.connect(**DB_CONFIG)

MODEL = SpeakerRecognition.from_hparams(
    source="speechbrain/spkrec-ecapa-voxceleb",
    savedir="models/ecapa"
)

EMBED_DIR = "voiceprints"
os.makedirs(EMBED_DIR, exist_ok=True)

def extract_embedding(wav_path: str):
    """
    Extract voice embedding from audio file.
    
    Args:
        wav_path: Path to 16kHz WAV audio file
                  Example: "audio_samples/john_voice.wav"
    """
    signal, sr = sf.read(wav_path)
    if sr != 16000:
        raise ValueError("Audio must be 16kHz")

    signal = torch.tensor(signal).unsqueeze(0)
    emb = MODEL.encode_batch(signal)
    return emb.squeeze().detach().cpu().numpy()

def register_speaker(speaker_code, display_name, wav_path):
    """
    Enroll a new speaker into the system.
    
    Args:
        speaker_code: Unique ID for the speaker (e.g., "SPK001")
        display_name: Human-readable name (e.g., "John Doe")
        wav_path: Path to speaker's voice sample (16kHz WAV)
                  Example: "enrollment_audio/john_sample.wav"
    """
    emb = extract_embedding(wav_path)
    emb_path = f"{EMBED_DIR}/{speaker_code}.npy"
    np.save(emb_path, emb)

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO speakers (speaker_code, display_name, embedding_path)
        VALUES (%s, %s, %s)
        ON CONFLICT (speaker_code)
        DO UPDATE SET embedding_path = EXCLUDED.embedding_path
    """, (speaker_code, display_name, emb_path))

    conn.commit()
    cur.close()
    conn.close()

def load_speaker_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT speaker_code, embedding_path
        FROM speakers
        WHERE active = TRUE
    """)

    speaker_db = {}
    for code, path in cur.fetchall():
        speaker_db[code] = np.load(path)

    cur.close()
    conn.close()
    return speaker_db

def cosine_distance(a, b):
    return 1 - (a @ b) / (np.linalg.norm(a) * np.linalg.norm(b))

def identify_speaker(wav_path, speaker_db, threshold=0.75):
    """
    Identify which registered speaker is talking (1-to-N matching).
    
    Args:
        wav_path: Path to test audio file (16kHz WAV)
                  Example: "test_audio/unknown_voice.wav"
        speaker_db: Dictionary of enrolled speakers (from load_speaker_db())
        threshold: Maximum distance for a match (default 0.75)
    
    Returns:
        (speaker_code, score) if match found, or ("unknown", score)
    """
    test_emb = extract_embedding(wav_path)

    best_speaker = None
    best_score = float("inf")

    for speaker, ref_emb in speaker_db.items():
        dist = cosine_distance(test_emb, ref_emb)
        if dist < best_score:
            best_score = dist
            best_speaker = speaker

    if best_score < threshold:
        return best_speaker, best_score
    return "unknown", best_score

def verify_speaker(wav_path, reference_emb, threshold=0.75):
    """
    Verify if audio matches a specific speaker (1-to-1 matching).
    
    Args:
        wav_path: Path to test audio file (16kHz WAV)
                  Example: "verify_audio/test_voice.wav"
        reference_emb: Reference embedding of the claimed speaker
        threshold: Maximum distance for verification (default 0.75)
    
    Returns:
        (True/False, distance_score)
    """
    test_emb = extract_embedding(wav_path)
    dist = cosine_distance(test_emb, reference_emb)
    return dist < threshold, dist


# ============================================================================
# USAGE EXAMPLES - How to provide audio files:
# ============================================================================
#
# 1. REGISTER A SPEAKER (Enrollment):
#    register_speaker("SPK001", "John Doe", "audio/john_enrollment.wav")
#
# 2. IDENTIFY WHO IS SPEAKING:
#    speaker_db = load_speaker_db()  # Load all enrolled speakers
#    speaker, score = identify_speaker("audio/unknown_voice.wav", speaker_db)
#    print(f"Identified: {speaker} with score {score}")
#
# 3. VERIFY A SPECIFIC SPEAKER:
#    john_emb = speaker_db["SPK001"]  # Get John's embedding
#    is_john, score = verify_speaker("audio/test_voice.wav", john_emb)
#    print(f"Is John? {is_john} (score: {score})")
#
# Note: All audio files must be 16kHz WAV format!
# ============================================================================
