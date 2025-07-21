"""
Database migration manager for handling schema changes.
"""

import sqlite3
import os
import glob
import importlib.util
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class MigrationManager:
    def __init__(self, db_path: str, migrations_dir: str = "migrations"):
        self.db_path = db_path
        self.migrations_dir = migrations_dir
        self.ensure_database_exists()
        self.ensure_migrations_table()
    
    def ensure_database_exists(self):
        """Ensure the database file exists."""
        if not os.path.exists(self.db_path):
            # Create empty database file
            open(self.db_path, 'a').close()
            logger.info(f"Created new database file: {self.db_path}")
    
    def ensure_migrations_table(self):
        """Create the migrations tracking table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    migration_name TEXT UNIQUE NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    def get_applied_migrations(self) -> List[str]:
        """Get list of already applied migrations."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT migration_name FROM schema_migrations ORDER BY migration_name")
            return [row[0] for row in cursor.fetchall()]
    
    def get_available_migrations(self) -> List[str]:
        """Get list of available migration files."""
        pattern = os.path.join(self.migrations_dir, "*.py")
        migration_files = glob.glob(pattern)
        
        # Filter out __init__.py and sort by filename
        migrations = []
        for file_path in migration_files:
            filename = os.path.basename(file_path)
            if filename != "__init__.py" and filename.endswith(".py"):
                migration_name = filename[:-3]  # Remove .py extension
                migrations.append(migration_name)
        
        return sorted(migrations)
    
    def get_pending_migrations(self) -> List[str]:
        """Get list of migrations that need to be applied."""
        applied = set(self.get_applied_migrations())
        available = self.get_available_migrations()
        
        pending = [migration for migration in available if migration not in applied]
        return sorted(pending)
    
    def load_migration_module(self, migration_name: str):
        """Load a migration module by name."""
        migration_file = os.path.join(self.migrations_dir, f"{migration_name}.py")
        
        if not os.path.exists(migration_file):
            raise FileNotFoundError(f"Migration file not found: {migration_file}")
        
        spec = importlib.util.spec_from_file_location(migration_name, migration_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        return module
    
    def apply_migration(self, migration_name: str) -> bool:
        """Apply a single migration."""
        try:
            logger.info(f"Applying migration: {migration_name}")
            
            # Load the migration module
            migration_module = self.load_migration_module(migration_name)
            
            # Check if the module has an 'up' function
            if not hasattr(migration_module, 'up'):
                raise AttributeError(f"Migration {migration_name} does not have an 'up' function")
            
            # Apply the migration
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Run the migration
                migration_module.up(cursor)
                
                # Record that this migration was applied
                cursor.execute(
                    "INSERT INTO schema_migrations (migration_name) VALUES (?)",
                    (migration_name,)
                )
                
                conn.commit()
            
            logger.info(f"Successfully applied migration: {migration_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply migration {migration_name}: {str(e)}")
            return False
    
    def rollback_migration(self, migration_name: str) -> bool:
        """Rollback a single migration."""
        try:
            logger.info(f"Rolling back migration: {migration_name}")
            
            # Load the migration module
            migration_module = self.load_migration_module(migration_name)
            
            # Check if the module has a 'down' function
            if not hasattr(migration_module, 'down'):
                logger.warning(f"Migration {migration_name} does not have a 'down' function, skipping rollback")
                return False
            
            # Rollback the migration
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Run the rollback
                migration_module.down(cursor)
                
                # Remove the migration record
                cursor.execute(
                    "DELETE FROM schema_migrations WHERE migration_name = ?",
                    (migration_name,)
                )
                
                conn.commit()
            
            logger.info(f"Successfully rolled back migration: {migration_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rollback migration {migration_name}: {str(e)}")
            return False
    
    def migrate(self, target_migration: str = None) -> Dict[str, Any]:
        """
        Run all pending migrations up to a target migration.
        If target_migration is None, run all pending migrations.
        """
        pending_migrations = self.get_pending_migrations()
        
        if not pending_migrations:
            logger.info("No pending migrations to apply")
            return {
                'success': True,
                'applied_migrations': [],
                'message': 'Database is up to date'
            }
        
        # Filter migrations if target is specified
        if target_migration:
            try:
                target_index = pending_migrations.index(target_migration)
                pending_migrations = pending_migrations[:target_index + 1]
            except ValueError:
                return {
                    'success': False,
                    'applied_migrations': [],
                    'message': f'Target migration not found: {target_migration}'
                }
        
        applied_migrations = []
        failed_migrations = []
        
        for migration_name in pending_migrations:
            if self.apply_migration(migration_name):
                applied_migrations.append(migration_name)
            else:
                failed_migrations.append(migration_name)
                break  # Stop on first failure
        
        if failed_migrations:
            return {
                'success': False,
                'applied_migrations': applied_migrations,
                'failed_migrations': failed_migrations,
                'message': f'Migration failed: {failed_migrations[0]}'
            }
        
        return {
            'success': True,
            'applied_migrations': applied_migrations,
            'message': f'Successfully applied {len(applied_migrations)} migration(s)'
        }
    
    def get_migration_status(self) -> Dict[str, Any]:
        """Get the current migration status."""
        applied = self.get_applied_migrations()
        available = self.get_available_migrations()
        pending = self.get_pending_migrations()
        
        return {
            'database_path': self.db_path,
            'migrations_directory': self.migrations_dir,
            'applied_migrations': applied,
            'available_migrations': available,
            'pending_migrations': pending,
            'database_up_to_date': len(pending) == 0
        }