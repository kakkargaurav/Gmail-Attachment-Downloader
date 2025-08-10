#!/usr/bin/env python3
"""
Gmail Attachment Downloader

This application downloads all attachments from Gmail messages using the Gmail API.
It supports OAuth2 authentication and can run in a Docker container.
"""

import os
import sys
import json
import base64
import logging
import re
import html
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# PDF generation imports
try:
    from weasyprint import HTML, CSS
    from bs4 import BeautifulSoup
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    logger = logging.getLogger(__name__)
    logger.warning("PDF generation libraries not installed. Email-to-PDF functionality will be disabled.")

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('gmail_downloader.log')
    ]
)
logger = logging.getLogger(__name__)


class GmailDownloader:
    """Gmail attachment downloader class."""
    
    def __init__(self, download_path: str = './downloads', create_subject_folders: bool = True,
                 download_email_if_no_attachment: bool = False):
        """Initialize the Gmail downloader.
        
        Args:
            download_path: Path where attachments will be saved
            create_subject_folders: Whether to create folders based on email subjects
            download_email_if_no_attachment: Whether to download email content as PDF if no attachments
        """
        self.download_path = Path(download_path)
        self.download_path.mkdir(parents=True, exist_ok=True)
        self.create_subject_folders = create_subject_folders
        self.download_email_if_no_attachment = download_email_if_no_attachment
        self.service = None
        self.credentials = None
        
    def authenticate(self) -> bool:
        """Authenticate with Gmail API using OAuth2.
        
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            # Check for existing credentials
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    self.credentials = pickle.load(token)
            
            # If there are no valid credentials available, get new ones
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    logger.info("Refreshing expired credentials...")
                    self.credentials.refresh(Request())
                else:
                    # Check if we have credentials file
                    creds_file = os.getenv('GMAIL_CREDENTIALS_FILE', 'credentials/credentials.json')
                    if not os.path.exists(creds_file):
                        logger.error(f"Credentials file {creds_file} not found!")
                        logger.info("Please place your OAuth2 credentials file at: credentials/credentials.json")
                        logger.info("See credentials/README.txt for setup instructions")
                        return False
                    
                    logger.info("Starting OAuth2 flow...")
                    flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
                    self.credentials = flow.run_local_server(port=0)
                
                # Save credentials for next run
                with open('token.pickle', 'wb') as token:
                    pickle.dump(self.credentials, token)
            
            # Build the Gmail service
            self.service = build('gmail', 'v1', credentials=self.credentials)
            logger.info("Successfully authenticated with Gmail API")
            return True
            
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            return False
    
    def build_search_query(self, base_query: str = '', date_from: str = '', date_to: str = '',
                          subject_regex: str = '') -> str:
        """Build Gmail search query with filters.
        
        Args:
            base_query: Base search query (e.g., 'has:attachment')
            date_from: Start date in YYYY/MM/DD format
            date_to: End date in YYYY/MM/DD format
            subject_regex: Subject filter (will be converted to Gmail search format)
            
        Returns:
            Complete search query string
        """
        query_parts = []
        
        if base_query:
            # If download_email_if_no_attachment is enabled, remove has:attachment requirement
            if self.download_email_if_no_attachment and 'has:attachment' in base_query:
                # Remove has:attachment and any leading/trailing whitespace
                modified_query = base_query.replace('has:attachment', '').strip()
                if modified_query:  # Only add if there's still content
                    query_parts.append(modified_query)
            else:
                query_parts.append(base_query)
        
        if date_from:
            try:
                # Validate date format
                datetime.strptime(date_from, '%Y/%m/%d')
                query_parts.append(f"after:{date_from}")
            except ValueError:
                logger.warning(f"Invalid DATE_FROM format: {date_from}. Expected YYYY/MM/DD")
        
        if date_to:
            try:
                # Validate date format
                datetime.strptime(date_to, '%Y/%m/%d')
                query_parts.append(f"before:{date_to}")
            except ValueError:
                logger.warning(f"Invalid DATE_TO format: {date_to}. Expected YYYY/MM/DD")
        
        if subject_regex:
            # For Gmail search, we'll use simple contains search
            # Regex filtering will be applied post-retrieval
            # Remove common regex characters for basic Gmail search
            simple_subject = re.sub(r'[.*+?^${}()|[\]\\]', '', subject_regex)
            if simple_subject:
                query_parts.append(f'subject:"{simple_subject}"')
        
        return ' '.join(query_parts)

    def get_messages(self, query: str = '', max_results: int = 100) -> List[Dict[str, Any]]:
        """Get Gmail messages with pagination support.
        
        Args:
            query: Gmail search query (e.g., 'has:attachment')
            max_results: Maximum number of messages to retrieve
            
        Returns:
            List of message dictionaries
        """
        try:
            logger.info(f"Searching for messages with query: '{query}', max_results: {max_results}")
            messages = []
            next_page_token = None
            total_fetched = 0
            
            while total_fetched < max_results:
                # Gmail API limits maxResults to 500 per request
                batch_size = min(500, max_results - total_fetched)
                
                logger.debug(f"Fetching batch of {batch_size} messages (total so far: {total_fetched})")
                
                result = self.service.users().messages().list(
                    userId='me',
                    q=query,
                    maxResults=batch_size,
                    pageToken=next_page_token
                ).execute()
                
                batch_messages = result.get('messages', [])
                messages.extend(batch_messages)
                total_fetched += len(batch_messages)
                
                logger.info(f"Fetched {len(batch_messages)} messages in this batch (total: {total_fetched})")
                
                # Check if there are more pages
                next_page_token = result.get('nextPageToken')
                if not next_page_token:
                    logger.info("No more pages available")
                    break
                    
                # If we got fewer messages than requested in this batch, we've reached the end
                if len(batch_messages) < batch_size:
                    logger.info("Reached end of available messages")
                    break
            
            logger.info(f"Total messages retrieved: {len(messages)}")
            return messages
            
        except HttpError as error:
            logger.error(f"An error occurred while getting messages: {error}")
            return []
    
    def get_message_details(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific message.
        
        Args:
            message_id: Gmail message ID
            
        Returns:
            Message details dictionary or None if error
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id
            ).execute()
            return message
            
        except HttpError as error:
            logger.error(f"An error occurred while getting message details: {error}")
            return None
    
    def download_attachment(self, message_id: str, attachment_id: str, filename: str) -> bool:
        """Download a specific attachment.
        
        Args:
            message_id: Gmail message ID
            attachment_id: Gmail attachment ID
            filename: Name to save the file as
            
        Returns:
            True if download successful, False otherwise
        """
        try:
            attachment = self.service.users().messages().attachments().get(
                userId='me',
                messageId=message_id,
                id=attachment_id
            ).execute()
            
            file_data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))
            file_path = self.download_path / filename
            
            # Create subdirectory if filename contains path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            logger.info(f"Downloaded attachment: {filename} ({len(file_data)} bytes)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download attachment {filename}: {str(e)}")
            return False
    
    def extract_email_content(self, message: Dict[str, Any]) -> Dict[str, str]:
        """Extract email content and metadata from Gmail message.
        
        Args:
            message: Gmail message dictionary
            
        Returns:
            Dictionary containing email content and metadata
        """
        headers = message.get('payload', {}).get('headers', [])
        
        # Extract headers
        subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
        from_addr = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown Sender')
        to_addr = next((h['value'] for h in headers if h['name'].lower() == 'to'), 'Unknown Recipient')
        date_header = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')
        
        # Extract email body
        body_html = ''
        body_text = ''
        
        def extract_body_parts(parts):
            nonlocal body_html, body_text
            
            for part in parts:
                mime_type = part.get('mimeType', '')
                
                if mime_type == 'text/plain' and part.get('body', {}).get('data'):
                    body_text = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                elif mime_type == 'text/html' and part.get('body', {}).get('data'):
                    body_html = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                elif 'parts' in part:
                    extract_body_parts(part['parts'])
        
        # Extract body content
        payload = message.get('payload', {})
        if payload.get('parts'):
            extract_body_parts(payload['parts'])
        elif payload.get('body', {}).get('data'):
            # Simple message without parts
            mime_type = payload.get('mimeType', '')
            body_data = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
            if mime_type == 'text/html':
                body_html = body_data
            else:
                body_text = body_data
        
        return {
            'subject': subject,
            'from': from_addr,
            'to': to_addr,
            'date': date_header,
            'body_html': body_html,
            'body_text': body_text
        }
    
    def format_email_as_html(self, content: Dict[str, str]) -> str:
        """Format email content as HTML for PDF generation.
        
        Args:
            content: Dictionary containing email content and metadata
            
        Returns:
            Formatted HTML string
        """
        # Clean and escape content
        subject = html.escape(content.get('subject', 'No Subject'))
        from_addr = html.escape(content.get('from', 'Unknown Sender'))
        to_addr = html.escape(content.get('to', 'Unknown Recipient'))
        date_str = html.escape(content.get('date', ''))
        
        # Use HTML content if available, otherwise convert text to HTML
        body_content = content.get('body_html', '')
        if not body_content and content.get('body_text'):
            # Convert plain text to HTML
            body_content = html.escape(content['body_text']).replace('\n', '<br>')
        elif body_content:
            # Clean HTML content using BeautifulSoup if available
            try:
                if PDF_SUPPORT:
                    soup = BeautifulSoup(body_content, 'html.parser')
                    body_content = str(soup)
            except:
                pass
        
        if not body_content:
            body_content = '<p><em>No content available</em></p>'
        
        # HTML template
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{subject}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    line-height: 1.6;
                    color: #333;
                }}
                .email-header {{
                    border-bottom: 2px solid #ccc;
                    padding-bottom: 15px;
                    margin-bottom: 20px;
                }}
                .email-header h1 {{
                    color: #2c3e50;
                    margin-bottom: 10px;
                    font-size: 24px;
                }}
                .metadata {{
                    color: #666;
                    font-size: 14px;
                    background-color: #f8f9fa;
                    padding: 10px;
                    border-radius: 5px;
                }}
                .metadata p {{
                    margin: 5px 0;
                }}
                .email-content {{
                    margin-top: 20px;
                    padding: 10px;
                }}
                .email-content img {{
                    max-width: 100%;
                    height: auto;
                }}
                .signature {{
                    margin-top: 30px;
                    padding-top: 10px;
                    border-top: 1px solid #eee;
                    font-size: 12px;
                    color: #888;
                }}
            </style>
        </head>
        <body>
            <div class="email-header">
                <h1>{subject}</h1>
                <div class="metadata">
                    <p><strong>From:</strong> {from_addr}</p>
                    <p><strong>To:</strong> {to_addr}</p>
                    <p><strong>Date:</strong> {date_str}</p>
                </div>
            </div>
            <div class="email-content">
                {body_content}
            </div>
            <div class="signature">
                <p>Generated by Gmail Attachment Downloader</p>
            </div>
        </body>
        </html>
        """
        
        return html_template
    
    def generate_email_pdf(self, html_content: str, filename: str) -> bool:
        """Generate PDF from HTML email content.
        
        Args:
            html_content: HTML formatted email content
            filename: Name to save the PDF file as
            
        Returns:
            True if PDF generation successful, False otherwise
        """
        if not PDF_SUPPORT:
            logger.error("PDF generation not available. Install weasyprint: pip install weasyprint")
            return False
        
        try:
            file_path = self.download_path / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Generate PDF using WeasyPrint
            html_doc = HTML(string=html_content)
            html_doc.write_pdf(str(file_path))
            
            file_size = file_path.stat().st_size
            logger.info(f"Generated email PDF: {filename} ({file_size} bytes)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate PDF {filename}: {str(e)}")
            return False
    
    def process_message_content(self, message: Dict[str, Any], message_id: str, safe_subject: str) -> bool:
        """Process email content and generate PDF if no attachments.
        
        Args:
            message: Gmail message dictionary
            message_id: Gmail message ID
            safe_subject: Safe filename version of subject
            
        Returns:
            True if email PDF was generated, False otherwise
        """
        if not self.download_email_if_no_attachment or not PDF_SUPPORT:
            return False
        
        try:
            # Extract email content
            content = self.extract_email_content(message)
            
            # Format as HTML
            html_content = self.format_email_as_html(content)
            
            # Determine filename
            if self.create_subject_folders:
                folder_name = f"{safe_subject}_{message_id[:8]}"
                filename = os.path.join(folder_name, "email_content.pdf")
            else:
                filename = f"{message_id[:8]}_email_content.pdf"
            
            # Generate PDF
            return self.generate_email_pdf(html_content, filename)
            
        except Exception as e:
            logger.error(f"Failed to process email content for message {message_id}: {str(e)}")
            return False
    
    def process_message_attachments(self, message: Dict[str, Any], subject_regex: str = '',
                                   filename_regex: str = '') -> int:
        """Process all attachments in a message.
        
        Args:
            message: Gmail message dictionary
            subject_regex: Regular expression to filter by subject
            filename_regex: Regular expression to filter attachment filenames
            
        Returns:
            Number of attachments downloaded
        """
        downloaded_count = 0
        message_id = message['id']
        
        # Get message subject for organizing downloads
        headers = message.get('payload', {}).get('headers', [])
        subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
        date_header = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')
        
        # Apply subject regex filter if specified
        if subject_regex:
            try:
                if not re.search(subject_regex, subject, re.IGNORECASE):
                    logger.debug(f"Subject doesn't match regex '{subject_regex}': {subject}")
                    return 0
            except re.error as e:
                logger.warning(f"Invalid subject regex '{subject_regex}': {e}")
                return 0
        
        # Create a safe filename from subject and date
        safe_subject = "".join(c for c in subject if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_subject = safe_subject[:50]  # Limit length
        
        def extract_attachments(part: Dict[str, Any], path_prefix: str = ""):
            nonlocal downloaded_count
            
            if part.get('filename'):
                attachment_id = part.get('body', {}).get('attachmentId')
                if attachment_id:
                    original_filename = part['filename']
                    
                    # Apply filename regex filter if specified
                    if filename_regex:
                        try:
                            if not re.search(filename_regex, original_filename, re.IGNORECASE):
                                logger.debug(f"Filename doesn't match regex '{filename_regex}': {original_filename}")
                                return
                        except re.error as e:
                            logger.warning(f"Invalid filename regex '{filename_regex}': {e}")
                            return
                    
                    # Determine final filename path
                    if self.create_subject_folders:
                        folder_name = f"{safe_subject}_{message_id[:8]}"
                        filename = os.path.join(folder_name, original_filename)
                    else:
                        # Add message ID prefix to avoid filename conflicts
                        filename = f"{message_id[:8]}_{original_filename}"
                    
                    if self.download_attachment(message_id, attachment_id, filename):
                        downloaded_count += 1
            
            # Recursively check parts
            if 'parts' in part:
                for subpart in part['parts']:
                    extract_attachments(subpart, path_prefix)
        
        # Process message payload
        payload = message.get('payload', {})
        extract_attachments(payload)

        # If no attachments found and email-to-PDF is enabled, generate email PDF
        if downloaded_count == 0 and self.download_email_if_no_attachment:
            logger.debug(f"No attachments found for message {message_id}, generating email PDF")
            if self.process_message_content(message, message_id, safe_subject):
                downloaded_count = 1  # Count email PDF as one "download"

        return downloaded_count
    
    def download_all_attachments(self, query: str = 'has:attachment', max_messages: int = 100,
                                subject_regex: str = '', filename_regex: str = '') -> Dict[str, int]:
        """Download all attachments from Gmail messages matching the query.
        
        Args:
            query: Gmail search query
            max_messages: Maximum number of messages to process
            subject_regex: Regular expression to filter by subject
            filename_regex: Regular expression to filter attachment filenames
            
        Returns:
            Dictionary with download statistics
        """
        if not self.service:
            logger.error("Not authenticated. Please call authenticate() first.")
            return {'messages_processed': 0, 'attachments_downloaded': 0, 'messages_filtered': 0}
        
        logger.info("Starting attachment download process...")
        
        # Get messages with attachments
        messages = self.get_messages(query, max_messages)
        
        total_attachments = 0
        processed_messages = 0
        filtered_messages = 0
        
        for message in messages:
            logger.info(f"Processing message {processed_messages + 1}/{len(messages)}")
            
            # Get detailed message info
            detailed_message = self.get_message_details(message['id'])
            if detailed_message:
                attachments_count = self.process_message_attachments(
                    detailed_message, subject_regex, filename_regex
                )
                
                if attachments_count == 0 and (subject_regex or filename_regex):
                    filtered_messages += 1
                else:
                    total_attachments += attachments_count
                
                processed_messages += 1
            
        stats = {
            'messages_processed': processed_messages,
            'attachments_downloaded': total_attachments,
            'messages_filtered': filtered_messages
        }
        
        logger.info(f"Download complete! Processed {processed_messages} messages, downloaded {total_attachments} attachments")
        if filtered_messages > 0:
            logger.info(f"Filtered out {filtered_messages} messages due to regex constraints")
        return stats


def main():
    """Main application entry point."""
    # Enable debug logging if requested
    debug_logging = os.getenv('DEBUG_LOGGING', 'false').lower() == 'true'
    if debug_logging:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.info("Debug logging enabled")
    
    logger.info("Gmail Attachment Downloader starting...")
    
    # Get configuration from environment variables
    download_path = os.getenv('DOWNLOAD_PATH', './downloads')
    base_search_query = os.getenv('SEARCH_QUERY', 'has:attachment')
    max_messages = int(os.getenv('MAX_MESSAGES', '100'))
    
    # New filtering options
    date_from = os.getenv('DATE_FROM', '')
    date_to = os.getenv('DATE_TO', '')
    subject_regex = os.getenv('SUBJECT_REGEX', '')
    filename_regex = os.getenv('FILENAME_REGEX', '')
    create_subject_folders = os.getenv('CREATE_SUBJECT_FOLDERS', 'true').lower() == 'true'
    download_email_if_no_attachment = os.getenv('DOWNLOAD_EMAIL_IF_NO_ATTACHMENT', 'false').lower() == 'true'
    
    logger.info(f"Configuration:")
    logger.info(f"  Download path: {download_path}")
    logger.info(f"  Base search query: {base_search_query}")
    logger.info(f"  Max messages: {max_messages}")
    logger.info(f"  Create subject folders: {create_subject_folders}")
    logger.info(f"  Download email if no attachment: {download_email_if_no_attachment}")
    if date_from:
        logger.info(f"  Date from: {date_from}")
    if date_to:
        logger.info(f"  Date to: {date_to}")
    if subject_regex:
        logger.info(f"  Subject regex: {subject_regex}")
    if filename_regex:
        logger.info(f"  Filename regex: {filename_regex}")
    
    # Create downloader instance
    downloader = GmailDownloader(download_path, create_subject_folders, download_email_if_no_attachment)
    
    # Build complete search query
    search_query = downloader.build_search_query(
        base_search_query, date_from, date_to, subject_regex
    )
    logger.info(f"  Final search query: {search_query}")
    
    # Authenticate
    if not downloader.authenticate():
        logger.error("Authentication failed. Exiting.")
        sys.exit(1)
    
    # Download attachments
    try:
        stats = downloader.download_all_attachments(
            search_query, max_messages, subject_regex, filename_regex
        )
        
        logger.info("=" * 60)
        logger.info("DOWNLOAD SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Messages processed: {stats['messages_processed']}")
        logger.info(f"Attachments downloaded: {stats['attachments_downloaded']}")
        if stats.get('messages_filtered', 0) > 0:
            logger.info(f"Messages filtered out: {stats['messages_filtered']}")
        logger.info(f"Download location: {download_path}")
        logger.info(f"Subject folders: {'Enabled' if create_subject_folders else 'Disabled'}")
        logger.info("=" * 60)
        
    except KeyboardInterrupt:
        logger.info("Download interrupted by user")
    except Exception as e:
        logger.error(f"An error occurred during download: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()