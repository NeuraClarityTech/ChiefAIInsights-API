FROM python:3.11-slim

WORKDIR /app

# Install system dependencies needed for compilation
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    cargo \
    rustc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY ChiefAIInsights-API-V2/requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ChiefAIInsights-API-V2/backend ./backend

# Expose the port
EXPOSE 10000

# Set environment variable for Python
ENV PYTHONUNBUFFERED=1

# Start command
CMD cd backend && gunicorn main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-10000} --workers 1 --timeout 120
