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
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

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
    
    def __init__(self, download_path: str = './downloads'):
        """Initialize the Gmail downloader.
        
        Args:
            download_path: Path where attachments will be saved
        """
        self.download_path = Path(download_path)
        self.download_path.mkdir(parents=True, exist_ok=True)
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
                    creds_file = os.getenv('GMAIL_CREDENTIALS_FILE', 'credentials.json')
                    if not os.path.exists(creds_file):
                        logger.error(f"Credentials file {creds_file} not found!")
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
    
    def get_messages(self, query: str = '', max_results: int = 100) -> List[Dict[str, Any]]:
        """Get Gmail messages.
        
        Args:
            query: Gmail search query (e.g., 'has:attachment')
            max_results: Maximum number of messages to retrieve
            
        Returns:
            List of message dictionaries
        """
        try:
            logger.info(f"Searching for messages with query: '{query}'")
            result = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = result.get('messages', [])
            logger.info(f"Found {len(messages)} messages")
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
    
    def process_message_attachments(self, message: Dict[str, Any]) -> int:
        """Process all attachments in a message.
        
        Args:
            message: Gmail message dictionary
            
        Returns:
            Number of attachments downloaded
        """
        downloaded_count = 0
        message_id = message['id']
        
        # Get message subject for organizing downloads
        headers = message.get('payload', {}).get('headers', [])
        subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
        date_header = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')
        
        # Create a safe filename from subject and date
        safe_subject = "".join(c for c in subject if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_subject = safe_subject[:50]  # Limit length
        
        def extract_attachments(part: Dict[str, Any], path_prefix: str = ""):
            nonlocal downloaded_count
            
            if part.get('filename'):
                attachment_id = part.get('body', {}).get('attachmentId')
                if attachment_id:
                    # Create organized folder structure
                    folder_name = f"{safe_subject}_{message_id[:8]}"
                    filename = os.path.join(folder_name, part['filename'])
                    
                    if self.download_attachment(message_id, attachment_id, filename):
                        downloaded_count += 1
            
            # Recursively check parts
            if 'parts' in part:
                for subpart in part['parts']:
                    extract_attachments(subpart, path_prefix)
        
        # Process message payload
        payload = message.get('payload', {})
        extract_attachments(payload)
        
        return downloaded_count
    
    def download_all_attachments(self, query: str = 'has:attachment', max_messages: int = 100) -> Dict[str, int]:
        """Download all attachments from Gmail messages matching the query.
        
        Args:
            query: Gmail search query
            max_messages: Maximum number of messages to process
            
        Returns:
            Dictionary with download statistics
        """
        if not self.service:
            logger.error("Not authenticated. Please call authenticate() first.")
            return {'messages_processed': 0, 'attachments_downloaded': 0}
        
        logger.info("Starting attachment download process...")
        
        # Get messages with attachments
        messages = self.get_messages(query, max_messages)
        
        total_attachments = 0
        processed_messages = 0
        
        for message in messages:
            logger.info(f"Processing message {processed_messages + 1}/{len(messages)}")
            
            # Get detailed message info
            detailed_message = self.get_message_details(message['id'])
            if detailed_message:
                attachments_count = self.process_message_attachments(detailed_message)
                total_attachments += attachments_count
                processed_messages += 1
            
        stats = {
            'messages_processed': processed_messages,
            'attachments_downloaded': total_attachments
        }
        
        logger.info(f"Download complete! Processed {processed_messages} messages, downloaded {total_attachments} attachments")
        return stats


def main():
    """Main application entry point."""
    logger.info("Gmail Attachment Downloader starting...")
    
    # Get configuration from environment variables
    download_path = os.getenv('DOWNLOAD_PATH', './downloads')
    search_query = os.getenv('SEARCH_QUERY', 'has:attachment')
    max_messages = int(os.getenv('MAX_MESSAGES', '100'))
    
    logger.info(f"Configuration:")
    logger.info(f"  Download path: {download_path}")
    logger.info(f"  Search query: {search_query}")
    logger.info(f"  Max messages: {max_messages}")
    
    # Create downloader instance
    downloader = GmailDownloader(download_path)
    
    # Authenticate
    if not downloader.authenticate():
        logger.error("Authentication failed. Exiting.")
        sys.exit(1)
    
    # Download attachments
    try:
        stats = downloader.download_all_attachments(search_query, max_messages)
        
        logger.info("=" * 50)
        logger.info("DOWNLOAD SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Messages processed: {stats['messages_processed']}")
        logger.info(f"Attachments downloaded: {stats['attachments_downloaded']}")
        logger.info(f"Download location: {download_path}")
        logger.info("=" * 50)
        
    except KeyboardInterrupt:
        logger.info("Download interrupted by user")
    except Exception as e:
        logger.error(f"An error occurred during download: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()