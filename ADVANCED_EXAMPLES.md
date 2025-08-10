# 🚀 Advanced Usage Examples

This guide demonstrates advanced filtering and configuration options for the Gmail Attachment Downloader and Email-to-PDF converter.

## 📋 Quick Reference

### Environment Variables Summary

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `CREATE_SUBJECT_FOLDERS` | Boolean | Create folders by email subject | `true` / `false` |
| `DOWNLOAD_EMAIL_IF_NO_ATTACHMENT` | Boolean | Convert emails to PDF | `true` / `false` |
| `DEBUG_LOGGING` | Boolean | Enable detailed logging | `true` / `false` |
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

### 8. Newsletter and Email Archival

**Scenario**: Convert newsletters, notifications, and important emails to searchable PDFs.

```bash
docker run -it --rm \
  -v $(pwd)/email-archive:/app/downloads \
  -v $(pwd)/credentials:/app/credentials \
  -e DOWNLOAD_EMAIL_IF_NO_ATTACHMENT=true \
  -e SEARCH_QUERY="from:(newsletter@company.com OR notifications@service.com)" \
  -e DATE_FROM="2024/01/01" \
  -e CREATE_SUBJECT_FOLDERS=true \
  -e DEBUG_LOGGING=true \
  ghcr.io/gaurav/gmail-downloader:latest
```

### 9. Complete Email Backup Solution

**Scenario**: Download attachments AND convert emails to PDF for complete backup.

```bash
docker run -it --rm \
  -v $(pwd)/complete-backup:/app/downloads \
  -v $(pwd)/credentials:/app/credentials \
  -e DOWNLOAD_EMAIL_IF_NO_ATTACHMENT=true \
  -e SUBJECT_REGEX=".*(important|urgent|receipt|invoice).*" \
  -e DATE_FROM="2024/01/01" \
  -e MAX_MESSAGES=1000 \
  -e DEBUG_LOGGING=true \
  ghcr.io/gaurav/gmail-downloader:latest
```

### 10. Legal and Compliance Archive

**Scenario**: Archive all emails from specific domains as PDFs for compliance.

```bash
docker run -it --rm \
  -v $(pwd)/compliance:/app/downloads \
  -v $(pwd)/credentials:/app/credentials \
  -e DOWNLOAD_EMAIL_IF_NO_ATTACHMENT=true \
  -e SEARCH_QUERY="from:*@legal-firm.com OR from:*@court.gov" \
  -e CREATE_SUBJECT_FOLDERS=true \
  -e MAX_MESSAGES=500 \
  ghcr.io/gaurav/gmail-downloader:latest
```

### 11. Newsletter and Content Archive

**Scenario**: Convert specific newsletters to readable PDFs without search restrictions.

```bash
docker run -it --rm \
  -v $(pwd)/newsletters:/app/downloads \
  -v $(pwd)/credentials:/app/credentials \
  -e DOWNLOAD_EMAIL_IF_NO_ATTACHMENT=true \
  -e SEARCH_QUERY="from:weekly@newsletter.com" \
  -e SUBJECT_REGEX="" \
  -e CREATE_SUBJECT_FOLDERS=false \
  -e DEBUG_LOGGING=true \
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

## 📄 Email-to-PDF Advanced Patterns

### Email-to-PDF with Smart Filtering

```bash
# Archive all emails from specific timeframe as PDFs
DOWNLOAD_EMAIL_IF_NO_ATTACHMENT=true
SEARCH_QUERY=""  # Remove attachment requirement
DATE_FROM="2024/06/01"
DATE_TO="2024/06/30"
SUBJECT_REGEX=".*(meeting|agenda|summary).*"

# Convert marketing emails to PDFs for review
DOWNLOAD_EMAIL_IF_NO_ATTACHMENT=true
SEARCH_QUERY="from:(marketing@company.com OR promo@service.com)"
CREATE_SUBJECT_FOLDERS=false
DEBUG_LOGGING=true

# Backup important notifications as PDFs
DOWNLOAD_EMAIL_IF_NO_ATTACHMENT=true
SUBJECT_REGEX=".*(alert|notification|security|backup).*"
DATE_FROM="2024/01/01"
MAX_MESSAGES=200
```

### Combined Attachment and Email Processing

```bash
# Process everything - attachments AND email content
DOWNLOAD_EMAIL_IF_NO_ATTACHMENT=true
SEARCH_QUERY="from:support@company.com"  # Don't include has:attachment
SUBJECT_REGEX=".*(ticket|support|issue).*"
FILENAME_REGEX="\.(pdf|png|log)$"
CREATE_SUBJECT_FOLDERS=true

# Archive financial communications completely
DOWNLOAD_EMAIL_IF_NO_ATTACHMENT=true
SEARCH_QUERY="from:*@bank.com"
SUBJECT_REGEX=".*(statement|transaction|alert).*"
DATE_FROM="2024/01/01"
```

### PDF Generation Troubleshooting

```bash
# Enable detailed PDF generation logging
DEBUG_LOGGING=true
DOWNLOAD_EMAIL_IF_NO_ATTACHMENT=true
MAX_MESSAGES=5  # Start small for testing

# Test PDF conversion with simple emails
DOWNLOAD_EMAIL_IF_NO_ATTACHMENT=true
SEARCH_QUERY="from:noreply@github.com"
DEBUG_LOGGING=true
MAX_MESSAGES=3
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

  # Email archive as PDFs
  email-archive:
    image: ghcr.io/gaurav/gmail-downloader:latest
    environment:
      - DOWNLOAD_EMAIL_IF_NO_ATTACHMENT=true
      - SEARCH_QUERY=from:newsletter@company.com
      - DATE_FROM=2024/01/01
      - CREATE_SUBJECT_FOLDERS=true
      - DEBUG_LOGGING=true
    volumes:
      - ./downloads/emails:/app/downloads
      - ./credentials:/app/credentials

  # Complete backup (attachments + emails)
  complete-backup:
    image: ghcr.io/gaurav/gmail-downloader:latest
    environment:
      - DOWNLOAD_EMAIL_IF_NO_ATTACHMENT=true
      - SUBJECT_REGEX=.*(important|urgent|invoice).*
      - DATE_FROM=2024/01/01
      - MAX_MESSAGES=500
      - DEBUG_LOGGING=true
    volumes:
      - ./downloads/complete:/app/downloads
      - ./credentials:/app/credentials
    profiles:
      - backup

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

# Run complete backup
docker-compose --profile backup up complete-backup

# Run email archive
docker-compose up email-archive
```

## 🔧 Troubleshooting Advanced Scenarios

### Debug Regex Patterns

Enable detailed logging for troubleshooting:
```bash
-e DEBUG_LOGGING=true
```

Test PDF generation:
```bash
# Test email-to-PDF with small sample
-e DOWNLOAD_EMAIL_IF_NO_ATTACHMENT=true
-e DEBUG_LOGGING=true
-e MAX_MESSAGES=3
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
5. **PDF generation fails**: Check `DEBUG_LOGGING=true` for detailed errors
6. **Empty PDFs**: Some encrypted emails may not convert properly
7. **Missing email content**: Ensure emails have readable HTML or text content

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
7. **Test Email-to-PDF**: Enable `DEBUG_LOGGING=true` when testing PDF conversion
8. **Smart Search Queries**: Remove `has:attachment` when using `DOWNLOAD_EMAIL_IF_NO_ATTACHMENT=true`
9. **PDF Review**: Generated PDFs include metadata and professional formatting
10. **Performance**: Large email processing may take time - use date ranges for efficiency

## 📄 Email-to-PDF Best Practices

### When to Use Email-to-PDF

- **Newsletter archival**: Convert marketing emails to readable PDFs
- **Compliance**: Archive business communications as searchable documents
- **Important notifications**: Preserve system alerts and notifications
- **Meeting summaries**: Convert email meeting notes to PDF format
- **Legal communications**: Archive legal correspondence permanently

### PDF Output Quality

Generated PDFs include:
- Professional CSS styling and formatting
- Email metadata (From, To, Date, Subject)
- Proper HTML rendering with images (where supported)
- Generated signature for document authenticity
- Searchable text content for easy retrieval

### Performance Considerations

```bash
# Process large email volumes efficiently
DOWNLOAD_EMAIL_IF_NO_ATTACHMENT=true
DATE_FROM="2024/08/01"
DATE_TO="2024/08/31"  # One month at a time
MAX_MESSAGES=100      # Reasonable batch size
DEBUG_LOGGING=false   # Disable for production runs
```

---

**Happy advanced filtering! 🎯📧**