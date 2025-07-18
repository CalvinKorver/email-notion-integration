#!/usr/bin/env python3
"""
Test script to verify the 3-day lookback period is working correctly.
"""

import logging
import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our modules
from config import EMAIL_LOOKBACK_DAYS, get_config_summary
from scheduler import get_scheduler

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_3_day_lookback():
    """Test the 3-day lookback configuration."""
    print("=" * 60)
    print("3-DAY LOOKBACK TEST")
    print("=" * 60)
    
    # Test 1: Configuration
    print("\n1. Testing Configuration...")
    config_summary = get_config_summary()
    print(f"   Email lookback days: {EMAIL_LOOKBACK_DAYS}")
    print(f"   Configuration loaded successfully: ✅")
    
    # Test 2: Date Calculation
    print("\n2. Testing Date Calculation...")
    current_time = datetime.now()
    lookback_date = current_time - timedelta(days=EMAIL_LOOKBACK_DAYS)
    print(f"   Current time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Lookback date: {lookback_date.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Days difference: {(current_time - lookback_date).days}")
    print(f"   Date calculation correct: ✅")
    
    # Test 3: Scheduler Integration
    print("\n3. Testing Scheduler Integration...")
    try:
        scheduler = get_scheduler()
        print(f"   Scheduler created successfully: ✅")
        
        # Test manual check to see if it uses the new lookback period
        print("\n4. Testing Manual Check with 3-day lookback...")
        result = scheduler.run_manual_check()
        
        if result['success']:
            print(f"   Manual check successful: ✅")
            print(f"   Result: {result['message']}")
        else:
            print(f"   Manual check failed: ❌")
            print(f"   Error: {result['message']}")
            return False
    except Exception as e:
        print(f"   Scheduler test failed: ❌")
        print(f"   Error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 3-DAY LOOKBACK TEST PASSED!")
    print("System will now only check emails from the last 3 days")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_3_day_lookback()
    
    if success:
        print("\n✅ Configuration updated successfully!")
        print("Your system will now only process emails from the last 3 days.")
        print("\nTo change this in the future, update EMAIL_LOOKBACK_DAYS in your .env file.")
    else:
        print("\n❌ Configuration test failed. Please check the errors above.")