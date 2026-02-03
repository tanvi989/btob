# Backend API - Docker image for Cloud Run / any container host
FROM python:3.11-slim

WORKDIR /app

# System deps for OpenCV / some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY . .

# Cloud Run sets PORT at runtime (default 8080); listen on all interfaces
EXPOSE 8080

# Run FastAPI with Uvicorn (PORT read at container start; Cloud Run sets PORT)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
