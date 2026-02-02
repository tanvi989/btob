import os
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.glasses_detector import router as glasses_router
from app.routes.landmark_detector import router as landmark_router
from app.routes.virtual_tryon import virtual_tryon
from dotenv import load_dotenv
load_dotenv()

# CORS: optional explicit list from env; if empty we use origin reflection below
_allowed = os.getenv("CORS_ALLOWED_ORIGINS", "").strip()
ALLOWED_ORIGINS = [o.strip() for o in _allowed.split(",") if o.strip()] or [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "https://multifolks.com",
    "https://www.multifolks.com",
    "http://multifolks.com",
    "http://www.multifolks.com",
    "https://test.multifolks.com",
    "http://test.multifolks.com",
]

# --------------------------------------------------
# FASTAPI APP
# --------------------------------------------------
app = FastAPI()

# Use origin reflection on server so any frontend domain works (no CORS list needed)
USE_CORS_REFLECT = os.getenv("CORS_REFLECT_ORIGIN", "true").lower() in ("1", "true", "yes")

if USE_CORS_REFLECT:
    class CORSReflectMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            origin = request.headers.get("origin")
            if request.method == "OPTIONS":
                from starlette.responses import Response
                return Response(
                    status_code=200,
                    headers={
                        "Access-Control-Allow-Origin": origin or "*",
                        "Access-Control-Allow-Credentials": "true",
                        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
                        "Access-Control-Allow-Headers": "*",
                        "Access-Control-Max-Age": "86400",
                    },
                )
            response = await call_next(request)
            if origin:
                response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
            response.headers["Access-Control-Allow-Headers"] = "*"
            return response

    app.add_middleware(CORSReflectMiddleware)
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
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
