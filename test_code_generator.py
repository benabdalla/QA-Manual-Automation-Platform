#!/usr/bin/env python3
"""
Test script to verify LLM code generation without full Flask app
"""

import sys
import json

def test_llm_imports():
    """Test that all LLM packages can be imported"""
    print("Testing LLM package imports...")
    
    try:
        from openai import OpenAI
        print("[OK] OpenAI package imported successfully")
    except ImportError as e:
        print(f"[FAIL] OpenAI import failed: {e}")
        return False
    
    try:
        import google.genai as genai
        print("[OK] Google Gemini package imported successfully")
    except ImportError as e:
        print(f"[FAIL] Gemini import failed: {e}")
        return False
    
    try:
        import anthropic
        print("[OK] Anthropic package imported successfully")
    except ImportError as e:
        print(f"[FAIL] Anthropic import failed: {e}")
        return False
    
    return True


def test_template_code_generation():
    """Test the template code generation function"""
    print("\nTesting template code generation...")
    
    from flask_app.routes.api import generate_template_code
    
    scenario = """
    Given I am on the login page
    When I enter valid credentials
    And I click the login button
    Then I should see the dashboard
    """
    
    # Test Cypress JavaScript
    code = generate_template_code("Cypress", "JavaScript", scenario)
    if "describe('Test Suite'" in code and "cy.visit" in code:
        print("[OK] Cypress JavaScript template generated correctly")
    else:
        print("[FAIL] Cypress JavaScript template failed")
        return False
    
    # Test Playwright Python
    code = generate_template_code("Playwright", "Python", scenario)
    if "sync_playwright" in code and "page.goto" in code:
        print("[OK] Playwright Python template generated correctly")
    else:
        print("[FAIL] Playwright Python template failed")
        return False
    
    # Test Selenium Java
    code = generate_template_code("Selenium", "Java", scenario)
    if "WebDriver" in code and "navigate" in code:
        print("[OK] Selenium Java template generated correctly")
    else:
        print("[FAIL] Selenium Java template failed")
        return False
    
    return True


def main():
    print("=" * 60)
    print("Code Generator Test Suite")
    print("=" * 60)
    
    if not test_llm_imports():
        print("\n[FAIL] LLM imports failed - please install packages")
        sys.exit(1)
    
    if not test_template_code_generation():
        print("\n[FAIL] Template generation failed")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("[OK] All tests passed! Code generator is ready to use.")
    print("=" * 60)
    print("\nTo use with your Flask app:")
    print("1. Start the Flask app: python flask_app/app.py")
    print("2. Go to: http://localhost:5000/code-generator")
    print("3. Select framework, language, and enter Gherkin scenario")
    print("4. Click 'Create Agent & Generate' button")
    print("5. Your test code will be generated!")


if __name__ == "__main__":
    main()
