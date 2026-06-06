FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project into a `backend` package directory so imports like
# `from backend.config import ...` work when running inside the image.
COPY . ./backend/

# Hint port for some platforms and local readers
EXPOSE 8000

# Use the PORT env var supplied by Render (fallback to 8000).
# Use a shell so `${PORT}` is expanded at runtime.
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]