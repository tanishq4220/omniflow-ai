from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.api.routes import router as api_router
from app.api.websocket import router as ws_router
import time, os

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="OmniFlow AI API", docs_url="/docs", redoc_url="/redoc")

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
    """Track response latency via X-Process-Time header."""
    start_time = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time"] = str(time.time() - start_time)
    return response

# API routes
app.include_router(api_router, prefix="/api")
app.include_router(api_router)          # fallback: /health, /analyze
app.include_router(ws_router)

# Static dashboard UI
_static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.isdir(_static_dir):
    app.mount("/static", StaticFiles(directory=_static_dir), name="static")

@app.get("/", include_in_schema=False)
async def serve_dashboard():
    """Serve the OmniFlow AI dashboard UI at root."""
    index = os.path.join(_static_dir, "index.html")
    if os.path.isfile(index):
        return FileResponse(index, media_type="text/html")
    return {
        "message": "OmniFlow AI Backend is live",
        "endpoints": {"health": "/api/health", "analyze": "/api/analyze", "docs": "/docs"}
    }
