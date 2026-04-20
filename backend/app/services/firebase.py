import os
import firebase_admin
from firebase_admin import credentials, firestore
from app.utils.logger import get_logger

log = get_logger(__name__)

def init_firebase():
    """Initialize Firebase App."""
    try:
        if not firebase_admin._apps:
            # For production, Use GOOGLE_APPLICATION_CREDENTIALS env var
            firebase_admin.initialize_app()
        return firestore.client()
    except Exception as e:
        log.warning(f"Firebase not initialized locally: {e}. Mocking it.")
        return None

db = init_firebase()

def save_state(state_dict: dict):
    """Save state to firestore."""
    if db:
        try:
            db.collection("system_states").add(state_dict)
        except Exception as e:
            log.error(f"Failed to save state: {e}")
