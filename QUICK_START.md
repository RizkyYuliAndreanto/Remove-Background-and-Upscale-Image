# 🚀 Quick Start Guide - Image Processing

Panduan cepat untuk testing dan menggunakan fitur background removal.

---

## 📋 Prerequisites

✅ Server sudah running  
✅ User sudah register & login  
✅ API key sudah didapat

---

## 🎯 Quick Test (3 Steps)

### Step 1: Create Test Image

```bash
python create_test_image.py
```

Output:

```
✅ Test image created: test_image.jpg
   Size: 800x600 pixels
   File size: ~45 KB
```

### Step 2: Run Test

```bash
python test_image_processing.py
```

Expected Output:

```
============================================================
🧪 IMAGE PROCESSING TEST
============================================================

1️⃣ Login to get API key...
✅ Login successful! API Key: abc123...

2️⃣ Checking current quota...
✅ Current quota: 0/10

3️⃣ Testing remove background endpoint (no file)...
Status: 400 ✅
Response: {'message': 'No image file provided', 'status': 'error'}

4️⃣ Testing with actual image: test_image.jpg
   File size: 45.23 KB
   Status: 200
   ✅ Success! Background removed
   Result URL: /api/v1/images/download/abc123_no_bg.png
   Quota used: 1/10

5️⃣ Checking quota after processing...
✅ Updated quota: 1/10
   Remaining: 9

============================================================
✅ TESTING COMPLETED
============================================================
```

### Step 3: View Results

Hasil file disimpan di folder `uploads/`:

```
uploads/
├── abc123_original.jpg      # Original file
└── abc123_no_bg.png        # Background removed
```

---

## 📝 Manual Test dengan cURL

### 1. Login & Get API Key

```bash
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"your@email.com","password":"yourpassword"}' \
  | jq -r '.data.api_key'
```

Save API key ke variable:

```bash
API_KEY="your-api-key-here"
```

### 2. Check Quota

```bash
curl -X GET http://localhost:5000/api/v1/auth/me \
  -H "X-API-KEY: $API_KEY" \
  | jq '.user | {usage_count, monthly_quota, quota_remaining}'
```

### 3. Remove Background

```bash
curl -X POST http://localhost:5000/api/v1/images/remove-bg \
  -H "X-API-KEY: $API_KEY" \
  -F "image=@test_image.jpg" \
  | jq '.'
```

### 4. Download Result

```bash
# Get filename from previous response
curl -O http://localhost:5000/api/v1/images/download/abc123_no_bg.png
```

---

## 🐍 Python Example

```python
import requests

# Configuration
BASE_URL = "http://localhost:5000/api/v1"
EMAIL = "your@email.com"
PASSWORD = "yourpassword"

# 1. Login
response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": EMAIL,
    "password": PASSWORD
})
api_key = response.json()['data']['api_key']

# 2. Check quota
headers = {"X-API-KEY": api_key}
response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
quota = response.json()['user']['quota_remaining']
print(f"Remaining quota: {quota}")

# 3. Remove background
if quota > 0:
    with open('test_image.jpg', 'rb') as f:
        files = {'image': f}
        response = requests.post(
            f"{BASE_URL}/images/remove-bg",
            headers=headers,
            files=files
        )

    if response.status_code == 200:
        result = response.json()['data']
        print(f"✅ Success!")
        print(f"Result: {result['result_url']}")
        print(f"Quota used: {result['quota_info']['used']}")
else:
    print("❌ No quota remaining")
```

---

## 🌐 JavaScript/Frontend Example

```javascript
// 1. Login
async function login(email, password) {
  const response = await fetch("http://localhost:5000/api/v1/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const data = await response.json();
  return data.data.api_key;
}

// 2. Remove background
async function removeBackground(apiKey, imageFile) {
  const formData = new FormData();
  formData.append("image", imageFile);

  const response = await fetch(
    "http://localhost:5000/api/v1/images/remove-bg",
    {
      method: "POST",
      headers: { "X-API-KEY": apiKey },
      body: formData,
    }
  );

  return await response.json();
}

// Usage
const apiKey = await login("user@example.com", "password");
const result = await removeBackground(apiKey, fileInput.files[0]);

if (result.status === "success") {
  console.log("Result URL:", result.data.result_url);
  console.log("Quota:", result.data.quota_info);
}
```

---

## 🎨 HTML Form Example

```html
<!DOCTYPE html>
<html>
  <head>
    <title>Background Remover</title>
  </head>
  <body>
    <h1>AI Background Remover</h1>

    <!-- Login Form -->
    <div id="loginForm">
      <h2>Login</h2>
      <input type="email" id="email" placeholder="Email" />
      <input type="password" id="password" placeholder="Password" />
      <button onclick="login()">Login</button>
    </div>

    <!-- Upload Form (hidden initially) -->
    <div id="uploadForm" style="display:none;">
      <h2>Upload Image</h2>
      <input type="file" id="imageFile" accept="image/jpeg,image/png" />
      <button onclick="processImage()">Remove Background</button>
      <div id="quota"></div>
      <div id="result"></div>
    </div>

    <script>
      let apiKey = null;

      async function login() {
        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;

        const response = await fetch(
          "http://localhost:5000/api/v1/auth/login",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password }),
          }
        );

        const data = await response.json();
        if (data.status === "success") {
          apiKey = data.data.api_key;
          document.getElementById("loginForm").style.display = "none";
          document.getElementById("uploadForm").style.display = "block";
          checkQuota();
        } else {
          alert("Login failed: " + data.message);
        }
      }

      async function checkQuota() {
        const response = await fetch("http://localhost:5000/api/v1/auth/me", {
          headers: { "X-API-KEY": apiKey },
        });
        const data = await response.json();
        document.getElementById(
          "quota"
        ).innerHTML = `Quota: ${data.user.usage_count}/${data.user.monthly_quota}`;
      }

      async function processImage() {
        const fileInput = document.getElementById("imageFile");
        const file = fileInput.files[0];

        if (!file) {
          alert("Please select an image");
          return;
        }

        const formData = new FormData();
        formData.append("image", file);

        const response = await fetch(
          "http://localhost:5000/api/v1/images/remove-bg",
          {
            method: "POST",
            headers: { "X-API-KEY": apiKey },
            body: formData,
          }
        );

        const data = await response.json();
        if (data.status === "success") {
          const resultUrl = "http://localhost:5000" + data.data.result_url;
          document.getElementById(
            "result"
          ).innerHTML = `<img src="${resultUrl}" style="max-width:500px"><br>
                     <a href="${resultUrl}" download>Download Result</a>`;
          checkQuota();
        } else {
          alert("Error: " + data.message);
        }
      }
    </script>
  </body>
</html>
```

Save as `test.html` dan buka di browser.

---

## 📊 Quota Management

### Check Remaining Quota

```bash
curl -X GET http://localhost:5000/api/v1/auth/me \
  -H "X-API-KEY: $API_KEY" \
  | jq '.user.quota_remaining'
```

### Quota by Role

- **Free (user):** 10 requests/month
- **Premium:** 1000 requests/month
- **Admin:** Unlimited

### Upgrade to Premium

Contact admin atau implement payment system.

---

## 🚨 Troubleshooting

### Error: "API Key Missing"

```bash
# Pastikan header X-API-KEY ada
curl -H "X-API-KEY: your-key" ...
```

### Error: "Quota exceeded"

```json
{
  "status": "error",
  "message": "Monthly quota exceeded. Please upgrade to premium.",
  "quota_info": {
    "used": 10,
    "limit": 10
  }
}
```

**Solution:** Wait for quota reset (30 days) or upgrade to premium

### Error: "File type not allowed"

Only JPG, JPEG, and PNG are supported.

### Error: "File too large"

Max file size: 16MB

### Server not responding

```bash
# Check if server is running
curl http://localhost:5000/health
```

---

## 📝 Tips

1. **Optimize images before upload**

   - Compress images
   - Resize to reasonable dimensions
   - Use PNG for better transparency

2. **Check quota before processing**

   - Always check remaining quota
   - Handle quota exceeded gracefully

3. **Store results**

   - Save result filename/URL
   - Download immediately if needed
   - Files may be cleaned up periodically

4. **Error handling**
   - Always check response status
   - Handle all error codes
   - Show user-friendly messages

---

## 🎯 Next Steps

1. ✅ Test basic functionality
2. ✅ Check quota management
3. ⏳ Build frontend interface
4. ⏳ Implement file cleanup
5. ⏳ Add batch processing
6. ⏳ Implement upscaling feature

---

**Ready to process images! 🎨**
