"""
Quick Test: Verifikasi fitur auth baru berjalan dengan baik
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_quick():
    print("\n" + "="*60)
    print("🧪 QUICK AUTH TEST")
    print("="*60)
    
    # Test 1: Register
    print("\n1️⃣ Testing Register...")
    register_data = {
        "email": "quicktest@example.com",
        "password": "TestPass123!"
    }
    
    try:
        r = requests.post(f"{BASE_URL}/api/v1/auth/register", json=register_data)
        print(f"   Status: {r.status_code}")
        if r.status_code == 201:
            print("   ✅ Register berhasil!")
            user_data = r.json()
            print(f"   User ID: {user_data['user']['id']}")
        elif r.status_code == 400 and "Already Registered" in r.json().get('message', ''):
            print("   ℹ️  User sudah ada (OK)")
        else:
            print(f"   ❌ Error: {r.json()}")
            
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        return
    
    # Test 2: Login
    print("\n2️⃣ Testing Login...")
    try:
        r = requests.post(f"{BASE_URL}/api/v1/auth/login", json=register_data)
        print(f"   Status: {r.status_code}")
        if r.status_code == 200:
            print("   ✅ Login berhasil!")
            login_data = r.json()['data']
            api_key = login_data.get('api_key')
            print(f"   Email: {login_data['email']}")
            print(f"   Role: {login_data['role']}")
            if api_key:
                print(f"   API Key: {api_key[:20]}...")
            
            # Test 3: Get User Info
            if api_key:
                print("\n3️⃣ Testing Get User Info (/me)...")
                headers = {"X-API-KEY": api_key}
                r = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
                print(f"   Status: {r.status_code}")
                if r.status_code == 200:
                    print("   ✅ Get user info berhasil!")
                    user_info = r.json()['user']
                    print(f"   Usage: {user_info.get('usage_count', 0)}/{user_info.get('monthly_quota', 0)}")
                    print(f"   Last Login: {user_info.get('last_login', 'N/A')}")
                else:
                    print(f"   ❌ Error: {r.json()}")
            
            # Test 4: Password Reset Request
            print("\n4️⃣ Testing Password Reset Request...")
            r = requests.post(f"{BASE_URL}/api/v1/auth/request-password-reset", 
                            json={"email": register_data['email']})
            print(f"   Status: {r.status_code}")
            if r.status_code == 200:
                print("   ✅ Password reset request berhasil!")
                reset_data = r.json()
                reset_token = reset_data.get('reset_token')
                if reset_token:
                    print(f"   Reset Token: {reset_token[:20]}...")
                    
                    # Test 5: Reset Password
                    print("\n5️⃣ Testing Password Reset...")
                    r = requests.post(f"{BASE_URL}/api/v1/auth/reset-password", 
                                    json={
                                        "token": reset_token,
                                        "new_password": "NewPass123!"
                                    })
                    print(f"   Status: {r.status_code}")
                    if r.status_code == 200:
                        print("   ✅ Password reset berhasil!")
                    else:
                        print(f"   ❌ Error: {r.json()}")
            else:
                print(f"   ❌ Error: {r.json()}")
                
            # Test 6: Login dengan password baru
            print("\n6️⃣ Testing Login with New Password...")
            r = requests.post(f"{BASE_URL}/api/v1/auth/login", 
                            json={
                                "email": register_data['email'],
                                "password": "NewPass123!"
                            })
            print(f"   Status: {r.status_code}")
            if r.status_code == 200:
                print("   ✅ Login dengan password baru berhasil!")
                new_api_key = r.json()['data'].get('api_key')
                
                # Test 7: Regenerate API Key
                if new_api_key:
                    print("\n7️⃣ Testing Regenerate API Key...")
                    headers = {"X-API-KEY": new_api_key}
                    r = requests.post(f"{BASE_URL}/api/v1/auth/regenerate-api-key", 
                                    headers=headers)
                    print(f"   Status: {r.status_code}")
                    if r.status_code == 200:
                        print("   ✅ API Key regeneration berhasil!")
                        new_key = r.json().get('api_key')
                        print(f"   New API Key: {new_key[:20]}...")
                    else:
                        print(f"   ❌ Error: {r.json()}")
            else:
                print(f"   ❌ Error: {r.json()}")
                
        else:
            print(f"   ❌ Login gagal: {r.json()}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "="*60)
    print("✅ TESTING COMPLETED")
    print("="*60)
    print("\n📚 Baca AUTH_API_DOCS.md untuk dokumentasi lengkap")

if __name__ == "__main__":
    test_quick()
