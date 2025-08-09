# 🚀 Advanced Usage Examples

This guide demonstrates advanced filtering and configuration options for the Gmail Attachment Downloader.

## 📋 Quick Reference

### Environment Variables Summary

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `CREATE_SUBJECT_FOLDERS` | Boolean | Create folders by email subject | `true` / `false` |
| `DATE_FROM` | Date | Start date filter | `2024/01/01` |
| `DATE_TO` | Date | End date filter | `2024/12/31` |
| `SUBJECT_REGEX` | Regex | Subject line pattern | `.*invoice.*` |
| `FILENAME_REGEX` | Regex | Attachment filename pattern | `\.pdf$` |

## 🎯 Real-World Scenarios

### 1. Financial Document Collection

**Scenario**: Download all financial documents (invoices, statements, receipts) as PDFs from the last 6 months.

```bash
docker run -it --rm \
  -v $(pwd)/downloads:/app/downloads \
  -v $(pwd)/credentials:/app/credentials \
  -e DATE_FROM="2024/06/01" \
  -e SUBJECT_REGEX=".*(invoice|statement|receipt|bill).*" \
  -e FILENAME_REGEX="\.pdf$" \
  -e CREATE_SUBJECT_FOLDERS=true \
  ghcr.io/gaurav/gmail-downloader:latest
```

**Result**: Organized folders with PDF financial documents only.

### 2. Tax Document Preparation

**Scenario**: Collect all tax-related documents for 2024 tax year.

```bash
docker run -it --rm \
  -v $(pwd)/tax-docs-2024:/app/downloads \
  -v $(pwd)/credentials:/app/credentials \
  -e DATE_FROM="2024/01/01" \
  -e DATE_TO="2024/12/31" \
  -e SUBJECT_REGEX=".*(tax|1099|W-2|receipt|invoice|donation).*" \
  -e FILENAME_REGEX="\.(pdf|jpg|jpeg|png)$" \
  -e MAX_MESSAGES=500 \
  ghcr.io/gaurav/gmail-downloader:latest
```

### 3. Research Paper Collection

**Scenario**: Download academic papers and documents without folder organization.

```bash
docker run -it --rm \
  -v $(pwd)/research:/app/downloads \
  -v $(pwd)/credentials:/app/credentials \
  -e SEARCH_QUERY="has:attachment (paper OR research OR journal OR academic)" \
  -e FILENAME_REGEX="\.(pdf|docx?)$" \
  -e CREATE_SUBJECT_FOLDERS=false \
  -e MAX_MESSAGES=200 \
  ghcr.io/gaurav/gmail-downloader:latest
```

### 4. Photo Backup from Specific Senders

**Scenario**: Backup photos from family members sent in the last year.

```bash
docker run -it --rm \
  -v $(pwd)/family-photos:/app/downloads \
  -v $(pwd)/credentials:/app/credentials \
  -e SEARCH_QUERY="has:attachment from:(mom@email.com OR dad@email.com OR sister@email.com)" \
  -e DATE_FROM="2024/01/01" \
  -e FILENAME_REGEX="\.(jpg|jpeg|png|gif|bmp|tiff)$" \
  -e CREATE_SUBJECT_FOLDERS=true \
  ghcr.io/gaurav/gmail-downloader:latest
```

### 5. Business Expense Reports

**Scenario**: Download expense-related attachments from specific companies.

```bash
docker run -it --rm \
  -v $(pwd)/expenses:/app/downloads \
  -v $(pwd)/credentials:/app/credentials \
  -e SEARCH_QUERY="has:attachment from:*@company.com" \
  -e SUBJECT_REGEX=".*(expense|reimbursement|travel|receipt).*" \
  -e FILENAME_REGEX="\.(pdf|xlsx?|csv)$" \
  -e DATE_FROM="2024/01/01" \
  ghcr.io/gaurav/gmail-downloader:latest
```

### 6. Legal Document Archive

**Scenario**: Archive legal documents and contracts.

```bash
docker run -it --rm \
  -v $(pwd)/legal:/app/downloads \
  -v $(pwd)/credentials:/app/credentials \
  -e SUBJECT_REGEX=".*(contract|agreement|legal|court|lawyer|attorney).*" \
  -e FILENAME_REGEX="\.(pdf|docx?)$" \
  -e CREATE_SUBJECT_FOLDERS=true \
  -e MAX_MESSAGES=100 \
  ghcr.io/gaurav/gmail-downloader:latest
```

### 7. Software Downloads and Licenses

**Scenario**: Collect software downloads and license files.

```bash
docker run -it --rm \
  -v $(pwd)/software:/app/downloads \
  -v $(pwd)/credentials:/app/credentials \
  -e SUBJECT_REGEX=".*(license|software|download|activation|key).*" \
  -e FILENAME_REGEX="\.(zip|exe|dmg|pkg|lic|key|txt|pdf)$" \
  -e CREATE_SUBJECT_FOLDERS=false \
  ghcr.io/gaurav/gmail-downloader:latest
```

## 🔍 Advanced Regex Patterns

### Subject Regex Examples

```bash
# Exact match (case insensitive)
SUBJECT_REGEX="^Invoice.*$"

# Contains any of multiple terms
SUBJECT_REGEX=".*(urgent|important|action required).*"

# Starts with specific pattern
SUBJECT_REGEX="^(Re:|Fwd:).*invoice.*"

# Contains numbers (like invoice numbers)
SUBJECT_REGEX=".*[0-9]{6,}.*"

# Month-specific filtering
SUBJECT_REGEX=".*(January|February|March).*2024.*"
```

### Filename Regex Examples

```bash
# Specific file types
FILENAME_REGEX="\.(pdf|docx?|xlsx?)$"

# Images only
FILENAME_REGEX="\.(jpe?g|png|gif|bmp|tiff)$"

# Archive files
FILENAME_REGEX="\.(zip|rar|7z|tar\.gz)$"

# Files with specific naming patterns
FILENAME_REGEX=".*invoice.*\.(pdf|xlsx?)$"

# Files with dates in name (YYYY-MM-DD)
FILENAME_REGEX=".*[0-9]{4}-[0-9]{2}-[0-9]{2}.*"

# Exclude certain file types
FILENAME_REGEX="^(?!.*\.(tmp|log|cache)).*\.(pdf|docx?)$"
```

## 📊 Performance Optimization

### Large Mailbox Strategies

For mailboxes with thousands of messages:

```bash
# Process in batches
MAX_MESSAGES=50

# Use specific date ranges
DATE_FROM="2024/08/01"
DATE_TO="2024/08/31"

# Combine with specific senders
SEARCH_QUERY="has:attachment from:important@company.com"
```

### Memory-Efficient Processing

```bash
# Disable subject folders for flat structure
CREATE_SUBJECT_FOLDERS=false

# Limit message count
MAX_MESSAGES=25

# Use specific file type filters
FILENAME_REGEX="\.pdf$"
```

## 🐳 Docker Compose Examples

### Multi-Purpose Download Setup

```yaml
version: '3.8'
services:
  # Financial documents
  financial:
    image: ghcr.io/gaurav/gmail-downloader:latest
    environment:
      - DATE_FROM=2024/01/01
      - SUBJECT_REGEX=.*(invoice|statement|bill).*
      - FILENAME_REGEX=\.pdf$
      - CREATE_SUBJECT_FOLDERS=true
    volumes:
      - ./downloads/financial:/app/downloads
      - ./credentials:/app/credentials

  # Photos backup
  photos:
    image: ghcr.io/gaurav/gmail-downloader:latest
    environment:
      - SEARCH_QUERY=has:attachment from:family
      - FILENAME_REGEX=\.(jpg|jpeg|png)$
      - CREATE_SUBJECT_FOLDERS=false
    volumes:
      - ./downloads/photos:/app/downloads
      - ./credentials:/app/credentials

  # Documents archive
  documents:
    image: ghcr.io/gaurav/gmail-downloader:latest
    environment:
      - FILENAME_REGEX=\.(pdf|docx?|xlsx?)$
      - MAX_MESSAGES=200
    volumes:
      - ./downloads/documents:/app/downloads
      - ./credentials:/app/credentials
    profiles:
      - documents
```

Run specific services:
```bash
# Run financial documents download
docker-compose up financial

# Run all services
docker-compose up

# Run documents service
docker-compose --profile documents up documents
```

## 🔧 Troubleshooting Advanced Scenarios

### Debug Regex Patterns

Add debugging environment variable:
```bash
-e DEBUG_REGEX=true  # (if implemented)
```

### Check Filtering Results

The application reports:
- Messages processed
- Attachments downloaded
- Messages filtered out

### Common Issues

1. **No files downloaded with regex**: Check regex syntax
2. **Too many files**: Add more specific filters
3. **Date format errors**: Use YYYY/MM/DD format
4. **Permission errors**: Check volume mount permissions

### Testing Regex Patterns

Before running the full download, test regex patterns:

```bash
# Test with limited messages first
MAX_MESSAGES=5
```

## 📝 Best Practices

1. **Start Small**: Test with `MAX_MESSAGES=10` first
2. **Use Date Ranges**: Prevent overwhelming downloads
3. **Combine Filters**: Use both subject and filename filters
4. **Organize by Purpose**: Create separate download directories
5. **Regular Backups**: Archive downloaded files regularly
6. **Monitor Logs**: Check filtering statistics in output

---

**Happy advanced filtering! 🎯📧**