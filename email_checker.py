#!/usr/bin/env python3
"""
Gmail IMAP client for checking recruiter emails.
Connects to Gmail using IMAP and retrieves new emails from specified labels.
"""

import imaplib
import email
import email.message
import email.utils
from email.header import decode_header
from datetime import datetime
import logging
from typing import List, Dict, Any, Optional
import json

logger = logging.getLogger(__name__)


class GmailChecker:
    def __init__(self, email_address: str, app_password: str):
        """Initialize Gmail checker with credentials."""
        self.email = email_address
        self.password = app_password
        self.connection = None
    
    def connect(self) -> bool:
        """Connect to Gmail IMAP server."""
        try:
            self.connection = imaplib.IMAP4_SSL('imap.gmail.com')
            self.connection.login(self.email, self.password)
            logger.info(f"Successfully connected to Gmail for {self.email}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Gmail for {self.email}: {str(e)}")
            return False
    
    def disconnect(self):
        """Disconnect from Gmail IMAP server."""
        if self.connection:
            try:
                self.connection.logout()
                logger.info(f"Disconnected from Gmail for {self.email}")
            except Exception as e:
                logger.warning(f"Error disconnecting from Gmail: {str(e)}")
            finally:
                self.connection = None
    
    def decode_mime_words(self, s: str) -> str:
        """Decode MIME encoded words in headers."""
        if s is None:
            return ""
        
        decoded_parts = []
        for part, encoding in decode_header(s):
            if isinstance(part, bytes):
                try:
                    if encoding:
                        decoded_parts.append(part.decode(encoding))
                    else:
                        decoded_parts.append(part.decode('utf-8'))
                except (UnicodeDecodeError, LookupError):
                    decoded_parts.append(part.decode('utf-8', errors='ignore'))
            else:
                decoded_parts.append(str(part))
        
        return ''.join(decoded_parts)
    
    def parse_email_message(self, msg: email.message.Message) -> Dict[str, Any]:
        """Parse an email message into a structured format."""
        # Extract basic headers
        subject = self.decode_mime_words(msg.get('Subject', ''))
        sender = self.decode_mime_words(msg.get('From', ''))
        date_str = msg.get('Date', '')
        message_id = msg.get('Message-ID', '')
        
        # Extract thread headers for conversation detection
        in_reply_to = msg.get('In-Reply-To', '')
        references = msg.get('References', '')
        thread_topic = msg.get('Thread-Topic', '')
        thread_index = msg.get('Thread-Index', '')
        
        # Parse date
        try:
            date_received = email.utils.parsedate_to_datetime(date_str)
        except Exception:
            date_received = datetime.now()
        
        # Extract email body
        body_text = ""
        body_html = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get('Content-Disposition', ''))
                
                # Skip attachments
                if 'attachment' in content_disposition:
                    continue
                
                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or 'utf-8'
                        content = payload.decode(charset, errors='ignore')
                        
                        if content_type == 'text/plain':
                            body_text = content
                        elif content_type == 'text/html':
                            body_html = content
                except Exception as e:
                    logger.warning(f"Error decoding email part: {str(e)}")
        else:
            # Single part message
            try:
                payload = msg.get_payload(decode=True)
                if payload:
                    charset = msg.get_content_charset() or 'utf-8'
                    body_text = payload.decode(charset, errors='ignore')
            except Exception as e:
                logger.warning(f"Error decoding email payload: {str(e)}")
        
        return {
            'message_id': message_id,
            'subject': subject,
            'sender': sender,
            'date_received': date_received,
            'body_text': body_text,
            'body_html': body_html,
            'raw_email': msg.as_string(),
            # Thread detection headers
            'in_reply_to': in_reply_to,
            'references': references,
            'thread_topic': thread_topic,
            'thread_index': thread_index
        }
    
    def check_new_emails(self, label) -> List[Dict[str, Any]]:
        """
        Check for all emails in the specified Gmail label.
        
        Args:
            label: Gmail label to search
        
        Returns:
            List of parsed email messages
        """
        if not label:
            logger.error("Label must be specified for checking emails")
            raise ValueError("Label must be specified")

        if not self.connection:
            if not self.connect():
                return []
        
        try:
            # Select the label (Gmail uses IMAP folders)
            # Gmail labels are case-sensitive and may need quotes
            try:
                status, messages = self.connection.select(f'"{label}"')
            except Exception:
                # Try without quotes
                status, messages = self.connection.select(label)
            
            if status != 'OK':
                logger.error(f"Failed to select label '{label}' for {self.email}")
                return []
            
            # Get ALL emails in the label - we'll filter by database later
            # If an email has the label, we want to process it regardless of date
            search_criteria = 'ALL'
            
            # Search for emails
            status, message_ids = self.connection.search(None, search_criteria)
            if status != 'OK':
                logger.error(f"Failed to search emails in label '{label}' for {self.email}")
                return []
            
            # Parse message IDs
            if not message_ids[0]:
                logger.info(f"No new emails found in label '{label}' for {self.email}")
                return []
            
            message_id_list = message_ids[0].split()
            logger.info(f"Found {len(message_id_list)} emails in label '{label}' for {self.email}")
            
            # Fetch and parse emails
            emails = []
            for msg_id in message_id_list:
                try:
                    # Fetch the email
                    status, msg_data = self.connection.fetch(msg_id, '(RFC822)')
                    if status != 'OK':
                        continue
                    
                    # Parse the email
                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)
                    parsed_email = self.parse_email_message(msg)
                    
                    emails.append(parsed_email)
                    
                except Exception as e:
                    logger.error(f"Error processing email {msg_id}: {str(e)}")
                    continue
            
            logger.info(f"Successfully parsed {len(emails)} emails for {self.email}")
            return emails
            
        except Exception as e:
            logger.error(f"Error checking emails for {self.email}: {str(e)}")
            return []
    
    def test_connection(self) -> bool:
        """Test the Gmail connection and basic functionality."""
        try:
            if not self.connect():
                return False
            
            # List available folders/labels
            status, folders = self.connection.list()
            if status == 'OK':
                logger.info(f"Available folders for {self.email}: {len(folders)} folders")
                # Log first few folder names for debugging
                for folder in folders[:5]:
                    logger.debug(f"  - {folder}")
            
            return True
            
        except Exception as e:
            logger.error(f"Connection test failed for {self.email}: {str(e)}")
            return False
        finally:
            self.disconnect()


def test_gmail_connection(email_address: str, app_password: str, label: str = 'Recruiters'):
    """Test Gmail connection and email checking functionality."""
    logger.info(f"Testing Gmail connection for {email_address}")
    
    checker = GmailChecker(email_address, app_password)
    
    # Test basic connection
    if not checker.test_connection():
        logger.error("Basic connection test failed")
        return False
    
    # Test email checking
    try:
        emails = checker.check_new_emails(label=label)
        logger.info(f"Email check test successful: found {len(emails)} recent emails")
        
        # Log details of first email if any
        if emails:
            first_email = emails[0]
            logger.info(f"Sample email: '{first_email['subject']}' from {first_email['sender']}")
        
        return True
        
    except Exception as e:
        logger.error(f"Email checking test failed: {str(e)}")
        return False
    finally:
        checker.disconnect()


if __name__ == "__main__":
    # Test the Gmail checker with example credentials
    logging.basicConfig(level=logging.INFO)
    
    # These would come from environment variables in real usage
    test_email = "your.email@gmail.com"
    test_password = "your app password here"
    test_label = "Recruiters"
    
    print(f"Testing Gmail checker for {test_email}")
    success = test_gmail_connection(test_email, test_password, test_label)
    
    if success:
        print("✅ Gmail checker test passed!")
    else:
        print("❌ Gmail checker test failed!")