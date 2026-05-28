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
# Install system dependencies
RUN apt-get update && apt-get install -y nodejs npm
# Copy backend code
COPY . .
# Copy built frontend into the Django static directory
COPY --from=build /app/frontend/dist ./frontend/dist

# Install python dependencies
RUN pip install -r requirements.txt
CMD ["gunicorn", "your_project_name.wsgi:application", "--bind", "0.0.0.0:8000"]