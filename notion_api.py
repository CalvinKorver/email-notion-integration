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
                - recruiter_name: str (optional, defaults to placeholder)
                - recruiter_email: str (stored in Notes field)
                - company: str (optional, defaults to placeholder)
                - position: str (optional, defaults to placeholder)
                - location: str (stored in Notes field)
                - status: str (defaults to "Applied")
                - date_received: datetime (only set on creation)
        
        Returns:
            The page ID of the created entry, or None if failed
        """
        try:
            current_time = datetime.now()
            
            # Format data for your actual Notion database schema
            properties = {
                "Company": {
                    "title": [
                        {
                            "text": {
                                "content": recruiter_data.get("company", "PLACEHOLDER_COMPANY")
                            }
                        }
                    ]
                },
                "Recruiter Name": {
                    "rich_text": [
                        {
                            "text": {
                                "content": recruiter_data.get("recruiter_name", "PLACEHOLDER_RECRUITER")
                            }
                        }
                    ]
                },
                "Job Title": {
                    "rich_text": [
                        {
                            "text": {
                                "content": recruiter_data.get("position", "PLACEHOLDER_POSITION")
                            }
                        }
                    ]
                },
                "Stage": {
                    "status": {
                        "name": recruiter_data.get("status", "Applied")
                    }
                },
                "Last Contact Date": {
                    "date": {
                        "start": current_time.strftime("%Y-%m-%d")
                    }
                }
            }
            
            # Add application date (only set on creation)
            if "date_received" in recruiter_data and recruiter_data["date_received"]:
                date_received = recruiter_data["date_received"]
                if isinstance(date_received, datetime):
                    properties["Application Date"] = {
                        "date": {
                            "start": date_received.strftime("%Y-%m-%d")
                        }
                    }
            else:
                # Default to current date if no date provided
                properties["Application Date"] = {
                    "date": {
                        "start": current_time.strftime("%Y-%m-%d")
                    }
                }
            
            # Create the page
            page = self.client.pages.create(
                parent={"database_id": database_id},
                properties=properties
            )
            
            page_id = page["id"]
            logger.info(f"Created Notion entry for {recruiter_data.get('recruiter_name', 'PLACEHOLDER_RECRUITER')} at {recruiter_data.get('company', 'PLACEHOLDER_COMPANY')}")
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
                - status: str (updates Stage field)
                - recruiter_name: str (updates Recruiter Name field)
                - company: str (updates Company field)
                - position: str (updates Job Title field)
                
        Note: 
            - Last Contact Date is always updated to current date
            - Follow-up Needed and Notes are never modified via API
            - Application Date is never modified after creation
        
        Returns:
            True if successful, False otherwise
        """
        try:
            current_time = datetime.now()
            properties = {}
            
            # Always update Last Contact Date
            properties["Last Contact Date"] = {
                "date": {
                    "start": current_time.strftime("%Y-%m-%d")
                }
            }
            
            # Map updates to Notion property format
            if "status" in updates:
                properties["Stage"] = {
                    "status": {
                        "name": updates["status"]
                    }
                }
            
            if "recruiter_name" in updates:
                properties["Recruiter Name"] = {
                    "rich_text": [
                        {
                            "text": {
                                "content": updates["recruiter_name"]
                            }
                        }
                    ]
                }
            
            if "company" in updates:
                properties["Company"] = {
                    "title": [
                        {
                            "text": {
                                "content": updates["company"]
                            }
                        }
                    ]
                }
            
            if "position" in updates:
                properties["Job Title"] = {
                    "rich_text": [
                        {
                            "text": {
                                "content": updates["position"]
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