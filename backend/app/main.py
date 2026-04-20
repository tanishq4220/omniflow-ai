from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.api.routes import router as api_router
from app.api.websocket import router as ws_router
import time

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="OmniFlow AI API")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

app.include_router(api_router)
app.include_router(api_router, prefix="/api")
app.include_router(ws_router)

@app.get("/")
async def root():
    return {
        "message": "OmniFlow AI Backend is live",
        "endpoints": {
            "health": "/health or /api/health",
            "analyze": "/analyze or /api/analyze"
        }
    }
