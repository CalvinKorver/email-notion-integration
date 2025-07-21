#!/usr/bin/env python3
"""
Database migration CLI tool.
Usage: python migrate.py [command] [options]
"""

import sys
import argparse
import os
from migration_manager import MigrationManager
import config


def main():
    parser = argparse.ArgumentParser(description='Database migration tool')
    parser.add_argument(
        'command',
        choices=['status', 'migrate', 'rollback', 'create'],
        help='Migration command to run'
    )
    parser.add_argument(
        '--target',
        help='Target migration name (for migrate/rollback commands)'
    )
    parser.add_argument(
        '--name',
        help='Migration name (for create command)'
    )
    parser.add_argument(
        '--db-path',
        default=config.DATABASE_PATH,
        help=f'Database path (default: {config.DATABASE_PATH})'
    )
    
    args = parser.parse_args()
    
    # Initialize migration manager
    mm = MigrationManager(args.db_path)
    
    if args.command == 'status':
        status = mm.get_migration_status()
        print(f"Database: {status['database_path']}")
        print(f"Migrations directory: {status['migrations_directory']}")
        print(f"Database up to date: {status['database_up_to_date']}")
        print()
        
        if status['applied_migrations']:
            print("Applied migrations:")
            for migration in status['applied_migrations']:
                print(f"  ✓ {migration}")
        else:
            print("No migrations applied yet")
        
        if status['pending_migrations']:
            print("\nPending migrations:")
            for migration in status['pending_migrations']:
                print(f"  • {migration}")
        else:
            print("\nNo pending migrations")
    
    elif args.command == 'migrate':
        print("Running migrations...")
        result = mm.migrate(args.target)
        
        if result['success']:
            if result['applied_migrations']:
                print(f"✓ {result['message']}")
                for migration in result['applied_migrations']:
                    print(f"  ✓ Applied: {migration}")
            else:
                print("✓ Database is already up to date")
        else:
            print(f"✗ Migration failed: {result['message']}")
            sys.exit(1)
    
    elif args.command == 'rollback':
        if not args.target:
            print("Error: --target migration name is required for rollback")
            sys.exit(1)
        
        print(f"Rolling back migration: {args.target}")
        success = mm.rollback_migration(args.target)
        
        if success:
            print(f"✓ Successfully rolled back: {args.target}")
        else:
            print(f"✗ Failed to rollback: {args.target}")
            sys.exit(1)
    
    elif args.command == 'create':
        if not args.name:
            print("Error: --name is required for creating migrations")
            sys.exit(1)
        
        # Get next migration number
        available = mm.get_available_migrations()
        if available:
            # Extract numbers from existing migrations
            numbers = []
            for migration in available:
                if migration.split('_')[0].isdigit():
                    numbers.append(int(migration.split('_')[0]))
            next_number = max(numbers) + 1 if numbers else 1
        else:
            next_number = 1
        
        # Create migration file
        migration_name = f"{next_number:03d}_{args.name}"
        migration_path = os.path.join(mm.migrations_dir, f"{migration_name}.py")
        
        if os.path.exists(migration_path):
            print(f"Error: Migration file already exists: {migration_path}")
            sys.exit(1)
        
        # Create migration template
        template = f'''"""
{args.name.replace('_', ' ').title()} migration.
"""

def up(cursor):
    """Apply the migration."""
    # Add your migration code here
    pass


def down(cursor):
    """Rollback the migration."""
    # Add your rollback code here
    pass
'''
        
        with open(migration_path, 'w') as f:
            f.write(template)
        
        print(f"✓ Created migration: {migration_path}")
        print("Edit the file to add your migration code.")


if __name__ == '__main__':
    main()