FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (FFmpeg for audio processing, build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    espeak-ng \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY backend /app/backend
COPY frontend /app/frontend
COPY .env.example /app/.env.example

# Set PYTHONPATH
ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
