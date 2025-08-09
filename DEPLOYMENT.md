# Deployment Guide

This guide covers different deployment options for the Gmail Attachment Downloader.

## 📦 GitHub Container Registry (GHCR)

### Automated Deployment

The repository includes GitHub Actions that automatically build and push images to GHCR:

- **Triggers**: Push to main branch, version tags (v*), pull requests
- **Architectures**: linux/amd64, linux/arm64
- **Registry**: `ghcr.io/USERNAME/gmail-downloader`

### Manual Deployment

#### Prerequisites

1. GitHub Personal Access Token with `package:write` permissions
2. Docker installed locally

#### Windows (PowerShell)

```powershell
# Make script executable and run
.\push-to-ghcr.ps1 YOUR_GITHUB_USERNAME v1.0.0
```

#### Linux/macOS (Bash)

```bash
# Make script executable
chmod +x push-to-ghcr.sh

# Run the script
./push-to-ghcr.sh YOUR_GITHUB_USERNAME v1.0.0
```

#### Manual Steps

```bash
# 1. Build the image
docker build -t ghcr.io/USERNAME/gmail-downloader:latest .

# 2. Login to GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# 3. Push the image
docker push ghcr.io/USERNAME/gmail-downloader:latest
```

## 🐳 Docker Deployment Options

### Option 1: Pre-built Image from GHCR

```bash
# Pull and run
docker pull ghcr.io/USERNAME/gmail-downloader:latest
docker run -d \
  --name gmail-downloader \
  -v $(pwd)/downloads:/app/downloads \
  -v $(pwd)/credentials:/app/credentials \
  -e SEARCH_QUERY="has:attachment" \
  -e MAX_MESSAGES=100 \
  ghcr.io/USERNAME/gmail-downloader:latest
```

### Option 2: Docker Compose with Pre-built Image

```bash
# Use the GHCR profile
docker-compose --profile ghcr up -d gmail-downloader-ghcr
```

### Option 3: Local Build with Docker Compose

```bash
# Standard docker-compose (builds locally)
docker-compose up -d
```

### Option 4: Local Build Manual

```bash
# Build locally
docker build -t gmail-downloader .

# Run container
docker run -d \
  --name gmail-downloader \
  -v $(pwd)/downloads:/app/downloads \
  -v $(pwd)/credentials:/app/credentials \
  -e SEARCH_QUERY="has:attachment" \
  gmail-downloader
```

## ☁️ Cloud Deployment

### Google Cloud Run

```bash
# Deploy to Cloud Run
gcloud run deploy gmail-downloader \
  --image ghcr.io/USERNAME/gmail-downloader:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="SEARCH_QUERY=has:attachment,MAX_MESSAGES=100"
```

### AWS ECS

1. Create ECS task definition using the GHCR image
2. Set environment variables for configuration
3. Mount EFS volumes for persistent storage
4. Deploy using ECS service

### Azure Container Instances

```bash
# Deploy to Azure Container Instances
az container create \
  --resource-group myResourceGroup \
  --name gmail-downloader \
  --image ghcr.io/USERNAME/gmail-downloader:latest \
  --environment-variables SEARCH_QUERY="has:attachment" MAX_MESSAGES=100 \
  --azure-file-volume-account-name mystorageaccount \
  --azure-file-volume-account-key $STORAGE_KEY \
  --azure-file-volume-share-name gmail-downloads \
  --azure-file-volume-mount-path /app/downloads
```

## 🔧 Configuration

### Required Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GMAIL_CREDENTIALS_FILE` | Path to OAuth2 credentials | `/app/credentials/credentials.json` |
| `DOWNLOAD_PATH` | Download directory | `/app/downloads` |

### Optional Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SEARCH_QUERY` | Gmail search query | `has:attachment` |
| `MAX_MESSAGES` | Maximum messages to process | `100` |

### Volume Mounts

| Host Path | Container Path | Description |
|-----------|----------------|-------------|
| `./credentials` | `/app/credentials` | OAuth2 credentials |
| `./downloads` | `/app/downloads` | Downloaded attachments |
| `./logs` | `/app/logs` | Application logs |

## 🔐 Security Considerations

### Credentials Management

- **Never commit** `credentials.json` to version control
- Use Docker secrets or environment variables in production
- Rotate OAuth2 tokens regularly
- Use least-privilege permissions

### Network Security

- Run containers in private networks when possible
- Use HTTPS for all external communications
- Implement proper firewall rules
- Monitor container logs for security events

### Container Security

```bash
# Run as non-root user (add to Dockerfile)
USER 1000:1000

# Use read-only filesystem
docker run --read-only \
  --tmpfs /tmp \
  --tmpfs /app/logs \
  ghcr.io/USERNAME/gmail-downloader:latest
```

## 📊 Monitoring and Logging

### Health Checks

```bash
# Add health check to docker-compose.yml
healthcheck:
  test: ["CMD", "python", "-c", "import sys; sys.exit(0)"]
  interval: 30s
  timeout: 10s
  retries: 3
```

### Log Management

```bash
# Configure Docker logging
docker run \
  --log-driver json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  ghcr.io/USERNAME/gmail-downloader:latest
```

### Monitoring Tools

- **Prometheus**: Container metrics
- **Grafana**: Visualization dashboards  
- **ELK Stack**: Log aggregation and analysis
- **Docker Stats**: Real-time resource usage

## 🚀 Production Deployment Checklist

- [ ] OAuth2 credentials configured
- [ ] Environment variables set
- [ ] Volume mounts configured
- [ ] Network security implemented
- [ ] Health checks configured
- [ ] Logging configured
- [ ] Monitoring setup
- [ ] Backup strategy defined
- [ ] Update strategy planned
- [ ] Documentation updated

## 🔄 Update Strategy

### Rolling Updates

```bash
# Pull latest image
docker pull ghcr.io/USERNAME/gmail-downloader:latest

# Update with zero downtime
docker-compose up -d --no-deps gmail-downloader
```

### Blue-Green Deployment

```bash
# Deploy to staging environment
docker-compose -f docker-compose.staging.yml up -d

# Switch traffic after validation
# Update production configuration
```

## 📞 Support

For deployment issues:
1. Check container logs: `docker logs gmail-downloader`
2. Verify environment variables: `docker exec gmail-downloader env`
3. Test network connectivity: `docker exec gmail-downloader ping gmail.googleapis.com`
4. Review OAuth2 setup in credentials/README.txt