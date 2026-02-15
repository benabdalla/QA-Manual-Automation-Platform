#!/usr/bin/env python
"""
Test script for Jira-Xray Settings functionality
Run this script to verify all components are working correctly
"""

import os
import sys
import json
from datetime import datetime

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

from flask_app import create_app, db
from flask_app.models import User, JiraXraySettings


def print_header(text):
    """Print a formatted header"""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")


def print_success(text):
    """Print success message"""
    print(f"✅ {text}")


def print_error(text):
    """Print error message"""
    print(f"❌ {text}")


def print_info(text):
    """Print info message"""
    print(f"ℹ️  {text}")


def test_database_connection():
    """Test database connection"""
    print_header("1. Testing Database Connection")
    try:
        app = create_app()
        with app.app_context():
            # Try to execute a simple query
            result = db.session.execute('SELECT 1')
            print_success("Database connection successful")
            return True
    except Exception as e:
        print_error(f"Database connection failed: {e}")
        return False


def test_model_creation():
    """Test model creation and structure"""
    print_header("2. Testing JiraXraySettings Model")
    try:
        app = create_app()
        with app.app_context():
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'jira_xray_settings' not in tables:
                print_error("jira_xray_settings table does not exist")
                print_info("Run migration: python migrate_jira_xray_table.py")
                return False
            
            print_success("jira_xray_settings table exists")
            
            # Get table structure
            columns = inspector.get_columns('jira_xray_settings')
            print_info(f"Table has {len(columns)} columns:")
            
            for col in columns:
                print(f"    • {col['name']}: {col['type']}")
            
            return True
    except Exception as e:
        print_error(f"Model test failed: {e}")
        return False


def test_crud_operations():
    """Test Create, Read, Update, Delete operations"""
    print_header("3. Testing CRUD Operations")
    try:
        app = create_app()
        with app.app_context():
            # Get or create a test user
            test_user = User.query.filter_by(username='test_jira_user').first()
            if not test_user:
                test_user = User(
                    username='test_jira_user',
                    email='test_jira@example.com'
                )
                test_user.set_password('testpass123')
                db.session.add(test_user)
                db.session.commit()
                print_success("Test user created")
            else:
                print_info("Using existing test user")
            
            # CREATE
            print_info("Testing CREATE...")
            settings = JiraXraySettings(
                user_id=test_user.id,
                jira_requirement_key='TEST-001',
                jira_username='test@example.com',
                jira_url='https://test.atlassian.net',
                jira_api_token='test-token',
                project_key='TEST',
                version_name='v1.0',
                xray_folder_path='/test/path',
                xray_client_id='test-client',
                xray_client_secret='test-secret',
                num_test_cases=10,
                is_active=True
            )
            db.session.add(settings)
            db.session.commit()
            print_success(f"Created settings with ID: {settings.id}")
            
            # READ
            print_info("Testing READ...")
            retrieved = JiraXraySettings.query.filter_by(
                user_id=test_user.id
            ).first()
            if retrieved:
                print_success(f"Retrieved settings: {retrieved.project_key}")
            else:
                print_error("Failed to retrieve settings")
                return False
            
            # UPDATE
            print_info("Testing UPDATE...")
            retrieved.num_test_cases = 20
            retrieved.version_name = 'v2.0'
            db.session.commit()
            print_success("Updated settings successfully")
            
            # VERIFY UPDATE
            verify = JiraXraySettings.query.get(retrieved.id)
            if verify.num_test_cases == 20 and verify.version_name == 'v2.0':
                print_success("Update verification passed")
            else:
                print_error("Update verification failed")
                return False
            
            # DELETE
            print_info("Testing DELETE...")
            setting_id = retrieved.id
            db.session.delete(retrieved)
            db.session.commit()
            
            # Verify deletion
            deleted = JiraXraySettings.query.get(setting_id)
            if deleted is None:
                print_success("Deletion verified successfully")
            else:
                print_error("Deletion verification failed")
                return False
            
            return True
            
    except Exception as e:
        print_error(f"CRUD operations failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_routes():
    """Test API routes exist"""
    print_header("4. Testing API Routes")
    try:
        app = create_app()
        
        # Get all routes
        routes = []
        for rule in app.url_map.iter_rules():
            if 'jira-xray' in rule.rule:
                routes.append(rule)
        
        if not routes:
            print_error("No Jira-Xray routes found")
            return False
        
        print_success(f"Found {len(routes)} Jira-Xray routes:")
        
        for route in routes:
            methods = ','.join(route.methods - {'HEAD', 'OPTIONS'})
            print(f"    • {route.rule} [{methods}]")
        
        expected_routes = {
            '/api/jira-xray-settings': ['GET', 'POST'],
            '/api/jira-xray-settings/<int:settings_id>': ['GET', 'PUT', 'DELETE']
        }
        
        found_routes = {str(rule.rule): rule.methods for rule in routes}
        
        for expected, methods in expected_routes.items():
            if expected in found_routes:
                print_success(f"Route {expected} exists")
            else:
                print_error(f"Missing route: {expected}")
                return False
        
        return True
        
    except Exception as e:
        print_error(f"Route test failed: {e}")
        return False


def test_template_exists():
    """Test if template file exists"""
    print_header("5. Testing Template File")
    template_path = 'flask_app/templates/main/jira_xray_settings.html'
    
    if os.path.exists(template_path):
        print_success(f"Template exists: {template_path}")
        
        with open(template_path, 'r') as f:
            content = f.read()
            if 'Jira-Xray Configuration' in content:
                print_success("Template content verified")
                return True
            else:
                print_error("Template content not as expected")
                return False
    else:
        print_error(f"Template not found: {template_path}")
        return False


def test_model_methods():
    """Test model methods"""
    print_header("6. Testing Model Methods")
    try:
        app = create_app()
        with app.app_context():
            # Get test user
            test_user = User.query.filter_by(username='test_jira_user').first()
            if not test_user:
                print_error("Test user not found")
                return False
            
            # Create test settings
            settings = JiraXraySettings(
                user_id=test_user.id,
                jira_requirement_key='METHOD-TEST',
                jira_username='method@test.com',
                jira_url='https://method.atlassian.net',
                project_key='METHOD',
                version_name='v1',
                xray_folder_path='/method/path',
                num_test_cases=5
            )
            db.session.add(settings)
            db.session.commit()
            
            # Test to_dict() method
            print_info("Testing to_dict() method...")
            data = settings.to_dict(include_secrets=False)
            
            required_fields = [
                'id', 'jira_requirement_key', 'jira_username',
                'jira_url', 'project_key', 'version_name',
                'xray_folder_path', 'num_test_cases', 'is_active'
            ]
            
            for field in required_fields:
                if field not in data:
                    print_error(f"Missing field in to_dict(): {field}")
                    return False
            
            print_success("to_dict() method works correctly")
            
            # Test with secrets
            data_with_secrets = settings.to_dict(include_secrets=True)
            if 'jira_api_token' in data_with_secrets:
                print_success("to_dict(include_secrets=True) works correctly")
            else:
                print_error("to_dict(include_secrets=True) missing secret fields")
                return False
            
            # Cleanup
            db.session.delete(settings)
            db.session.commit()
            
            return True
            
    except Exception as e:
        print_error(f"Model method test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests"""
    print_header("Jira-Xray Settings - Test Suite")
    print_info(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        'Database Connection': test_database_connection(),
        'Model Creation': test_model_creation(),
        'CRUD Operations': test_crud_operations(),
        'API Routes': test_api_routes(),
        'Template File': test_template_exists(),
        'Model Methods': test_model_methods(),
    }
    
    # Summary
    print_header("Test Summary")
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if failed == 0:
        print_success("All tests passed!")
        return True
    else:
        print_error(f"{failed} test(s) failed. See details above.")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    print("\n" + "="*70 + "\n")
    sys.exit(0 if success else 1)
