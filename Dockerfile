FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies for WeasyPrint PDF generation
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    libcairo2-dev \
    libpango1.0-dev \
    libgdk-pixbuf2.0-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libjpeg-dev \
    libfreetype6-dev \
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
ENV DOWNLOAD_EMAIL_IF_NO_ATTACHMENT=false

# Expose port for OAuth callback (if needed)
EXPOSE 8080

# Run the application
CMD ["python", "main.py"]