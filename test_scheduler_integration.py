#!/usr/bin/env python3
"""
Test script for the scheduler integration with Flask app.
"""

import logging
import time
from datetime import datetime
from scheduler import EmailScheduler, get_scheduler
from config import get_config_summary

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_scheduler_integration():
    """Test the scheduler integration."""
    print("=" * 60)
    print("SCHEDULER INTEGRATION TEST")
    print("=" * 60)
    
    try:
        # Test 1: Configuration
        print("\n1. Testing Configuration...")
        config_summary = get_config_summary()
        print(f"   Configuration: {config_summary}")
        
        # Test 2: Scheduler Creation
        print("\n2. Testing Scheduler Creation...")
        scheduler = EmailScheduler()
        print("   ✅ Scheduler created successfully")
        
        # Test 3: Global Scheduler Instance
        print("\n3. Testing Global Scheduler Instance...")
        global_scheduler = get_scheduler()
        print("   ✅ Global scheduler instance retrieved")
        
        # Test 4: Job Status (before start)
        print("\n4. Testing Job Status (before start)...")
        status = scheduler.get_job_status()
        print(f"   Status: {status}")
        
        # Test 5: Start Scheduler
        print("\n5. Testing Scheduler Start...")
        scheduler.start()
        print("   ✅ Scheduler started successfully")
        
        # Test 6: Job Status (after start)
        print("\n6. Testing Job Status (after start)...")
        status = scheduler.get_job_status()
        print(f"   Status: {status}")
        
        if status['jobs']:
            next_run = status['jobs'][0]['next_run_time']
            print(f"   Next job run: {next_run}")
        
        # Test 7: Manual Check
        print("\n7. Testing Manual Check...")
        result = scheduler.run_manual_check()
        print(f"   Manual check result: {result}")
        
        # Test 8: Wait a bit to see if scheduler is running
        print("\n8. Testing Scheduler Monitoring...")
        print("   Waiting 5 seconds to monitor scheduler...")
        time.sleep(5)
        
        # Test 9: Stop Scheduler
        print("\n9. Testing Scheduler Stop...")
        scheduler.stop()
        print("   ✅ Scheduler stopped successfully")
        
        # Test 10: Final Status Check
        print("\n10. Testing Final Status...")
        status = scheduler.get_job_status()
        print(f"    Final status: {status}")
        
        print("\n" + "=" * 60)
        print("✅ ALL SCHEDULER INTEGRATION TESTS PASSED")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        logger.error(f"Scheduler integration test failed: {str(e)}")
        print("=" * 60)
        return False

def test_email_parser():
    """Test the email parser functionality."""
    print("\n" + "=" * 60)
    print("EMAIL PARSER TEST")
    print("=" * 60)
    
    try:
        from email_parser import EmailParser
        
        parser = EmailParser()
        
        # Test data
        test_email = {
            'sender': 'Sarah Johnson <sarah.johnson@techcorp.com>',
            'subject': 'Senior Software Engineer Opportunity',
            'body_text': 'Hi! I am reaching out from TechCorp regarding a Senior Software Engineer position in San Francisco, CA.',
            'date_received': datetime.now(),
            'message_id': 'test-message-123'
        }
        
        print("Testing email parsing...")
        parsed = parser.parse_recruiter_email(test_email)
        
        print(f"Input: {test_email['sender']} - {test_email['subject']}")
        print(f"Output:")
        print(f"  Recruiter: {parsed['recruiter_name']} ({parsed['recruiter_email']})")
        print(f"  Company: {parsed['company']}")
        print(f"  Position: {parsed['position']}")
        print(f"  Location: {parsed['location']}")
        print(f"  Status: {parsed['status']}")
        
        print("\n✅ Email parser test passed")
        return True
        
    except Exception as e:
        print(f"\n❌ Email parser test failed: {str(e)}")
        return False

def test_database_methods():
    """Test the database methods needed by scheduler."""
    print("\n" + "=" * 60)
    print("DATABASE METHODS TEST")
    print("=" * 60)
    
    try:
        from database import DatabaseManager
        
        db = DatabaseManager()
        
        # Test user operations
        print("Testing database methods...")
        
        # Test get_user_last_check
        last_check = db.get_user_last_check('test@example.com')
        print(f"  get_user_last_check: {last_check}")
        
        # Test update_user_last_check
        result = db.update_user_last_check('test@example.com', datetime.now())
        print(f"  update_user_last_check: {result}")
        
        # Test email_already_processed
        processed = db.email_already_processed('test-message-123')
        print(f"  email_already_processed: {processed}")
        
        print("\n✅ Database methods test passed")
        return True
        
    except Exception as e:
        print(f"\n❌ Database methods test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("COMPREHENSIVE SCHEDULER INTEGRATION TEST")
    print("=" * 80)
    
    success = True
    
    # Run all tests
    success &= test_scheduler_integration()
    success &= test_email_parser()
    success &= test_database_methods()
    
    print("\n" + "=" * 80)
    if success:
        print("🎉 ALL TESTS PASSED - SCHEDULER INTEGRATION READY!")
    else:
        print("❌ SOME TESTS FAILED - PLEASE CHECK ABOVE")
    print("=" * 80)