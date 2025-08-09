# Gmail Attachment Downloader

A Python application that downloads all attachments from Gmail messages using the Gmail API. The application can run locally or in a Docker container with environment variable configuration.

[![Docker Build and Push](https://github.com/USERNAME/gmail-downloader/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/USERNAME/gmail-downloader/actions/workflows/docker-publish.yml)
[![Container Registry](https://ghcr.io/USERNAME/gmail-downloader)](https://github.com/USERNAME/gmail-downloader/pkgs/container/gmail-downloader)

## Features

- Download all attachments from Gmail messages
- **Advanced Filtering Options:**
  - Configurable search queries to filter messages
  - Date range filtering (DATE_FROM/DATE_TO)
  - Subject regex filtering for precise email matching
  - Attachment filename regex filtering
- OAuth2 authentication with Gmail API
- **Flexible Organization:**
  - Organized folder structure by email subjects (optional)
  - Direct download without folders (configurable)
- Docker containerization with multi-architecture support (amd64/arm64)
- GitHub Container Registry (GHCR) deployment
- Environment variable configuration
- Comprehensive logging with filtering statistics
- Resume capability with stored credentials
- Automated CI/CD with GitHub Actions

## Prerequisites

### For Local Development
- Python 3.8 or higher
- Gmail API credentials (OAuth2)

### For Docker
- Docker and Docker Compose
- Gmail API credentials (OAuth2)

## Setup Instructions

### 1. Gmail API Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API" and enable it
4. Create OAuth2 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Choose "Desktop Application" as the application type
   - Download the JSON file and save it as `credentials/credentials.json`

### 2. Project Structure

Create the following directory structure:

```
gmail-downloader/
├── main.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── README.md
├── credentials/
│   └── credentials.json  # Your OAuth2 credentials
├── downloads/            # Downloaded attachments will be stored here
└── logs/                # Application logs
```

### 3. Local Installation

```bash
# Clone or create the project directory
mkdir gmail-downloader
cd gmail-downloader

# Install Python dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env

# Edit .env file with your configuration
# Place your credentials.json file in the credentials/ directory
```

### 4. Docker Installation

#### Option A: Use Pre-built Image from GitHub Container Registry

```bash
# Pull the latest image
docker pull ghcr.io/USERNAME/gmail-downloader:latest

# Run the container
docker run -v $(pwd)/downloads:/app/downloads \
           -v $(pwd)/credentials:/app/credentials \
           -v $(pwd)/logs:/app/logs \
           -e SEARCH_QUERY="has:attachment" \
           -e MAX_MESSAGES=100 \
           -it ghcr.io/USERNAME/gmail-downloader:latest
```

#### Option B: Build Locally with Docker Compose

```bash
# Build and run with Docker Compose
docker-compose up --build
```

#### Option C: Build Manually

```bash
# Build and run manually
docker build -t gmail-downloader .
docker run -v $(pwd)/downloads:/app/downloads \
           -v $(pwd)/credentials:/app/credentials \
           -v $(pwd)/logs:/app/logs \
           -e DOWNLOAD_PATH=/app/downloads \
           -e SEARCH_QUERY="has:attachment" \
           -e MAX_MESSAGES=100 \
           -it gmail-downloader
```

## Configuration

### Required Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GMAIL_CREDENTIALS_FILE` | Path to OAuth2 credentials | `credentials/credentials.json` |
| `DOWNLOAD_PATH` | Download directory | `./downloads` |

### Basic Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `SEARCH_QUERY` | Gmail search query | `has:attachment` |
| `MAX_MESSAGES` | Maximum messages to process | `100` |
| `CREATE_SUBJECT_FOLDERS` | Create folders by email subject | `true` |

### Advanced Filtering Options

| Variable | Description | Example |
|----------|-------------|---------|
| `DATE_FROM` | Start date (YYYY/MM/DD) | `2024/01/01` |
| `DATE_TO` | End date (YYYY/MM/DD) | `2024/12/31` |
| `SUBJECT_REGEX` | Subject line regex filter | `.*invoice.*` |
| `FILENAME_REGEX` | Attachment filename regex | `\.(pdf\|xlsx?)$` |

### Configuration Examples

#### Download Only PDFs from 2024
```bash
DATE_FROM=2024/01/01
DATE_TO=2024/12/31
FILENAME_REGEX=\.pdf$
```

#### Download Invoices and Receipts
```bash
SUBJECT_REGEX=.*(invoice|receipt).*
CREATE_SUBJECT_FOLDERS=true
```

#### Download Office Documents Without Folders
```bash
FILENAME_REGEX=\.(pdf|doc|docx|xls|xlsx)$
CREATE_SUBJECT_FOLDERS=false
```

#### Filter by Sender and Date Range
```bash
SEARCH_QUERY=has:attachment from:accounts@company.com
DATE_FROM=2024/06/01
DATE_TO=2024/06/30
```

### Search Query Examples

**Basic Queries:**
- `has:attachment` - All messages with attachments
- `has:attachment from:example@gmail.com` - Attachments from specific sender
- `has:attachment subject:"Invoice"` - Attachments from messages with "Invoice" in subject
- `has:attachment larger:5M` - Attachments from messages larger than 5MB

**Advanced Combinations:**
- Date filtering is handled by `DATE_FROM`/`DATE_TO` environment variables
- Subject filtering is enhanced by `SUBJECT_REGEX` for precise pattern matching
- Filename filtering uses `FILENAME_REGEX` for attachment-specific filtering

**Example Configurations:**
```bash
# Financial documents from banks
SEARCH_QUERY="has:attachment from:noreply@bank.com"
SUBJECT_REGEX=".*(statement|invoice).*"
FILENAME_REGEX="\.pdf$"

# Recent presentations and documents
DATE_FROM="2024/01/01"
FILENAME_REGEX="\.(pptx?|docx?|xlsx?)$"

# Images from specific timeframe
DATE_FROM="2024/06/01"
DATE_TO="2024/06/30"
FILENAME_REGEX="\.(jpg|jpeg|png|gif)$"
```

## Usage

### Local Execution

```bash
python main.py
```

### Docker Execution

#### Using Pre-built Image from GHCR

```bash
# Using Docker directly with pre-built image
docker run -v $(pwd)/downloads:/app/downloads \
           -v $(pwd)/credentials:/app/credentials \
           -e SEARCH_QUERY="has:attachment" \
           ghcr.io/USERNAME/gmail-downloader:latest
```

#### Using Docker Compose (Local Build)

```bash
# Using Docker Compose
docker-compose up
```

#### Manual Docker Run (Local Build)

```bash
# Using Docker directly with locally built image
docker run -v $(pwd)/downloads:/app/downloads \
           -v $(pwd)/credentials:/app/credentials \
           gmail-downloader
```

### First-Time Authentication

On first run, the application will:
1. Open a browser window for Gmail authentication
2. Ask you to sign in to your Gmail account
3. Request permission to access your Gmail (read-only)
4. Save the authentication token for future use

## Output Structure

Downloaded attachments are organized as follows:

```
downloads/
├── Subject_Line_MessageID/
│   ├── attachment1.pdf
│   ├── attachment2.jpg
│   └── ...
├── Another_Subject_MessageID/
│   ├── document.docx
│   └── ...
└── ...
```

## Logging

The application creates detailed logs in:
- Console output (real-time)
- `gmail_downloader.log` file
- Docker logs (when running in container)

## Security Considerations

- OAuth2 credentials are stored in `token.pickle` after first authentication
- Never commit `credentials.json` or `token.pickle` to version control
- Use `.gitignore` to exclude sensitive files
- The application only requests read-only access to Gmail

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Ensure `credentials.json` is in the correct location
   - Check that Gmail API is enabled in Google Cloud Console
   - Verify OAuth2 client is configured as "Desktop Application"

2. **Permission Denied**
   - Make sure the application has read permissions for credentials directory
   - Check Docker volume mounts are correct

3. **No Attachments Downloaded**
   - Verify your search query matches messages with attachments
   - Check the Gmail account has messages matching the query
   - Increase `MAX_MESSAGES` if needed

4. **Docker Container Exits**
   - Check logs with `docker-compose logs`
   - Ensure all required files are mounted correctly
   - Verify environment variables are set

### Debug Mode

Enable verbose logging by modifying the logging level in `main.py`:

```python
logging.basicConfig(level=logging.DEBUG, ...)
```

## Development

### Running Tests

```bash
# Install development dependencies
pip install pytest pytest-mock

# Run tests (create test files as needed)
pytest
```

### Building and Publishing Docker Image

#### Automated Publishing via GitHub Actions

The repository includes a GitHub Actions workflow that automatically builds and publishes multi-architecture Docker images to GitHub Container Registry on:
- Push to `main`/`master` branch
- Creation of version tags (e.g., `v1.0.0`)
- Pull requests (for testing)

#### Manual Publishing to GHCR

```bash
# Windows (PowerShell)
.\push-to-ghcr.ps1 YOUR_GITHUB_USERNAME v1.0.0

# Linux/macOS (Bash)
chmod +x push-to-ghcr.sh
./push-to-ghcr.sh YOUR_GITHUB_USERNAME v1.0.0
```

#### Custom Registry Publishing

```bash
# Build with custom tag
docker build -t my-gmail-downloader:latest .

# Push to custom registry
docker tag my-gmail-downloader:latest your-registry/gmail-downloader:latest
docker push your-registry/gmail-downloader:latest
```

### GitHub Container Registry Setup

1. Create a Personal Access Token with `package:write` permissions
2. Enable GitHub Actions in your repository
3. The workflow will automatically build and publish on push to main branch
4. Images are available at `ghcr.io/YOUR_USERNAME/gmail-downloader`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## 📚 Additional Resources

- [QUICKSTART.md](QUICKSTART.md) - Get running in 5 minutes
- [ADVANCED_EXAMPLES.md](ADVANCED_EXAMPLES.md) - Real-world filtering scenarios
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment guide
- [Gmail Search Operators](https://support.google.com/mail/answer/7190?hl=en)
- [Google Cloud Console](https://console.cloud.google.com/)
- [Regular Expressions Guide](https://regexr.com/) - Test and learn regex patterns

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the Gmail API documentation
3. Create an issue in the project repository

## Changelog

### v2.0.0 - Enhanced Filtering & Organization
- **🎯 Advanced Filtering**: Date range filtering with `DATE_FROM`/`DATE_TO`
- **🔍 Regex Support**: Subject and filename regex pattern matching
- **📁 Flexible Organization**: Optional subject folder creation via `CREATE_SUBJECT_FOLDERS`
- **📊 Enhanced Logging**: Filtering statistics and improved reporting
- **📖 Comprehensive Documentation**: QUICKSTART.md and ADVANCED_EXAMPLES.md guides
- **🔧 Production Ready**: Enhanced configuration options for enterprise use

### v1.0.0 - Initial Release
- Initial release with core functionality
- OAuth2 authentication
- Basic attachment download functionality
- Docker containerization with multi-architecture support
- GitHub Container Registry integration
- GitHub Actions CI/CD pipeline
- Environment variable configuration
- Comprehensive logging
- Manual and automated deployment scripts