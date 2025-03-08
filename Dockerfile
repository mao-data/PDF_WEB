# Build stage for React
FROM node:16-alpine AS frontend-build
WORKDIR /app/frontend
COPY src/package*.json ./
RUN npm install
COPY src/ ./
RUN npm run build

# Python application
FROM python:3.9-slim-buster
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libmupdf-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .
# Copy built React files from frontend-build
COPY --from=frontend-build /app/frontend/build ./build

# Create necessary directories with proper permissions
RUN mkdir -p uploads output \
    && chmod 777 uploads output

# Environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PORT=3000
ENV HOST=0.0.0.0

# Expose the port
EXPOSE 3000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/test || exit 1

# Start the application
CMD ["gunicorn", "--bind", "0.0.0.0:3000", "--workers=4", "--timeout=120", "app:app"] 