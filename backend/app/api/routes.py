"""
API routes for OmniFlow AI backend.
Includes: auth token, telemetry analysis (JWT-protected), and system health.
Rate limiting applied per endpoint. Request tracking via unique request_id.
"""
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.models.schemas import TelemetryData, SystemState, LoginRequest, Token
from app.core.decision_engine import DecisionEngine
from app.utils.security import (
    verify_password, create_access_token,
    get_password_hash, require_auth,
)
from app.services.firebase import save_state, save_analysis_log, firestore_status
from app.utils.logger import get_logger

log = get_logger(__name__)
router = APIRouter()
engine = DecisionEngine()
limiter = Limiter(key_func=get_remote_address)

# Mock user DB – replace with real store in production
users_db = {"admin": get_password_hash("password123")}


@router.post("/token", response_model=Token)
@limiter.limit("10/minute")
async def login(request: Request, req: LoginRequest):
    """Authenticate user credentials and return a signed JWT access token."""
    user_hash = users_db.get(req.username)
    if not user_hash or not verify_password(req.password, user_hash):
        log.warning(f"Failed login attempt for user: {req.username}")
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    token = create_access_token(data={"sub": req.username})
    log.info(f"Token issued for user: {req.username}")
    return {"access_token": token, "token_type": "bearer"}


@router.post("/analyze", response_model=SystemState)
@limiter.limit("30/minute")
async def process_telemetry(
    request: Request,
    data: TelemetryData,
    _auth: dict = Depends(require_auth),
):
    """
    Process real-time venue telemetry and return deterministic system state.
    Requires: Authorization: Bearer <token>
    Logs analysis metadata to Firestore 'analysis_logs' collection.
    """
    request_id = str(uuid.uuid4())
    user_id = _auth.get("sub", "anonymous")
    log.info(f"[{request_id}] analyze called by user={user_id}")

    state = engine.process_telemetry(data)

    log_entry = {
        "request_id": request_id,
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat(),
        "CDI": state.analysis.cdi,
        "score": state.experience_score,
        "risk_level": state.analysis.safety_risk,
    }

    try:
        save_state(state.model_dump())
        save_analysis_log(log_entry)
    except Exception as e:
        log.error(f"[{request_id}] Firestore write failed (non-fatal): {e}")

    return state


@router.get("/health")
async def health_check():
    """
    Returns live system status including Firestore connectivity.
    Safe to call without authentication.
    """
    db_status = firestore_status()
    return {
        "status": "OK",
        "uptime": "running",
        "services": {
            "database": db_status,
            "agents": "running",
        }
    }
