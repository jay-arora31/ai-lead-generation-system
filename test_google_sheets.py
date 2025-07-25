"""
Test script for Google Sheets integration
Run this to verify your Google Sheets Apps Script is working correctly
"""
import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

def test_header_functionality():
    """Test if headers are properly detected and added"""
    
    load_dotenv()
    endpoint = os.getenv("GOOGLE_SHEETS_ENDPOINT")
    
    if not endpoint:
        print("❌ Error: GOOGLE_SHEETS_ENDPOINT not found in .env file")
        return False
    
    print("🔧 Testing header functionality...")
    
    # Test with empty data to trigger header check
    payload = {
        "action": "testHeaders"
    }
    
    try:
        response = requests.post(
            endpoint,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"📋 Header test response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"⚠️  Header test returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"⚠️  Could not test header functionality: {str(e)}")
        return False

def test_google_sheets_integration():
    """Test the Google Sheets Apps Script endpoint"""
    
    # Load environment variables
    load_dotenv()
    endpoint = os.getenv("GOOGLE_SHEETS_ENDPOINT")
    
    if not endpoint:
        print("❌ Error: GOOGLE_SHEETS_ENDPOINT not found in .env file")
        print("Please add your Google Apps Script deployment URL to .env file")
        return False
    
    print(f"🔍 Testing Google Sheets endpoint: {endpoint}")
    
    # Create test data
    test_data = [
        {
            "company_name": "Test Hardware Company",
            "website": "https://testhardware.com",
            "employee_count": 150,
            "industry": "Technology",
            "location": "San Francisco, CA",
            "business_summary": "A test company that develops hardware solutions for businesses",
            "hardware_opportunities": "Workstations, Servers, Networking",
            "decision_maker_hint": "CTO",
            "contact_emails": "cto@testhardware.com",
            "decision_makers": "Jane Smith (CTO)",
            "personalized_message": "Subject: Test Hardware Solutions\n\nHi Jane,\n\nThis is a test message for hardware solutions...",
            "generated_at": datetime.now().isoformat()
        }
    ]
    
    # Prepare payload
    payload = {
        "action": "addLeads",
        "data": test_data
    }
    
    try:
        print("📡 Sending test data to Google Sheets...")
        
        # Send request
        response = requests.post(
            endpoint,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📋 Response Data: {json.dumps(result, indent=2)}")
            
            if result.get('success', False):
                print("✅ SUCCESS: Test data was successfully added to Google Sheets!")
                print(f"   - Rows added: {result.get('rowsAdded', 'Unknown')}")
                print(f"   - Sheet ID: {result.get('sheetId', 'Unknown')}")
                print(f"   - Sheet Name: {result.get('sheetName', 'Unknown')}")
                return True
            else:
                print("❌ FAILED: Google Sheets returned an error")
                print(f"Error message: {result.get('message', 'Unknown error')}")
                if 'errorDetails' in result:
                    print(f"Error details: {result['errorDetails']}")
                return False
        else:
            print(f"❌ FAILED: HTTP Error {response.status_code}")
            print(f"Response: {response.text[:500]}...")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT: Request to Google Sheets took too long")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ REQUEST ERROR: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {str(e)}")
        return False

def check_environment():
    """Check if environment is properly configured"""
    print("🔧 Checking environment configuration...")
    
    load_dotenv()
    
    required_vars = [
        "APOLLO_API_KEY",
        "OPENAI_API_KEY", 
        "HUNTER_API_KEY"
    ]
    
    optional_vars = [
        "GOOGLE_SHEETS_ENDPOINT"
    ]
    
    missing_required = []
    missing_optional = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
        else:
            print(f"✅ {var}: Configured")
    
    for var in optional_vars:
        if not os.getenv(var):
            missing_optional.append(var)
        else:
            print(f"✅ {var}: Configured")
    
    if missing_required:
        print(f"\n❌ Missing required environment variables: {', '.join(missing_required)}")
        return False
    
    if missing_optional:
        print(f"\n⚠️  Missing optional environment variables: {', '.join(missing_optional)}")
        print("   Google Sheets integration will not work without GOOGLE_SHEETS_ENDPOINT")
    
    return True

if __name__ == "__main__":
    print("🧪 Google Sheets Integration Test")
    print("=" * 50)
    
    # Check environment first
    env_ok = check_environment()
    
    if not env_ok:
        print("\n❌ Environment check failed. Please fix the issues above.")
        exit(1)
    
    print("\n" + "=" * 50)
    
    # Test Google Sheets integration
    if os.getenv("GOOGLE_SHEETS_ENDPOINT"):
        # Test header functionality first
        print("🧪 Testing header functionality...")
        header_ok = test_header_functionality()
        
        print("\n" + "-" * 30)
        
        # Test full integration
        print("🧪 Testing full integration...")
        sheets_ok = test_google_sheets_integration()
        
        if sheets_ok and header_ok:
            print("\n🎉 All tests passed! Your Google Sheets integration is working correctly.")
            print("✅ Headers will be automatically added if missing")
            print("✅ Lead data is being saved properly")
        else:
            print("\n❌ Google Sheets test failed. Please check your Apps Script setup.")
            print("\nTroubleshooting tips:")
            print("1. Make sure your Google Apps Script is deployed as a web app")
            print("2. Ensure 'Who has access' is set to 'Anyone'")
            print("3. Check that SHEET_ID in your Apps Script matches your Google Sheets ID")
            print("4. Verify your Google Sheets document exists and is accessible")
            print("5. Headers will be automatically added - no manual setup needed")
    else:
        print("\n⚠️  Google Sheets endpoint not configured. Skipping integration test.")
        print("If you want to use Google Sheets, please set up GOOGLE_SHEETS_ENDPOINT in .env")
    
    print("\n" + "=" * 50)
    print("Test completed!") 