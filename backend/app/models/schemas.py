"""
Strict Pydantic schemas with full field-level validation constraints.
TelemetryData supports large-scale real-world scenarios (up to 100,000 people).
AgentResponse now includes overload_factor for production-grade crowd modelling.
"""
from pydantic import BaseModel, Field


class TelemetryData(BaseModel):
    """Validated real-time telemetry payload from venue sensors."""
    people_count: int   = Field(..., ge=0,   le=100_000,  description="Current people in venue (0–100,000)")
    max_capacity: int   = Field(..., gt=0,   le=100_000,  description="Maximum venue capacity (1–100,000)")
    queue_length: int   = Field(..., ge=0,   le=50_000,   description="Current queue length (0–50,000)")
    service_rate: float = Field(..., gt=0.0, le=1_000.0,  description="People served per minute (>0–1,000)")
    emotion_score: float = Field(..., ge=0.0, le=100.0,   description="Attendee sentiment score (0–100)")


class AgentResponse(BaseModel):
    """Computed analysis outputs from the multi-agent engine."""
    cdi: float                    # Normalized 0–100 crowd density index
    overload_factor: float        # Raw ratio: people / capacity (can exceed 1.0)
    wait_time: float
    safety_risk: str
    predicted_congestion: int


class SystemState(BaseModel):
    """Full system analysis result returned by the /analyze endpoint."""
    telemetry: TelemetryData
    analysis: AgentResponse
    experience_score: float


class LoginRequest(BaseModel):
    """Authentication credentials for token generation."""
    username: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=1, max_length=128)


class Token(BaseModel):
    """JWT access token response."""
    access_token: str
    token_type: str
