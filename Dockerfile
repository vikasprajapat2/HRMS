FROM python:3.11-slim

# Prevent Python from writing .pyc files to disc and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies (kept minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    netcat-openbsd \
 && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# Expose port (Railway uses $PORT env var at runtime)
EXPOSE 5000

# Default command — use Gunicorn to run the Flask app (app:app)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
