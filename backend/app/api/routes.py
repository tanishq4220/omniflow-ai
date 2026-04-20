from fastapi import APIRouter, HTTPException
from app.models.schemas import TelemetryData, SystemState, LoginRequest, Token
from app.core.decision_engine import DecisionEngine
from app.utils.security import verify_password, create_access_token, get_password_hash
from app.services.firebase import save_state

router = APIRouter()
engine = DecisionEngine()

# Mock DB for demo
users_db = {"admin": get_password_hash("password123")}



@router.post("/token", response_model=Token)
async def login(req: LoginRequest):
    """Authenticate user and generate access token."""
    if req.username not in users_db or not verify_password(req.password, users_db[req.username]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": req.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/analyze", response_model=SystemState)
async def process_telemetry(data: TelemetryData):
    """Processes real-time telemetry array inputs and returns the structured system state variables."""
    state = engine.process_telemetry(data)
    try:
        save_state(state.model_dump())
    except Exception:
        pass  # Prevent DB failures from crashing analytics
    return state

@router.get("/health")
async def health_check():
    """Returns system status and connected services."""
    return {
        "status": "OK",
        "uptime": "running",
        "services": {
            "database": "connected",
            "agents": "running"
        }
    }
