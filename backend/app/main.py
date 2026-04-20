"""
OmniFlow AI – FastAPI application entry point.
Security features: CORS restriction, security headers, rate limiting,
global exception handler, request-time tracking, and JWT enforcement.
"""
import os
import time
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi import Depends
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.api.routes import router as api_router
from app.api.websocket import router as ws_router
from app.utils.security import require_auth

log = logging.getLogger("omniflow.main")

# ---------- App ----------
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="OmniFlow AI API",
    version="1.0.0",
    description="Autonomous Event Intelligence & Experience Optimization System",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ---------- CORS ----------
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "https://omniflow-backend-342805636089.us-central1.run.app"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

# ---------- Security headers middleware ----------
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Attach security and process-time headers to every response."""
    start = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time"]         = f"{time.time() - start:.4f}s"
    response.headers["X-Content-Type-Options"]  = "nosniff"
    response.headers["X-Frame-Options"]         = "DENY"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"]         = "strict-origin-when-cross-origin"
    response.headers["X-XSS-Protection"]        = "1; mode=block"
    return response

# ---------- Global exception handler ----------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Return safe JSON errors without leaking internal stack traces."""
    log.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": "Please try again later"},
    )

# ---------- Routers ----------
app.include_router(api_router, prefix="/api")   # /api/health, /api/analyze
app.include_router(api_router)                  # /health, /analyze (fallback)
app.include_router(ws_router)

# ---------- Static dashboard ----------
_static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static"))
if os.path.isdir(_static_dir):
    app.mount("/static", StaticFiles(directory=_static_dir), name="static")

@app.get("/openapi.json", include_in_schema=False)
async def get_openapi_endpoint(_dict: dict = Depends(require_auth)):
    return app.openapi()

@app.get("/secure-docs", include_in_schema=False)
async def secure_swagger_ui(_dict: dict = Depends(require_auth)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="OmniFlow AI Secure Docs")

@app.get("/", include_in_schema=False)
async def serve_dashboard():
    """Serve OmniFlow AI dashboard UI at root."""
    index = os.path.join(_static_dir, "index.html")
    if os.path.isfile(index):
        return FileResponse(index, media_type="text/html")
    return {
        "message": "OmniFlow AI Backend is live",
        "status": "running",
        "docs": "/docs",
        "endpoints": {"health": "/api/health", "analyze": "/api/analyze"},
    }
