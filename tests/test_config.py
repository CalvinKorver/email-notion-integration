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
    
    # Test 1: Check that basic config values are loaded
    assert hasattr(config, 'DATABASE_PATH')
    assert hasattr(config, 'FLASK_ENV')
    assert hasattr(config, 'FLASK_HOST')
    assert hasattr(config, 'FLASK_PORT')
    assert hasattr(config, 'CHECK_INTERVAL')
    
    # Test 2: Check users configuration
    assert hasattr(config, 'USERS')
    assert len(config.USERS) > 0
    
    # Test 3: Test user lookup functions
    test_email = config.USERS[0]['email']
    user = config.get_user_by_email(test_email)
    assert user is not None
    assert user['name'] == config.USERS[0]['name']
    
    # Test lookup with non-existent email
    user = config.get_user_by_email("nonexistent@example.com")
    assert user is None
    
    # Test 4: Configuration validation
    errors = config.validate_config()
    assert isinstance(errors, list)
    
    # Test 5: Configuration summary
    summary = config.get_config_summary()
    assert isinstance(summary, dict)
    assert 'user_configured' in summary