#!/usr/bin/env python
"""
Database migration script to create jira_xray_settings table
Run this script: python migrate_jira_xray_table.py
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from flask_app import create_app, db
from flask_app.models import JiraXraySettings

def migrate():
    """Create the jira_xray_settings table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            
            # Check if table exists
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'jira_xray_settings' in tables:
                print("✓ jira_xray_settings table created/verified successfully")
                print("\nTable structure:")
                columns = inspector.get_columns('jira_xray_settings')
                for col in columns:
                    print(f"  - {col['name']}: {col['type']}")
                return True
            else:
                print("✗ Failed to create jira_xray_settings table")
                return False
                
        except Exception as e:
            print(f"✗ Migration error: {e}")
            return False

if __name__ == '__main__':
    success = migrate()
    sys.exit(0 if success else 1)
