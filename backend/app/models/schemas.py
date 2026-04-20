from pydantic import BaseModel, Field

class TelemetryData(BaseModel):
    people_count: int = Field(..., ge=0)
    max_capacity: int = Field(..., gt=0)
    queue_length: int = Field(..., ge=0)
    service_rate: float = Field(..., gt=0.0)
    emotion_score: float = Field(..., ge=0.0, le=100.0)

class AgentResponse(BaseModel):
    cdi: float
    wait_time: float
    safety_risk: str
    predicted_congestion: int

class SystemState(BaseModel):
    telemetry: TelemetryData
    analysis: AgentResponse
    experience_score: float

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
