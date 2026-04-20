"""
Firebase service module.
Initializes Firestore client using GOOGLE_APPLICATION_CREDENTIALS env var.
Exposes save_analysis_log() for structured per-request audit logging.
"""
import os
import firebase_admin
from firebase_admin import credentials, firestore
from app.utils.logger import get_logger

log = get_logger(__name__)

_FIREBASE_PROJECT = os.getenv("FIREBASE_PROJECT_ID", "")


def init_firebase():
    """Initialize Firebase app; returns Firestore client or None on failure."""
    try:
        if not firebase_admin._apps:
            cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
            if cred_path and os.path.isfile(cred_path):
                firebase_admin.initialize_app(credentials.Certificate(cred_path))
            else:
                firebase_admin.initialize_app()  # Uses ADC on Cloud Run
        return firestore.client()
    except Exception as e:
        log.warning(f"Firebase unavailable – running in degraded mode: {e}")
        return None


db = init_firebase()


def firestore_status() -> str:
    """Ping Firestore with a lightweight read; returns 'connected' or 'failed'."""
    if db is None:
        return "failed"
    try:
        db.collection("health_check").limit(1).get()
        return "connected"
    except Exception as e:
        log.error(f"Firestore ping failed: {e}")
        return "failed"


def save_state(state_dict: dict):
    """Legacy – persist raw system state to 'system_states' collection."""
    if db:
        try:
            db.collection("system_states").add(state_dict)
        except Exception as e:
            log.error(f"save_state failed: {e}")


def save_analysis_log(log_entry: dict):
    """
    Store a structured analysis audit log to 'analysis_logs' collection.
    Includes: timestamp, request_id, user_id, CDI, score, risk_level.
    """
    if db:
        try:
            db.collection("analysis_logs").add(log_entry)
            log.info(f"[Firestore] Logged request {log_entry.get('request_id', '?')}")
        except Exception as e:
            log.error(f"save_analysis_log failed: {e}")
