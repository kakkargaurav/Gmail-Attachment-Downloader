# 🚀 Quick Start Guide

Get up and running with Gmail Attachment Downloader in minutes!

## 📋 Prerequisites

- Docker installed on your system
- Gmail account with API access
- GitHub account (for GHCR access)

## ⚡ Quick Setup (Using Pre-built Image)

### 1. Create Project Directory

```bash
mkdir gmail-downloader-setup
cd gmail-downloader-setup
mkdir credentials downloads logs
```

### 2. Get Gmail API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project and enable Gmail API
3. Create OAuth2 credentials (Desktop Application)
4. Download as `credentials/credentials.json`

### 3. Run with Pre-built Image

```bash
# Pull and run the latest image
docker run -it --rm \
  --name gmail-downloader \
  -v $(pwd)/downloads:/app/downloads \
  -v $(pwd)/credentials:/app/credentials \
  -v $(pwd)/logs:/app/logs \
  -e SEARCH_QUERY="has:attachment" \
  -e MAX_MESSAGES=50 \
  -e CREATE_SUBJECT_FOLDERS=true \
  ghcr.io/gaurav/gmail-downloader:latest
```

### 4. First-Time Authentication

- The application will open a browser for Gmail OAuth
- Sign in and grant permissions
- Authentication token will be saved for future use

## 🐳 Alternative: Using Docker Compose

### 1. Create docker-compose.yml

```yaml
version: '3.8'
services:
  gmail-downloader:
    image: ghcr.io/gaurav/gmail-downloader:latest
    container_name: gmail-downloader
    environment:
      - SEARCH_QUERY=has:attachment
      - MAX_MESSAGES=100
      - DOWNLOAD_PATH=/app/downloads
      - GMAIL_CREDENTIALS_FILE=/app/credentials/credentials.json
      - CREATE_SUBJECT_FOLDERS=true
      # Advanced filtering options
      # - DATE_FROM=2024/01/01
      # - DATE_TO=2024/12/31
      # - SUBJECT_REGEX=.*invoice.*
      # - FILENAME_REGEX=\.(pdf|xlsx?)$
    volumes:
      - ./downloads:/app/downloads
      - ./credentials:/app/credentials
      - ./logs:/app/logs
    stdin_open: true
    tty: true
```

### 2. Run

```bash
docker-compose up
```

## 🔧 Configuration Options

### Basic Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SEARCH_QUERY` | Gmail search filter | `has:attachment` |
| `MAX_MESSAGES` | Max messages to process | `100` |
| `DOWNLOAD_PATH` | Download directory | `/app/downloads` |
| `CREATE_SUBJECT_FOLDERS` | Create folders by subject | `true` |

### Advanced Filtering Options

| Variable | Description | Example |
|----------|-------------|---------|
| `DATE_FROM` | Start date (YYYY/MM/DD) | `2024/01/01` |
| `DATE_TO` | End date (YYYY/MM/DD) | `2024/12/31` |
| `SUBJECT_REGEX` | Subject regex filter | `.*invoice.*` |
| `FILENAME_REGEX` | Filename regex filter | `\.(pdf\|xlsx?)$` |

### Quick Examples

```bash
# Download only PDFs from 2024
-e DATE_FROM="2024/01/01" \
-e DATE_TO="2024/12/31" \
-e FILENAME_REGEX="\.pdf$"

# Download invoices without subject folders
-e SUBJECT_REGEX=".*invoice.*" \
-e CREATE_SUBJECT_FOLDERS=false

# Download recent office documents
-e DATE_FROM="2024/06/01" \
-e FILENAME_REGEX="\.(pdf|doc|docx|xls|xlsx)$"

# Download from specific sender with date range
-e SEARCH_QUERY="has:attachment from:billing@company.com" \
-e DATE_FROM="2024/01/01"
```

### Common Search Queries

```bash
# All attachments
SEARCH_QUERY="has:attachment"

# From specific sender
SEARCH_QUERY="has:attachment from:sender@example.com"

# With specific subject (basic Gmail search)
SEARCH_QUERY="has:attachment subject:Invoice"

# Larger than 5MB
SEARCH_QUERY="has:attachment larger:5M"

# Note: For precise filtering, use regex environment variables
# instead of complex Gmail search queries
```

## 📁 Output Structure

```
downloads/
├── Subject_Line_MessageID/
│   ├── attachment1.pdf
│   ├── attachment2.jpg
│   └── ...
└── Another_Subject_MessageID/
    └── document.docx
```

## 🛠️ Troubleshooting

### Common Issues

**Authentication Failed**
- Ensure `credentials.json` is in the credentials directory
- Check Gmail API is enabled in Google Cloud Console

**No Attachments Downloaded**
- Verify your Gmail account has messages with attachments
- Try a broader search query like `has:attachment`
- Increase `MAX_MESSAGES` if needed

**Permission Denied**
- Check volume mount permissions
- Ensure Docker has access to the directories

### Debug Commands

```bash
# Check container logs
docker logs gmail-downloader

# Access container shell
docker exec -it gmail-downloader /bin/bash

# Test Gmail API connectivity
docker exec gmail-downloader python -c "from googleapiclient.discovery import build; print('OK')"
```

## 🎯 Next Steps

1. **Customize Search**: Modify `SEARCH_QUERY` for specific needs
2. **Automate**: Set up scheduled runs with cron or task scheduler  
3. **Monitor**: Check logs in the `logs/` directory
4. **Scale**: Deploy to cloud platforms for larger operations

## 📚 Additional Resources

- [README.md](README.md) - Complete documentation
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment options
- [Gmail Search Operators](https://support.google.com/mail/answer/7190?hl=en)
- [Google Cloud Console](https://console.cloud.google.com/)

## 🆘 Support

Having issues? 
1. Check the troubleshooting section above
2. Review container logs: `docker logs gmail-downloader`
3. Verify your OAuth2 credentials setup
4. Test with a simple search query first

---

**Happy downloading! 📧📎**