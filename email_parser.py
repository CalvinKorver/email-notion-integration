#!/usr/bin/env python3
"""
Email parser for extracting recruiter data from Gmail messages.
Analyzes email content to extract recruiter information.
"""

import re
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from email.utils import parseaddr

logger = logging.getLogger(__name__)


class EmailParser:
    """Parser for extracting recruiter data from email messages."""
    
    def __init__(self, user_email: str = None):
        """Initialize the email parser."""
        self.user_email = user_email
        self.user_domain = user_email.split('@')[1].lower() if user_email and '@' in user_email else None
        
        # Common job title keywords
        self.job_keywords = [
            'engineer', 'developer', 'manager', 'director', 'analyst', 
            'specialist', 'coordinator', 'lead', 'senior', 'junior',
            'architect', 'consultant', 'designer', 'scientist', 'principal',
            'software', 'backend', 'frontend', 'fullstack', 'devops',
            'data', 'ml', 'ai', 'machine learning', 'python', 'javascript',
            'react', 'node', 'java', 'golang', 'rust', 'scala'
        ]
        
        # Company domain patterns to skip
        self.skip_domains = [
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
            'aol.com', 'icloud.com', 'protonmail.com'
        ]
        
        # Location patterns
        self.location_patterns = [
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2})\b',  # City, ST
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z][a-z]+)\b',  # City, State
            r'\b(Remote|remote)\b',  # Remote work
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+area\b',  # Bay Area, NYC area
        ]
    
    def is_thread_starter(self, email_data: Dict[str, Any]) -> bool:
        """
        Determine if this email starts a new thread (original outreach).
        
        Args:
            email_data: Email data dictionary with thread headers
            
        Returns:
            True if this is a thread starter, False if it's a reply
        """
        # Check for reply headers
        in_reply_to = email_data.get('in_reply_to', '').strip()
        references = email_data.get('references', '').strip()
        
        # If email has In-Reply-To or References headers, it's a reply
        if in_reply_to or references:
            return False
        
        # Check subject for reply patterns
        subject = email_data.get('subject', '').strip()
        if subject.lower().startswith(('re:', 'fw:', 'fwd:')):
            return False
            
        return True
    
    def is_external_sender(self, email_data: Dict[str, Any]) -> bool:
        """
        Determine if the sender is external (not from user's domain).
        
        Args:
            email_data: Email data dictionary
            
        Returns:
            True if sender is external, False if internal
        """
        sender = email_data.get('sender', '')
        
        # Extract email from sender field
        if '<' in sender and '>' in sender:
            sender_email = sender.split('<')[1].split('>')[0]
        else:
            sender_email = sender
            
        if not sender_email or '@' not in sender_email:
            return True  # Assume external if can't determine
            
        sender_domain = sender_email.split('@')[1].lower()
        
        # Check if sender is from user's domain
        if self.user_domain and sender_domain == self.user_domain:
            return False
            
        return True
    
    def should_process_email(self, email_data: Dict[str, Any]) -> bool:
        """
        Determine if this email should be processed (create Notion entry).
        
        Args:
            email_data: Email data dictionary
            
        Returns:
            True if should process, False if should skip
        """
        # Only process emails that:
        # 1. Start a new thread (not replies)
        # 2. Are from external senders (not from user's domain)
        
        if not self.is_thread_starter(email_data):
            logger.info(f"Skipping reply email: {email_data.get('subject', 'No subject')}")
            return False
            
        if not self.is_external_sender(email_data):
            logger.info(f"Skipping internal email: {email_data.get('subject', 'No subject')}")
            return False
            
        return True
    
    def extract_recruiter_info(self, sender: str, email_content: str = "") -> Dict[str, str]:
        """Extract recruiter name and email from sender field and email content."""
        # Parse sender using email.utils.parseaddr
        name, email_addr = parseaddr(sender)
        
        # Clean up the name from sender field
        if name:
            # Remove quotes and extra whitespace
            name = name.strip().strip('"').strip("'")
        
        # If no name found in sender, try to extract from email content
        if not name and email_content:
            name = self.extract_name_from_content(email_content)
        
        # Default values
        if not name:
            name = "Unknown Recruiter"
        if not email_addr:
            email_addr = "unknown@example.com"
        
        return {
            'recruiter_name': name,
            'recruiter_email': email_addr
        }
    
    def extract_name_from_content(self, content: str) -> str:
        """Extract recruiter name from email content."""
        if not content:
            return ""
        
        # Common email endings to look for names after
        ending_patterns = [
            r'(?:Best|Best regards|Regards|Thanks|Thank you|Cheers|Sincerely|From),?\s*\n\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*?)(?:\s*\n|$)',
            r'\n([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*\n.*?(?:Recruiter|Talent|HR|Human Resources)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*\n(?:Talent Acquisition|HR|Human Resources|Recruiter)',
        ]
        
        for pattern in ending_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            if matches:
                name = matches[0].strip()
                # Validate the name (should be reasonable length and not contain numbers)
                if 2 <= len(name) <= 50 and not re.search(r'\d', name):
                    return name
        
        # Look for names at the end of the email (last few words before signature)
        lines = content.strip().split('\n')
        if lines:
            # Check last few non-empty lines
            for line in reversed(lines[-5:]):
                line = line.strip()
                if line and not re.search(r'@|http|www|\.com|phone|mobile|office', line, re.IGNORECASE):
                    # Extract potential name (1-3 words starting with capitals)
                    words = line.split()
                    if len(words) <= 3:
                        potential_name = ' '.join(words)
                        if re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$', potential_name):
                            return potential_name
        
        return ""
    
    def extract_company_from_email(self, email_addr: str) -> str:
        """Extract company name from email domain."""
        if not email_addr or '@' not in email_addr:
            return "Unknown Company"
        
        domain = email_addr.split('@')[1].lower()
        
        # Skip personal email domains
        if domain in self.skip_domains:
            return "Unknown Company"
        
        # Extract company name from domain
        # Remove common TLD patterns
        company_part = domain.split('.')[0]
        
        # Clean up and capitalize
        company = company_part.replace('-', ' ').replace('_', ' ').title()
        
        # Handle some common patterns
        if company.lower() in ['hr', 'talent', 'recruiting', 'careers']:
            # These are generic, try to get more context
            parts = domain.split('.')
            if len(parts) > 2:
                company = parts[1].replace('-', ' ').replace('_', ' ').title()
        
        return company
    
    def extract_position_from_subject(self, subject: str) -> str:
        """Extract job position from email subject."""
        if not subject:
            return "Software Position"
        
        subject_lower = subject.lower()
        
        # Look for job title patterns
        for keyword in self.job_keywords:
            if keyword in subject_lower:
                # Try to extract a more specific title
                words = subject.split()
                for i, word in enumerate(words):
                    if keyword in word.lower():
                        # Take the keyword and surrounding words
                        start = max(0, i-1)
                        end = min(len(words), i+3)
                        position = ' '.join(words[start:end])
                        # Clean up the position
                        position = re.sub(r'[^\w\s]', '', position).strip()
                        if position:
                            return position
                break
        
        # Fallback: look for common position patterns
        position_patterns = [
            r'(senior|sr\.?|principal|lead|staff)\s+\w+\s+(engineer|developer)',
            r'(full.?stack|backend|frontend|front.end)\s+(engineer|developer)',
            r'(software|web|mobile)\s+(engineer|developer)',
            r'(data|ml|ai)\s+(engineer|scientist)',
            r'(devops|sre|platform)\s+engineer',
        ]
        
        for pattern in position_patterns:
            match = re.search(pattern, subject_lower)
            if match:
                return match.group(0).title()
        
        return "Software Position"
    
    def extract_location_from_content(self, content: str) -> str:
        """Extract location from email content."""
        if not content:
            return "Remote"
        
        # Look for location patterns
        for pattern in self.location_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                if isinstance(matches[0], tuple):
                    # City, State pattern
                    return f"{matches[0][0]}, {matches[0][1]}"
                else:
                    # Single match
                    return matches[0]
        
        # Common location keywords
        location_keywords = [
            'san francisco', 'sf', 'bay area', 'silicon valley',
            'new york', 'nyc', 'seattle', 'austin', 'denver',
            'boston', 'chicago', 'los angeles', 'la', 'remote'
        ]
        
        content_lower = content.lower()
        for keyword in location_keywords:
            if keyword in content_lower:
                return keyword.title()
        
        return "Remote"
    
    def extract_company_from_content(self, content: str, fallback_company: str) -> str:
        """Extract company name from email content."""
        if not content:
            return fallback_company
        
        # Look for company signature patterns
        patterns = [
            r'(?:from|at|with)\s+([A-Z][a-zA-Z\s&]+(?:Inc|LLC|Corp|Company|Technologies|Systems|Solutions))',
            r'([A-Z][a-zA-Z\s&]+(?:Inc|LLC|Corp|Company|Technologies|Systems|Solutions))',
            r'(?:representing|for)\s+([A-Z][a-zA-Z\s&]+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            if matches:
                company = matches[0].strip()
                if len(company) > 2 and company != fallback_company:
                    return company
        
        return fallback_company
    
    def parse_recruiter_email(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse an email message to extract recruiter information.
        
        Args:
            email_data: Dictionary containing email information
                - sender: str
                - subject: str
                - body_text: str
                - body_html: str
                - date_received: datetime
                - message_id: str
        
        Returns:
            Dictionary containing parsed recruiter data
        """
        try:
            # Get email content for name extraction
            content = email_data.get('body_text', '') or email_data.get('body_html', '')
            
            # Extract recruiter info from sender and content
            recruiter_info = self.extract_recruiter_info(email_data.get('sender', ''), content)
            
            # Extract company from email domain
            company = self.extract_company_from_email(recruiter_info['recruiter_email'])
            
            # Extract position from subject
            position = self.extract_position_from_subject(email_data.get('subject', ''))
            
            # Extract location from content
            location = self.extract_location_from_content(content)
            
            # Try to get better company name from content
            company = self.extract_company_from_content(content, company)
            
            # Get date received
            date_received = email_data.get('date_received')
            if not isinstance(date_received, datetime):
                date_received = datetime.now()
            
            parsed_data = {
                'recruiter_name': recruiter_info['recruiter_name'],
                'recruiter_email': recruiter_info['recruiter_email'],
                'company': company,
                'position': position,
                'location': location,
                'status': 'Applied',  # Default status for new entries
                'date_received': date_received
            }
            
            logger.info(f"Parsed email: {recruiter_info['recruiter_name']} from {company} for {position}")
            return parsed_data
            
        except Exception as e:
            logger.error(f"Error parsing email: {str(e)}")
            # Return default values on error
            return {
                'recruiter_name': 'Unknown Recruiter',
                'recruiter_email': 'unknown@example.com',
                'company': 'Unknown Company',
                'position': 'Software Position',
                'location': 'Remote',
                'status': 'Applied',
                'date_received': datetime.now()
            }


def test_email_parser():
    """Test the email parser with sample data."""
    parser = EmailParser('test@example.com')
    
    # Test data
    test_emails = [
        {
            'sender': 'Sarah Johnson <sarah.johnson@techcorp.com>',
            'subject': 'Senior Software Engineer Opportunity at TechCorp',
            'body_text': 'Hi! I hope this message finds you well. I am reaching out from TechCorp regarding a Senior Software Engineer position in San Francisco, CA. We are looking for someone with your skills...',
            'date_received': datetime.now()
        },
        {
            'sender': 'recruiting@startup.io',
            'subject': 'Full Stack Developer Role - Remote',
            'body_text': 'Hello, We have an exciting Full Stack Developer opportunity that is fully remote. Our company, Startup Inc, is looking for talented developers...',
            'date_received': datetime.now()
        },
        {
            'sender': 'Jane Smith <jane@gmail.com>',
            'subject': 'Great opportunity',
            'body_text': 'I represent BigTech Corp and we have a Principal Engineer position available in Seattle, WA.\n\nBest regards,\nMichael Rodriguez',
            'date_received': datetime.now()
        },
        {
            'sender': 'recruiting@bigtech.com',
            'subject': 'Backend Developer Position',
            'body_text': 'Hello,\n\nWe have an excellent Backend Developer opportunity at our company. The position is based in Austin, TX.\n\nThanks,\nSamantha Chen\nTalent Acquisition | BigTech Corp',
            'date_received': datetime.now()
        }
    ]
    
    print("Testing Email Parser")
    print("=" * 50)
    
    for i, email_data in enumerate(test_emails, 1):
        print(f"\nTest {i}:")
        print(f"Input: {email_data['sender']} - {email_data['subject']}")
        
        parsed = parser.parse_recruiter_email(email_data)
        
        print(f"Output:")
        print(f"  Recruiter: {parsed['recruiter_name']} ({parsed['recruiter_email']})")
        print(f"  Company: {parsed['company']}")
        print(f"  Position: {parsed['position']}")
        print(f"  Location: {parsed['location']}")
        print(f"  Status: {parsed['status']}")


if __name__ == "__main__":
    # Test the parser
    test_email_parser()