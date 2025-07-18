#!/usr/bin/env python3
"""
Background scheduler for periodic email checking.
Uses APScheduler to run email checking jobs at regular intervals.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
import atexit

# Import project modules
from config import USERS, CHECK_INTERVAL, EMAIL_LOOKBACK_DAYS, get_config_summary
from email_checker import GmailChecker
from email_parser import EmailParser
from notion_api import NotionClient
from database import DatabaseManager

logger = logging.getLogger(__name__)


class EmailScheduler:
    """Background scheduler for periodic email checking."""
    
    def __init__(self):
        """Initialize the scheduler."""
        self.scheduler = BackgroundScheduler()
        self.db_manager = DatabaseManager()
        self.is_running = False
        
        # Add event listeners
        self.scheduler.add_listener(self._job_executed, EVENT_JOB_EXECUTED)
        self.scheduler.add_listener(self._job_error, EVENT_JOB_ERROR)
        
        # Ensure scheduler shuts down on exit
        atexit.register(self.shutdown)
    
    def _job_executed(self, event):
        """Handle successful job execution."""
        logger.info(f"Job {event.job_id} executed successfully")
    
    def _job_error(self, event):
        """Handle job execution errors."""
        logger.error(f"Job {event.job_id} failed with error: {event.exception}")
    
    def process_user_emails(self, user_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process emails for a single user.
        
        Args:
            user_config: User configuration dictionary
            
        Returns:
            Dictionary with processing results
        """
        result = {
            'user_name': user_config['name'],
            'user_email': user_config['email'],
            'emails_processed': 0,
            'emails_created': 0,
            'errors': [],
            'success': True
        }
        
        try:
            # Get last check time from database
            last_check = self.db_manager.get_user_last_check(user_config['email'])
            if last_check is None:
                # First time checking, look back specified days
                since_date = datetime.now() - timedelta(days=EMAIL_LOOKBACK_DAYS)
                logger.info(f"First time checking for {user_config['name']}, looking back {EMAIL_LOOKBACK_DAYS} days")
            else:
                since_date = last_check
                logger.info(f"Checking emails for {user_config['name']} since {since_date}")
            
            # Initialize Gmail checker and email parser
            gmail_checker = GmailChecker(user_config['email'], user_config['gmail_app_password'])
            email_parser = EmailParser(user_config['email'])
            
            # Check for new emails
            emails = gmail_checker.check_new_emails(
                label=user_config['gmail_label']
            )
            
            if not emails:
                logger.info(f"No new emails found for {user_config['name']}")
                # Update last check time even if no emails found
                self.db_manager.update_user_last_check(user_config['email'], datetime.now())
                return result
            
            result['emails_processed'] = len(emails)
            logger.info(f"Found {len(emails)} new emails for {user_config['name']}")
            
            # Initialize Notion client
            notion_client = NotionClient(user_config['notion_token'])
            
            # Process each email
            for email_data in emails:
                try:
                    # Check if we've already processed this email
                    if self.db_manager.email_already_processed(email_data['message_id']):
                        logger.info(f"Email {email_data['message_id']} already processed, skipping")
                        continue
                    
                    # Check if this email should be processed (thread filtering)
                    if not email_parser.should_process_email(email_data):
                        logger.info(f"Skipping email based on thread filtering: {email_data.get('subject', 'No subject')}")
                        continue
                    
                    # Parse email to extract recruiter data
                    parsed_data = email_parser.parse_recruiter_email(email_data)
                    
                    # Check if we already have a contact from this company
                    user_record = self.db_manager.get_user_by_email(user_config['email'])
                    if user_record:
                        user_id = user_record['id']
                        existing_company_contact = self.db_manager.get_contact_by_company(user_id, parsed_data['company'])
                        
                        if existing_company_contact:
                            logger.info(f"Skipping email from {parsed_data['company']} - already have contact from this company")
                            # Log the skipped email to database to prevent reprocessing
                            self.db_manager.log_recruiter_contact(
                                user_config['email'],
                                email_data['message_id'],
                                parsed_data,
                                None  # No Notion page created
                            )
                            continue
                    
                    # Create Notion entry
                    page_id = notion_client.create_recruiter_entry(
                        user_config['notion_database_id'],
                        parsed_data
                    )
                    
                    if page_id:
                        # Log to database
                        self.db_manager.log_recruiter_contact(
                            user_config['email'],
                            email_data['message_id'],
                            parsed_data,
                            page_id
                        )
                        
                        result['emails_created'] += 1
                        logger.info(f"Successfully processed email from {parsed_data.get('recruiter_name', 'Unknown')} for {user_config['name']}")
                    else:
                        error_msg = f"Failed to create Notion entry for email {email_data['message_id']}"
                        result['errors'].append(error_msg)
                        logger.error(error_msg)
                        
                        # Still log the attempt to database
                        self.db_manager.log_recruiter_contact(
                            user_config['email'],
                            email_data['message_id'],
                            parsed_data,
                            None  # No page_id since creation failed
                        )
                
                except Exception as e:
                    error_msg = f"Error processing email {email_data.get('message_id', 'unknown')}: {str(e)}"
                    result['errors'].append(error_msg)
                    logger.error(error_msg)
            
            # Update last check time
            self.db_manager.update_user_last_check(user_config['email'], datetime.now())
            
            # Disconnect from Gmail
            gmail_checker.disconnect()
            
        except Exception as e:
            error_msg = f"Error processing emails for {user_config['name']}: {str(e)}"
            result['errors'].append(error_msg)
            result['success'] = False
            logger.error(error_msg)
        
        return result
    
    def check_all_users_emails(self):
        """Check emails for all configured users."""
        logger.info("Starting scheduled email check for all users")
        
        total_processed = 0
        total_created = 0
        total_errors = 0
        
        for user_config in USERS:
            try:
                logger.info(f"Checking emails for {user_config['name']}")
                result = self.process_user_emails(user_config)
                
                total_processed += result['emails_processed']
                total_created += result['emails_created']
                total_errors += len(result['errors'])
                
                if result['success']:
                    logger.info(f"Successfully processed {result['emails_processed']} emails for {user_config['name']}, created {result['emails_created']} Notion entries")
                else:
                    logger.error(f"Failed to process emails for {user_config['name']}: {result['errors']}")
                    
            except Exception as e:
                logger.error(f"Unexpected error processing user {user_config['name']}: {str(e)}")
                total_errors += 1
        
        logger.info(f"Scheduled email check completed - Processed: {total_processed}, Created: {total_created}, Errors: {total_errors}")
    
    def setup_email_checker(self):
        """Set up the periodic email checking job."""
        logger.info(f"Setting up email checker with {CHECK_INTERVAL} minute interval")
        
        # Add the job to check emails periodically
        self.scheduler.add_job(
            func=self.check_all_users_emails,
            trigger=IntervalTrigger(minutes=CHECK_INTERVAL),
            id='email_checker_job',
            name='Check all users emails',
            replace_existing=True,
            max_instances=1  # Prevent overlapping jobs
        )
        
        logger.info("Email checker job configured successfully")
    
    def start(self):
        """Start the scheduler."""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        try:
            # Validate configuration
            config_summary = get_config_summary()
            if config_summary['config_errors']:
                logger.warning(f"Configuration issues found: {config_summary['config_errors']}")
            
            # Set up the email checking job
            self.setup_email_checker()
            
            # Start the scheduler
            self.scheduler.start()
            self.is_running = True
            
            logger.info("Email scheduler started successfully")
            logger.info(f"Next job execution: {self.scheduler.get_job('email_checker_job').next_run_time}")
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {str(e)}")
            raise
    
    def stop(self):
        """Stop the scheduler."""
        if not self.is_running:
            logger.warning("Scheduler is not running")
            return
        
        try:
            self.scheduler.shutdown(wait=True)
            self.is_running = False
            logger.info("Email scheduler stopped")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {str(e)}")
    
    def shutdown(self):
        """Shutdown the scheduler (called on exit)."""
        if self.is_running:
            logger.info("Shutting down email scheduler...")
            self.stop()
    
    def get_job_status(self) -> Dict[str, Any]:
        """Get current status of scheduled jobs."""
        if not self.is_running:
            return {'status': 'stopped', 'jobs': []}
        
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time,
                'trigger': str(job.trigger)
            })
        
        return {
            'status': 'running',
            'jobs': jobs
        }
    
    def run_manual_check(self) -> Dict[str, Any]:
        """Run a manual email check for all users."""
        logger.info("Running manual email check")
        
        try:
            self.check_all_users_emails()
            return {'success': True, 'message': 'Manual email check completed'}
        except Exception as e:
            error_msg = f"Manual email check failed: {str(e)}"
            logger.error(error_msg)
            return {'success': False, 'message': error_msg}


# Global scheduler instance
_scheduler_instance = None


def get_scheduler() -> EmailScheduler:
    """Get the global scheduler instance."""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = EmailScheduler()
    return _scheduler_instance


def start_scheduler():
    """Start the global scheduler."""
    scheduler = get_scheduler()
    scheduler.start()


def stop_scheduler():
    """Stop the global scheduler."""
    scheduler = get_scheduler()
    scheduler.stop()


def get_scheduler_status() -> Dict[str, Any]:
    """Get the status of the global scheduler."""
    scheduler = get_scheduler()
    return scheduler.get_job_status()


def run_manual_check() -> Dict[str, Any]:
    """Run a manual email check."""
    scheduler = get_scheduler()
    return scheduler.run_manual_check()


if __name__ == "__main__":
    # Test the scheduler
    logging.basicConfig(level=logging.INFO)
    
    print("Testing Email Scheduler")
    print("=" * 50)
    
    scheduler = EmailScheduler()
    
    # Test configuration
    config = get_config_summary()
    print(f"Configuration: {config}")
    
    # Test manual check
    print("\nRunning manual check...")
    result = scheduler.run_manual_check()
    print(f"Manual check result: {result}")
    
    print("\nScheduler test completed")