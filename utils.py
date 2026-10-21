"""
Face recognition utilities using DeepFace + VGG-Face.
Embedding-based recognition with cosine similarity matching.
"""
import os
import pickle
import numpy as np
from django.conf import settings
from .models import KnownFace

# DeepFace is heavy; import lazily inside functions to keep Django boot fast
EMBEDDINGS_DB = os.path.join(settings.MEDIA_ROOT, 'known_faces.pkl')
SIMILARITY_THRESHOLD = 0.68  # VGG-Face cosine threshold (lower = more similar)
MODEL_NAME = 'VGG-Face'
DETECTOR_BACKEND = 'opencv'


def _load_db():
    """Load embeddings database from pickle file."""
    if os.path.exists(EMBEDDINGS_DB):
        try:
            with open(EMBEDDINGS_DB, 'rb') as f:
                return pickle.load(f)
        except Exception:
            return {}
    return {}


def _save_db(db):
    """Persist embeddings database."""
    os.makedirs(os.path.dirname(EMBEDDINGS_DB), exist_ok=True)
    with open(EMBEDDINGS_DB, 'wb') as f:
        pickle.dump(db, f)


def extract_embedding(image_path):
    """Extract a 512-d facial embedding from an image using VGG-Face."""
    from deepface import DeepFace
    try:
        result = DeepFace.represent(
            img_path=image_path,
            model_name=MODEL_NAME,
            detector_backend=DETECTOR_BACKEND,
            enforce_detection=True,
        )
        if isinstance(result, list) and len(result) > 0:
            return np.array(result[0]['embedding'], dtype=np.float32)
    except Exception as e:
        print(f"[FaceRec] Embedding extraction failed: {e}")
    return None


def enroll_face(patient_id, known_face_id, person_name, relationship, image_paths):
    """
    Enroll a known face by extracting embeddings from multiple images,
    averaging them, and storing in the DB.
    """
    embeddings = []
    for path in image_paths:
        emb = extract_embedding(path)
        if emb is not None:
            embeddings.append(emb)

    if not embeddings:
        return False, 0

    # mean embedding represents the person
    avg_embedding = np.mean(embeddings, axis=0)
    avg_embedding = avg_embedding / np.linalg.norm(avg_embedding)  # normalize

    db = _load_db()
    key = f"patient_{patient_id}"
    if key not in db:
        db[key] = {}

    db[key][known_face_id] = {
        'person_name': person_name,
        'relationship': relationship,
        'embedding': avg_embedding,
        'image_count': len(embeddings),
    }
    _save_db(db)
    return True, len(embeddings)


def remove_face(patient_id, known_face_id):
    """Remove an enrolled face from the embeddings DB."""
    db = _load_db()
    key = f"patient_{patient_id}"
    if key in db and known_face_id in db[key]:
        del db[key][known_face_id]
        _save_db(db)
        return True
    return False


def cosine_distance(a, b):
    """Cosine distance (0 = identical, 2 = opposite)."""
    a_norm = a / (np.linalg.norm(a) + 1e-10)
    b_norm = b / (np.linalg.norm(b) + 1e-10)
    return 1.0 - float(np.dot(a_norm, b_norm))


def recognize_face(patient_id, image_path):
    """
    Recognize a face in the given image against patient's enrolled DB.
    Returns dict: {match, person_name, relationship, confidence, distance}.
    """
    query_emb = extract_embedding(image_path)
    if query_emb is None:
        return {
            'match': False, 'person_name': 'No face detected',
            'relationship': '', 'confidence': 0.0, 'distance': 1.0,
        }

    db = _load_db()
    key = f"patient_{patient_id}"
    if key not in db or not db[key]:
        return {
            'match': False, 'person_name': 'Unknown',
            'relationship': '', 'confidence': 0.0, 'distance': 1.0,
        }

    best_match = None
    best_distance = 999.0
    for kf_id, info in db[key].items():
        dist = cosine_distance(query_emb, info['embedding'])
        if dist < best_distance:
            best_distance = dist
            best_match = info

    if best_match and best_distance < SIMILARITY_THRESHOLD:
        confidence = max(0.0, (1.0 - best_distance / SIMILARITY_THRESHOLD)) * 100

        known_face = KnownFace.objects.get(
            patient__id=patient_id,
            person_name=best_match['person_name']
        )

        return {
            'match': True,
            'person_name': best_match['person_name'],
            'primary_image': known_face.primary_image.url,
            'relationship': best_match['relationship'],
            'confidence': round(confidence, 2),
            'distance': round(best_distance, 4),
        }

    return {
        'match': False, 'person_name': 'Unknown',
        'relationship': '', 'confidence': 0.0,
        'distance': round(best_distance, 4),
    }
