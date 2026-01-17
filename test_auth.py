"""
Script untuk testing fitur-fitur authentication baru
Run: python test_auth.py
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

def print_response(title, response):
    print(f"\n{'='*60}")
    print(f"🔹 {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

def test_register():
    """Test registrasi user baru"""
    print("\n🚀 Testing User Registration...")
    data = {
        "email": f"test_{datetime.now().timestamp()}@example.com",
        "password": "SecurePass123!"
    }
    response = requests.post(f"{BASE_URL}/api/auth/register", json=data)
    print_response("Register New User", response)
    return response.json() if response.status_code == 201 else None

def test_login_success(email, password):
    """Test login sukses"""
    print("\n✅ Testing Successful Login...")
    data = {
        "email": email,
        "password": password
    }
    response = requests.post(f"{BASE_URL}/api/auth/login", json=data)
    print_response("Login Success", response)
    return response.json().get('data', {}) if response.status_code == 200 else None

def test_login_wrong_password(email):
    """Test login dengan password salah (test brute force protection)"""
    print("\n❌ Testing Failed Login (Brute Force Protection)...")
    
    for i in range(6):
        print(f"\nAttempt {i+1}/6...")
        data = {
            "email": email,
            "password": "WrongPassword123"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=data)
        print_response(f"Login Attempt {i+1}", response)
        
        if response.status_code == 403:
            print("🔒 Account locked after too many failed attempts!")
            break

def test_api_key_access(api_key):
    """Test akses endpoint dengan API key"""
    print("\n🔑 Testing API Key Access...")
    
    # Test endpoint yang butuh auth (contoh: admin endpoint)
    headers = {"X-API-KEY": api_key}
    response = requests.get(f"{BASE_URL}/api/admin/users", headers=headers)
    print_response("API Key Access Test", response)

def test_api_key_expiration():
    """Test API key yang expired"""
    print("\n⏰ Testing Expired API Key...")
    
    # Gunakan API key yang expired (fake)
    headers = {"X-API-KEY": "expired_api_key_12345"}
    response = requests.get(f"{BASE_URL}/api/admin/users", headers=headers)
    print_response("Expired API Key Test", response)

def test_password_reset_request(email):
    """Test request password reset"""
    print("\n🔄 Testing Password Reset Request...")
    data = {"email": email}
    response = requests.post(f"{BASE_URL}/api/auth/request-password-reset", json=data)
    print_response("Password Reset Request", response)
    return response.json().get('reset_token') if response.status_code == 200 else None

def test_password_reset(token, new_password):
    """Test reset password dengan token"""
    print("\n🔓 Testing Password Reset...")
    data = {
        "token": token,
        "new_password": new_password
    }
    response = requests.post(f"{BASE_URL}/api/auth/reset-password", json=data)
    print_response("Password Reset", response)

def test_regenerate_api_key(current_api_key):
    """Test regenerate API key"""
    print("\n🔄 Testing API Key Regeneration...")
    headers = {"X-API-KEY": current_api_key}
    response = requests.post(f"{BASE_URL}/api/auth/regenerate-api-key", headers=headers)
    print_response("Regenerate API Key", response)
    return response.json().get('new_api_key') if response.status_code == 200 else None

def test_quota_tracking(api_key):
    """Test usage tracking"""
    print("\n📊 Testing Usage Quota Tracking...")
    headers = {"X-API-KEY": api_key}
    
    # Simulate multiple API calls
    for i in range(3):
        print(f"\nAPI Call {i+1}...")
        response = requests.get(f"{BASE_URL}/api/admin/users", headers=headers)
        print(f"Remaining Quota: Check in response")

def main():
    """Main testing flow"""
    print("\n" + "="*60)
    print("🧪 AUTH SYSTEM TEST SUITE")
    print("="*60)
    
    try:
        # 1. Test Register
        user_data = test_register()
        if not user_data:
            print("❌ Registration failed. Exiting...")
            return
        
        email = user_data['user']['email']
        
        # 2. Test Login Success
        login_data = test_login_success(email, "SecurePass123!")
        if not login_data:
            print("❌ Login failed. Exiting...")
            return
        
        # Note: Untuk mendapatkan API key, kita perlu endpoint khusus atau ambil dari response
        # Untuk testing penuh, bisa tambahkan endpoint /api/auth/me
        
        # 3. Test Failed Login (Brute Force Protection)
        test_login_wrong_password(email)
        
        # 4. Test Password Reset Flow
        # reset_token = test_password_reset_request(email)
        # if reset_token:
        #     test_password_reset(reset_token, "NewSecurePass456!")
        
        print("\n" + "="*60)
        print("✅ TESTING COMPLETED")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to server.")
        print("Make sure Flask server is running on http://localhost:5000")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
