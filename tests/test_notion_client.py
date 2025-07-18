import unittest
from unittest.mock import Mock, patch
from datetime import datetime
import sys
import os

# Add the parent directory to the path to import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from notion_api import NotionClient

class TestNotionClient(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_token = "secret_test_token"
        self.mock_database_id = "test_database_id"
        self.sample_recruiter_data = {
            "recruiter_name": "John Doe",
            "recruiter_email": "john.doe@company.com",
            "company": "Tech Corp",
            "position": "Software Engineer",
            "location": "San Francisco, CA",
            "status": "Recruiter Screen",
            "date_received": datetime(2023, 12, 1, 10, 30)
        }
    
    @patch('notion_api.Client')
    def test_init(self, mock_client_class):
        """Test NotionClient initialization."""
        client = NotionClient(self.mock_token)
        self.assertEqual(client.token, self.mock_token)
        mock_client_class.assert_called_once_with(auth=self.mock_token)
    
    @patch('notion_api.Client')
    def test_test_connection_success(self, mock_client_class):
        """Test successful connection test."""
        mock_client = Mock()
        mock_client.users.me.return_value = {"name": "Test User"}
        mock_client_class.return_value = mock_client
        
        client = NotionClient(self.mock_token)
        result = client.test_connection()
        
        self.assertTrue(result)
        mock_client.users.me.assert_called_once()
    
    @patch('notion_api.Client')
    def test_test_connection_failure(self, mock_client_class):
        """Test failed connection test."""
        mock_client = Mock()
        mock_client.users.me.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client
        
        client = NotionClient(self.mock_token)
        result = client.test_connection()
        
        self.assertFalse(result)
    
    @patch('notion_api.Client')
    def test_get_database_info_success(self, mock_client_class):
        """Test successful database info retrieval."""
        mock_client = Mock()
        mock_database = {
            "title": [{"plain_text": "Test Database"}]
        }
        mock_client.databases.retrieve.return_value = mock_database
        mock_client_class.return_value = mock_client
        
        client = NotionClient(self.mock_token)
        result = client.get_database_info(self.mock_database_id)
        
        self.assertEqual(result, mock_database)
        mock_client.databases.retrieve.assert_called_once_with(database_id=self.mock_database_id)
    
    @patch('notion_api.Client')
    def test_create_recruiter_entry_success(self, mock_client_class):
        """Test successful recruiter entry creation."""
        mock_client = Mock()
        mock_page = {"id": "new_page_id"}
        mock_client.pages.create.return_value = mock_page
        mock_client_class.return_value = mock_client
        
        client = NotionClient(self.mock_token)
        result = client.create_recruiter_entry(self.mock_database_id, self.sample_recruiter_data)
        
        self.assertEqual(result, "new_page_id")
        mock_client.pages.create.assert_called_once()
        
        # Verify the call arguments
        call_args = mock_client.pages.create.call_args
        self.assertEqual(call_args[1]['parent']['database_id'], self.mock_database_id)
        
        # Check that properties were formatted correctly
        properties = call_args[1]['properties']
        self.assertEqual(properties['Company']['title'][0]['text']['content'], "Tech Corp")
        self.assertEqual(properties['Recruiter Name']['rich_text'][0]['text']['content'], "John Doe")
        self.assertEqual(properties['Job Title']['rich_text'][0]['text']['content'], "Software Engineer")
        self.assertEqual(properties['Stage']['status']['name'], "Recruiter Screen")
        self.assertEqual(properties['Application Date']['date']['start'], "2023-12-01")
    
    @patch('notion_api.Client')
    def test_create_recruiter_entry_failure(self, mock_client_class):
        """Test failed recruiter entry creation."""
        mock_client = Mock()
        mock_client.pages.create.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client
        
        client = NotionClient(self.mock_token)
        result = client.create_recruiter_entry(self.mock_database_id, self.sample_recruiter_data)
        
        self.assertIsNone(result)
    
    @patch('notion_api.datetime')
    @patch('notion_api.Client')
    def test_update_recruiter_entry_success(self, mock_client_class, mock_datetime):
        """Test successful recruiter entry update."""
        # Mock datetime to return a fixed date
        mock_datetime.now.return_value = datetime(2023, 12, 1, 10, 0, 0)
        
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        client = NotionClient(self.mock_token)
        updates = {"status": "Phone Screen", "notes": "Great conversation"}
        result = client.update_recruiter_entry("page_id", updates)
        
        self.assertTrue(result)
        mock_client.pages.update.assert_called_once()
        
        # Verify the call arguments
        call_args = mock_client.pages.update.call_args
        self.assertEqual(call_args[1]['page_id'], "page_id")
        properties = call_args[1]['properties']
        self.assertEqual(properties['Stage']['status']['name'], "Phone Screen")
        self.assertEqual(properties['Last Contact Date']['date']['start'], "2023-12-01")
    
    @patch('notion_api.Client')
    def test_search_entries_success(self, mock_client_class):
        """Test successful entry search."""
        mock_client = Mock()
        mock_results = [{"id": "entry1"}, {"id": "entry2"}]
        mock_client.databases.query.return_value = {"results": mock_results}
        mock_client_class.return_value = mock_client
        
        client = NotionClient(self.mock_token)
        result = client.search_entries(self.mock_database_id, "test query")
        
        self.assertEqual(result, mock_results)
        mock_client.databases.query.assert_called_once()

if __name__ == '__main__':
    unittest.main()