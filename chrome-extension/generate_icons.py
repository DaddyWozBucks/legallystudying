#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size):
    # Create a new image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Create rounded rectangle background with gradient effect
    # Using a solid purple color that represents the gradient midpoint
    purple = (108, 99, 206)  # Mix of #667eea and #764ba2
    
    # Draw rounded rectangle
    radius = int(size * 0.15)
    draw.rounded_rectangle(
        [(0, 0), (size-1, size-1)],
        radius=radius,
        fill=purple
    )
    
    # Draw "LD" text
    text = "LD"
    # Try to use a bold font, fallback to default if not available
    try:
        # Attempt to calculate font size
        font_size = int(size * 0.35)
        # Use default font since we can't guarantee system fonts
        font = ImageFont.load_default()
        # For larger sizes, we'll just scale the drawing
    except:
        font = ImageFont.load_default()
    
    # Get text bounding box for centering
    # Using a simple approach for centering
    text_width = len(text) * (size // 4)
    text_height = size // 3
    text_x = (size - text_width) // 2
    text_y = (size - text_height) // 2
    
    # Draw the text in white
    draw.text((text_x, text_y), text, fill='white', font=font)
    
    return img

# Create icons directory if it doesn't exist
icons_dir = '/Users/woz/Documents/legal_dify/chrome-extension/icons'
os.makedirs(icons_dir, exist_ok=True)

# Generate all required icon sizes
sizes = [16, 32, 48, 128]
for size in sizes:
    icon = create_icon(size)
    icon.save(f'{icons_dir}/icon{size}.png')
    print(f'Created icon{size}.png')

print('All icons generated successfully!')