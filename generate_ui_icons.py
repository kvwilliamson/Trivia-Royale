#!/usr/bin/env python3
"""
Generate UI Icons for Trivia Royale
Creates checkmark and X icons using PIL
"""

from PIL import Image, ImageDraw
import os

# Create output directory
os.makedirs("assets/images/ui", exist_ok=True)

def create_checkmark(size=128):
    """Create a green checkmark icon"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw checkmark
    width = max(size // 10, 8)
    
    # Calculate checkmark points
    points = [
        (size * 0.2, size * 0.5),
        (size * 0.4, size * 0.7),
        (size * 0.8, size * 0.3)
    ]
    
    # Draw the checkmark as thick lines
    draw.line([points[0], points[1]], fill=(0, 200, 0, 255), width=width)
    draw.line([points[1], points[2]], fill=(0, 200, 0, 255), width=width)
    
    img.save("assets/images/ui/checkmark.png")
    print("✓ Created: assets/images/ui/checkmark.png")

def create_x_mark(size=128):
    """Create a red X icon"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw X
    width = max(size // 10, 8)
    margin = size * 0.2
    
    # Draw the X as two diagonal lines
    draw.line([( margin, margin), (size-margin, size-margin)], fill=(255, 0, 0, 255), width=width)
    draw.line([(size-margin, margin), (margin, size-margin)], fill=(255, 0, 0, 255), width=width)
    
    img.save("assets/images/ui/x_mark.png")
    print("✓ Created: assets/images/ui/x_mark.png")

if __name__ == "__main__":
    print("🎨 Generating UI icons for Trivia Royale...\n")
    
    try:
        create_checkmark(128)
        create_x_mark(128)
        
        print("\n✅ All UI icons generated successfully!")
        print(f"📁 Saved to: assets/images/ui/")
        
    except Exception as e:
        print(f"\n❌ Error generating icons: {e}")
