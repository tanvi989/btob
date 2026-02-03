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

# CORS: allowed frontend origins (add more in .env as CORS_ALLOWED_ORIGINS if needed)
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
_extra = os.getenv("CORS_ALLOWED_ORIGINS", "").strip()
if _extra:
    ALLOWED_ORIGINS.extend(o.strip() for o in _extra.split(",") if o.strip())
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# --------------------------------------------------
# ROUTES
# --------------------------------------------------
app.include_router(glasses_router)
app.include_router(landmark_router)
app.include_router(virtual_tryon)  # from virtual_tryon.py
# Root endpoint
@app.get("/")
def root():
    return {"message": "API running"}
