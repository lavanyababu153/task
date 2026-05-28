# 1. Use an official lightweight Python image
FROM python:3.11-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Prevent Python from writing pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 4. Install system dependencies required for psycopg2 (PostgreSQL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. Copy the requirements file from the backend folder
COPY backend/requirements.txt .

# 6. Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 7. Copy the rest of your project files into the container
COPY . .

# 8. Expose the port your app runs on
EXPOSE 8000

# 9. Command to start the application (Update this to your actual entry point)
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]
