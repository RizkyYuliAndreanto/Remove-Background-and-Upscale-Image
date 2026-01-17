# 🖼️ Image Processing API Documentation

API untuk remove background dari gambar menggunakan AI (rembg + U2-Net).

---

## 📍 Endpoints

### Base URL

```
http://localhost:5000/api/v1/images
```

---

## 1. Remove Background

Remove background dari gambar menggunakan AI.

**Endpoint:** `POST /remove-bg`

**Authentication:** API Key required

**Headers:**

```
X-API-KEY: your-api-key-here
Content-Type: multipart/form-data
```

**Request Body (multipart/form-data):**

```
image: <file> (jpg, jpeg, png)
```

**Success Response (200):**

```json
{
  "status": "success",
  "message": "Background removed successfully",
  "data": {
    "result_url": "/api/v1/images/download/abc123_no_bg.png",
    "original_file": "abc123_original.jpg",
    "quota_info": {
      "used": 6,
      "remaining": 4,
      "limit": 10
    }
  }
}
```

**Error Responses:**

| Code | Error                  | Description                 |
| ---- | ---------------------- | --------------------------- |
| 400  | No image file provided | File 'image' not in request |
| 400  | No selected file       | Filename is empty           |
| 400  | File type not allowed  | Only jpg, jpeg, png allowed |
| 401  | API Key Missing        | No X-API-KEY header         |
| 401  | Invalid API Key        | API key not found           |
| 403  | Account Banned         | User account is banned      |
| 429  | Monthly quota exceeded | User reached quota limit    |
| 500  | Internal server error  | Processing failed           |

**Quota Exceeded Response (429):**

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

**Example - cURL:**

```bash
curl -X POST http://localhost:5000/api/v1/images/remove-bg \
  -H "X-API-KEY: your-api-key-here" \
  -F "image=@/path/to/image.jpg"
```

**Example - Python:**

```python
import requests

url = "http://localhost:5000/api/v1/images/remove-bg"
headers = {"X-API-KEY": "your-api-key-here"}
files = {'image': open('image.jpg', 'rb')}

response = requests.post(url, headers=headers, files=files)
print(response.json())
```

**Example - JavaScript:**

```javascript
const formData = new FormData();
formData.append("image", fileInput.files[0]);

fetch("http://localhost:5000/api/v1/images/remove-bg", {
  method: "POST",
  headers: {
    "X-API-KEY": "your-api-key-here",
  },
  body: formData,
})
  .then((response) => response.json())
  .then((data) => console.log(data));
```

---

## 2. Download File

Download hasil pemrosesan gambar.

**Endpoint:** `GET /download/<filename>`

**Authentication:** None (Public access)

**Path Parameters:**

- `filename` - Nama file hasil processing

**Success Response:**

- Returns image file as attachment

**Error Response (404):**

```json
{
  "status": "error",
  "message": "File not found"
}
```

**Example:**

```bash
curl -O http://localhost:5000/api/v1/images/download/abc123_no_bg.png
```

---

## 📊 Quota System

### Quota per Role

| Role        | Monthly Quota | Reset Period |
| ----------- | ------------- | ------------ |
| user (free) | 10 requests   | 30 days      |
| premium     | 1000 requests | 30 days      |
| admin       | Unlimited     | -            |

### Quota Tracking

- Setiap successful image processing mengurangi quota
- Quota di-reset otomatis setiap 30 hari
- Check quota via `/api/v1/auth/me` endpoint

### Quota Info Response

```json
{
  "quota_info": {
    "used": 5, // Sudah digunakan
    "remaining": 5, // Sisa quota
    "limit": 10 // Total quota
  }
}
```

---

## 🎯 File Requirements

### Supported Formats

- ✅ JPG / JPEG
- ✅ PNG

### File Size Limit

- **Maximum:** 16 MB

### Recommended Specifications

- **Resolution:** Max 4000x4000 pixels
- **Format:** PNG untuk hasil terbaik
- **Size:** Semakin kecil, semakin cepat

---

## 🔄 Processing Flow

```
1. User uploads image
   ↓
2. Validate file type & size
   ↓
3. Check user quota
   ↓
4. Save original image
   ↓
5. Process with AI (rembg)
   ↓
6. Save result image
   ↓
7. Increment usage count
   ↓
8. Return result URL
```

---

## 🛡️ Security

### Rate Limiting

- Quota-based limiting (per user)
- Free users: 10/month
- Premium: 1000/month

### File Validation

- ✅ Extension check (whitelist)
- ✅ File size limit (16MB)
- ✅ Secure filename generation (UUID)

### Storage

- Unique filename per upload (UUID)
- Original + processed versions stored
- Files stored in `uploads/` folder

---

## 🚨 Error Handling

### Common Errors

**1. Quota Exceeded**

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

**Solution:** Wait for quota reset or upgrade to premium

**2. Invalid File Type**

```json
{
  "status": "error",
  "message": "File type not allowed. Allowed: jpg, jpeg, png"
}
```

**Solution:** Convert image to supported format

**3. File Too Large**

```json
{
  "status": "error",
  "message": "File size exceeds limit (16MB)"
}
```

**Solution:** Compress or resize image

**4. Processing Failed**

```json
{
  "status": "error",
  "message": "Error processing image: [error details]"
}
```

**Solution:** Check image format, try different image

---

## 📝 Best Practices

### For API Consumers

1. **Always check quota first**

   ```python
   response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
   quota = response.json()['user']['quota_remaining']
   if quota > 0:
       # Process image
   ```

2. **Handle quota exceeded gracefully**

   ```python
   if response.status_code == 429:
       print("Quota exceeded. Upgrade or wait for reset.")
   ```

3. **Validate files client-side**

   - Check file type before upload
   - Check file size before upload
   - Show preview to user

4. **Error handling**

   ```python
   try:
       response = requests.post(url, headers=headers, files=files)
       if response.status_code == 200:
           # Success
       elif response.status_code == 429:
           # Quota exceeded
       else:
           # Other error
   except Exception as e:
       # Network error
   ```

5. **Store API key securely**
   - Never commit to version control
   - Use environment variables
   - Rotate keys regularly

---

## 🧪 Testing

### Test Script

```bash
python test_image_processing.py
```

### Manual Testing with cURL

```bash
# 1. Login to get API key
API_KEY=$(curl -s -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}' \
  | jq -r '.data.api_key')

# 2. Check quota
curl -X GET http://localhost:5000/api/v1/auth/me \
  -H "X-API-KEY: $API_KEY"

# 3. Remove background
curl -X POST http://localhost:5000/api/v1/images/remove-bg \
  -H "X-API-KEY: $API_KEY" \
  -F "image=@test_image.jpg"

# 4. Download result
curl -O http://localhost:5000/api/v1/images/download/result_filename.png
```

---

## 📈 Performance

### Processing Time

- Small images (< 500KB): ~1-2 seconds
- Medium images (500KB - 2MB): ~2-5 seconds
- Large images (2MB - 16MB): ~5-15 seconds

### Optimization Tips

1. Resize images before upload
2. Use appropriate format (PNG for transparency)
3. Compress images without quality loss
4. Use batch processing for multiple images (coming soon)

---

## 🔮 Future Features

- [ ] Batch processing (multiple images)
- [ ] Image upscaling
- [ ] Custom background color/image
- [ ] Edge refinement options
- [ ] Async processing (webhook callback)
- [ ] Cloud storage integration (S3, Azure Blob)
- [ ] Image optimization
- [ ] Format conversion

---

## 📞 Support

- **Documentation:** [Full Docs](../docs/README.md)
- **Issues:** Create issue on GitHub
- **Email:** support@example.com

---

## 📚 Related Documentation

- [Authentication API](../docs/auth/API.md)
- [Developer Guide](../docs/auth/DEVELOPER_GUIDE.md)
- [Security Features](../docs/auth/SECURITY.md)

---

**Happy Processing! 🎨**
