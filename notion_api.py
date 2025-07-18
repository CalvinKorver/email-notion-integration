import logging
from datetime import datetime
from typing import Dict, Optional, Any
from notion_client import Client
from notion_client.errors import APIResponseError, RequestTimeoutError

logger = logging.getLogger(__name__)

class NotionClient:
    """Wrapper for Notion API operations for recruiter tracking."""
    
    def __init__(self, token: str):
        """Initialize the Notion client with authentication token."""
        self.token = token
        self.client = Client(auth=token)
    
    def test_connection(self) -> bool:
        """Test the connection to Notion workspace."""
        try:
            # Try to get user info to verify token is valid
            user = self.client.users.me()
            logger.info(f"Successfully connected to Notion as: {user.get('name', 'Unknown')}")
            return True
        except APIResponseError as e:
            logger.error(f"Notion API authentication failed: {e}")
            return False
        except RequestTimeoutError as e:
            logger.error(f"Notion API timeout: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error testing Notion connection: {e}")
            return False
    
    def get_database_info(self, database_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a Notion database."""
        try:
            database = self.client.databases.retrieve(database_id=database_id)
            logger.info(f"Successfully retrieved database: {database.get('title', [{}])[0].get('plain_text', 'Unknown')}")
            return database
        except APIResponseError as e:
            logger.error(f"Failed to retrieve database {database_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error retrieving database: {e}")
            return None
    
    def create_recruiter_entry(self, database_id: str, recruiter_data: Dict[str, Any]) -> Optional[str]:
        """
        Create a new recruiter entry in the Notion database.
        
        Args:
            database_id: The ID of the Notion database
            recruiter_data: Dictionary containing recruiter information
                - recruiter_name: str
                - recruiter_email: str
                - company: str
                - position: str
                - location: str
                - status: str (defaults to "Recruiter Screen")
                - date_received: datetime
        
        Returns:
            The page ID of the created entry, or None if failed
        """
        try:
            # Format data for Notion API
            properties = {
                "Recruiter Name": {
                    "title": [
                        {
                            "text": {
                                "content": recruiter_data.get("recruiter_name", "Unknown")
                            }
                        }
                    ]
                },
                "Company": {
                    "rich_text": [
                        {
                            "text": {
                                "content": recruiter_data.get("company", "Unknown")
                            }
                        }
                    ]
                },
                "Position": {
                    "rich_text": [
                        {
                            "text": {
                                "content": recruiter_data.get("position", "Unknown")
                            }
                        }
                    ]
                },
                "Location": {
                    "rich_text": [
                        {
                            "text": {
                                "content": recruiter_data.get("location", "Unknown")
                            }
                        }
                    ]
                },
                "Status": {
                    "select": {
                        "name": recruiter_data.get("status", "Recruiter Screen")
                    }
                },
                "Email": {
                    "email": recruiter_data.get("recruiter_email", "")
                }
            }
            
            # Add date received if provided
            if "date_received" in recruiter_data and recruiter_data["date_received"]:
                date_received = recruiter_data["date_received"]
                if isinstance(date_received, datetime):
                    properties["Date Received"] = {
                        "date": {
                            "start": date_received.strftime("%Y-%m-%d")
                        }
                    }
            
            # Create the page
            page = self.client.pages.create(
                parent={"database_id": database_id},
                properties=properties
            )
            
            page_id = page["id"]
            logger.info(f"Created Notion entry for {recruiter_data.get('recruiter_name', 'Unknown')} at {recruiter_data.get('company', 'Unknown')}")
            return page_id
            
        except APIResponseError as e:
            logger.error(f"Failed to create Notion entry: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating Notion entry: {e}")
            return None
    
    def update_recruiter_entry(self, page_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update an existing recruiter entry in Notion.
        
        Args:
            page_id: The ID of the Notion page to update
            updates: Dictionary of fields to update
        
        Returns:
            True if successful, False otherwise
        """
        try:
            properties = {}
            
            # Map updates to Notion property format
            if "status" in updates:
                properties["Status"] = {
                    "select": {
                        "name": updates["status"]
                    }
                }
            
            if "notes" in updates:
                properties["Notes"] = {
                    "rich_text": [
                        {
                            "text": {
                                "content": updates["notes"]
                            }
                        }
                    ]
                }
            
            # Update the page
            self.client.pages.update(
                page_id=page_id,
                properties=properties
            )
            
            logger.info(f"Updated Notion entry {page_id}")
            return True
            
        except APIResponseError as e:
            logger.error(f"Failed to update Notion entry {page_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error updating Notion entry: {e}")
            return False
    
    def search_entries(self, database_id: str, query: str = "", filter_params: Optional[Dict] = None) -> list:
        """
        Search for entries in the Notion database.
        
        Args:
            database_id: The ID of the Notion database
            query: Search query string
            filter_params: Optional filter parameters
        
        Returns:
            List of matching entries
        """
        try:
            search_params = {
                "database_id": database_id,
                "page_size": 100
            }
            
            if query:
                search_params["query"] = query
            
            if filter_params:
                search_params["filter"] = filter_params
            
            response = self.client.databases.query(**search_params)
            return response.get("results", [])
            
        except APIResponseError as e:
            logger.error(f"Failed to search Notion database: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error searching Notion database: {e}")
            return []