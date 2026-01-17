"""
Create a simple test image for image processing tests
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_test_image(filename="test_image.jpg", size=(800, 600)):
    """Create a simple test image with colored background and text"""
    
    # Create image with gradient background
    img = Image.new('RGB', size, color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw gradient background
    for i in range(size[1]):
        color_value = int(255 * (i / size[1]))
        draw.rectangle([(0, i), (size[0], i+1)], fill=(100, color_value, 200))
    
    # Draw some shapes
    draw.ellipse([100, 100, 300, 300], fill='yellow', outline='orange', width=5)
    draw.rectangle([400, 200, 600, 400], fill='lightblue', outline='blue', width=5)
    draw.polygon([(650, 150), (700, 250), (600, 250)], fill='lightgreen', outline='green', width=5)
    
    # Add text
    try:
        # Try to use a font
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
    text = "Test Image for AI Background Removal"
    
    # Calculate text position (center)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    position = ((size[0] - text_width) // 2, size[1] - 100)
    
    # Draw text with shadow
    draw.text((position[0] + 2, position[1] + 2), text, font=font, fill='black')
    draw.text(position, text, font=font, fill='white')
    
    # Save image
    img.save(filename, 'JPEG', quality=95)
    print(f"✅ Test image created: {filename}")
    print(f"   Size: {size[0]}x{size[1]} pixels")
    print(f"   Format: JPEG")
    
    # Get file size
    file_size = os.path.getsize(filename)
    file_size_kb = file_size / 1024
    print(f"   File size: {file_size_kb:.2f} KB")
    
    return filename

if __name__ == "__main__":
    print("\n🎨 Creating test image...")
    print("="*50)
    
    # Create test image
    create_test_image()
    
    # Also create a smaller version for faster testing
    create_test_image("test_image_small.jpg", size=(400, 300))
    
    print("\n" + "="*50)
    print("✅ Test images created successfully!")
    print("\nYou can now run:")
    print("  python test_image_processing.py")
