FROM python:3.11-slim

WORKDIR /app

# DIAGNOSTIC STEP: List files before copying to see what exists
RUN echo "Current files in /app:" && ls -R

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
# If this fails, the diagnostic step above will show you exactly what folders exist
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy everything else
COPY . .

EXPOSE 8000
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]
