import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.glasses_detector import router as glasses_router
from app.routes.landmark_detector import router as landmark_router
from app.routes.virtual_tryon import virtual_tryon
from dotenv import load_dotenv

load_dotenv()

# --------------------------------------------------
# FASTAPI APP
# --------------------------------------------------
app = FastAPI()

# --------------------------------------------------
# CORS CONFIGURATION
# --------------------------------------------------
# List of allowed origins
ALLOWED_ORIGINS = [
    "https://test.multifolks.com",
    "https://www.multifolks.com",
    "https://multifolks.com",
    "https://test.tanviparadkar.in",
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
]

# Add any additional origins from environment variable
_extra = os.getenv("CORS_ALLOWED_ORIGINS", "").strip()
if _extra:
    ALLOWED_ORIGINS.extend(o.strip() for o in _extra.split(",") if o.strip())

# Add CORS middleware - MUST be added before routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # List of allowed origins
    allow_credentials=True,          # Allow cookies/authentication
    allow_methods=["*"],             # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],             # Allow all headers
    expose_headers=["*"],            # Expose all headers to the frontend
)

# --------------------------------------------------
# ROUTES
# --------------------------------------------------
app.include_router(glasses_router)
app.include_router(landmark_router)
app.include_router(virtual_tryon)  # from virtual_tryon.py

# --------------------------------------------------
# ROOT ENDPOINT
# --------------------------------------------------
@app.get("/")
def root():
    return {"message": "Virtual Try-On API is running"}

# --------------------------------------------------
# HEALTH CHECK ENDPOINT (Optional but recommended)
# --------------------------------------------------
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "vtob-api"}
