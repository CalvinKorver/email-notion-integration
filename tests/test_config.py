#!/usr/bin/env python3
"""
Test script for configuration module.
"""

import sys
import os

# Add parent directory to path to import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config


def test_config_loading():
    """Test that configuration loads correctly."""
    
    print("Testing configuration loading...")
    
    # Test 1: Check that basic config values are loaded
    print(f"\n1. Basic configuration:")
    print(f"   Database path: {config.DATABASE_PATH}")
    print(f"   Flask environment: {config.FLASK_ENV}")
    print(f"   Flask host: {config.FLASK_HOST}")
    print(f"   Flask port: {config.FLASK_PORT}")
    print(f"   Mailgun domain: {config.MAILGUN_DOMAIN}")
    
    # Test 2: Check users configuration
    print(f"\n2. Users configuration:")
    print(f"   Number of users: {len(config.USERS)}")
    for i, user in enumerate(config.USERS):
        print(f"   User {i+1}: {user['name']} ({user['mailgun_email']})")
    
    # Test 3: Test user lookup functions
    print(f"\n3. Testing user lookup functions:")
    
    # Test lookup by Mailgun email
    test_email = config.USERS[0]['mailgun_email']
    user = config.get_user_by_mailgun_email(test_email)
    print(f"   Lookup by Mailgun email '{test_email}': {user['name'] if user else 'Not found'}")
    
    # Test lookup by regular email
    test_email = config.USERS[0]['email']
    user = config.get_user_by_email(test_email)
    print(f"   Lookup by regular email '{test_email}': {user['name'] if user else 'Not found'}")
    
    # Test lookup with non-existent email
    user = config.get_user_by_mailgun_email("nonexistent@example.com")
    print(f"   Lookup non-existent email: {user}")
    
    # Test 4: Configuration validation
    print(f"\n4. Configuration validation:")
    errors = config.validate_config()
    if errors:
        print(f"   Found {len(errors)} configuration errors:")
        for error in errors:
            print(f"   - {error}")
    else:
        print("   No configuration errors found!")
    
    # Test 5: Configuration summary
    print(f"\n5. Configuration summary:")
    summary = config.get_config_summary()
    for key, value in summary.items():
        if key == 'config_errors' and value:
            print(f"   {key}: {len(value)} errors")
        else:
            print(f"   {key}: {value}")
    
    print("\n✅ Configuration testing completed!")


if __name__ == "__main__":
    test_config_loading()