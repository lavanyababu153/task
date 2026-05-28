# Stage 1: Build the frontend
FROM node:22-alpine AS build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Final image (Python/Django)
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies (needed to run gunicorn/python)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY . .

# Copy built frontend into the Django static directory
# Ensure your Django settings.py points to this directory for STATICFILES_DIRS
COPY --from=build /app/frontend/dist ./frontend/dist

# Expose the port Railway expects
EXPOSE 8000

# Start Gunicorn, binding to the $PORT provided by Railway
# Note: ${PORT:-8000} uses the Railway port, defaulting to 8000 if not set
CMD gunicorn your_project_name.wsgi:application --bind 0.0.0.0:${PORT:-8000}