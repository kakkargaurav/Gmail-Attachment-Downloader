FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY main.py .

# Create directories
RUN mkdir -p /app/downloads /app/credentials

# Set environment variables with defaults
ENV DOWNLOAD_PATH=/app/downloads
ENV SEARCH_QUERY="has:attachment"
ENV MAX_MESSAGES=100
ENV GMAIL_CREDENTIALS_FILE=/app/credentials/credentials.json

# Expose port for OAuth callback (if needed)
EXPOSE 8080

# Run the application
CMD ["python", "main.py"]