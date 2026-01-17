"""
Test script untuk image processing endpoint
"""
import requests
import os
import sys

BASE_URL = "http://127.0.0.1:5000/api/v1"

def create_test_image_if_missing():
    """Create test image if not exists"""
    if not os.path.exists("test_image.jpg") and not os.path.exists("test_image_small.jpg"):
        print("\n⚠️  No test image found. Creating one...")
        try:
            from create_test_image import create_test_image
            create_test_image("test_image.jpg", size=(800, 600))
            print("✅ Test image created!")
            return True
        except ImportError:
            print("❌ Could not create test image automatically.")
            print("   Run: python create_test_image.py")
            return False
    return True

def test_remove_background():
    """Test remove background endpoint"""
    print("\n" + "="*60)
    print("🧪 IMAGE PROCESSING TEST")
    print("="*60)
    
    # 1. Login dulu untuk mendapatkan API key
    print("\n1️⃣ Login to get API key...")
    login_response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "quicktest@example.com",
        "password": "NewPass123!"
    })
    
    if login_response.status_code != 200:
        print("❌ Login failed. Please register first or check credentials.")
        return
    
    api_key = login_response.json()['data']['api_key']
    print(f"✅ Login successful! API Key: {api_key[:20]}...")
    
    # 2. Check current quota
    print("\n2️⃣ Checking current quota...")
    headers = {"X-API-KEY": api_key}
    me_response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    
    if me_response.status_code == 200:
        user_data = me_response.json()['user']
        print(f"✅ Current quota: {user_data['usage_count']}/{user_data['monthly_quota']}")
    
    # 3. Test remove background (without actual image)
    print("\n3️⃣ Testing remove background endpoint (no file)...")
    response = requests.post(
        f"{BASE_URL}/images/remove-bg",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # 4. Test with image file (if exists)
    test_images = ["test_image_small.jpg", "test_image.jpg"]
    test_image_path = None
    
    for img_path in test_images:
        if os.path.exists(img_path):
            test_image_path = img_path
            break
    
    if test_image_path:
        print(f"\n4️⃣ Testing with actual image: {test_image_path}")
        
        # Get file size
        file_size = os.path.getsize(test_image_path) / 1024
        print(f"   File size: {file_size:.2f} KB")
        
        with open(test_image_path, 'rb') as img_file:
            files = {'image': img_file}
            response = requests.post(
                f"{BASE_URL}/images/remove-bg",
                headers=headers,
                files=files
            )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success! Background removed")
            print(f"   Result URL: {data['data']['result_url']}")
            print(f"   Quota used: {data['data']['quota_info']['used']}/{data['data']['quota_info']['limit']}")
        else:
            print(f"   ❌ Error: {response.json()}")
    else:
        print(f"\n4️⃣ No test image found")
        print("   Creating test image...")
        if create_test_image_if_missing():
            print("   ✅ Test image created! Run test again to process it.")
        else:
            print("   ⚠️  Run: python create_test_image.py")
    
    # 5. Check quota after processing
    print("\n5️⃣ Checking quota after processing...")
    me_response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    
    if me_response.status_code == 200:
        user_data = me_response.json()['user']
        print(f"✅ Updated quota: {user_data['usage_count']}/{user_data['monthly_quota']}")
        print(f"   Remaining: {user_data['quota_remaining']}")
    
    print("\n" + "="*60)
    print("✅ TESTING COMPLETED")
    print("="*60)

if __name__ == "__main__":
    try:
        test_remove_background()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to server.")
        print("Make sure Flask server is running on http://127.0.0.1:5000")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
