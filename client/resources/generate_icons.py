#!/usr/bin/env python
"""Generate placeholder app icons for Minimalist.

Run this script to create minimal placeholder icons.
Replace with real icons before release.

Requirements: Pillow (pip install Pillow)

Output:
  - minimalist.png  (1024x1024, Linux/source)
  - minimalist.ico  (Windows, multi-size)
  - minimalist.icns (macOS, multi-size)
"""

import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Install Pillow first: pip install Pillow")
    sys.exit(1)


def create_icon(size=1024):
    """Create a simple M icon on dark background."""
    img = Image.new('RGBA', (size, size), (13, 13, 13, 255))
    draw = ImageDraw.Draw(img)

    # Draw "M" in accent purple
    font_size = int(size * 0.6)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except (OSError, IOError):
        font = ImageFont.load_default()

    text = "M"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - bbox[1]
    draw.text((x, y), text, fill=(124, 58, 237, 255), font=font)

    return img


def main():
    icon = create_icon(1024)

    # PNG (Linux/source)
    icon.save('minimalist.png')
    print("Created minimalist.png")

    # ICO (Windows) - multiple sizes
    icon.save(
        'minimalist.ico',
        format='ICO',
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )
    print("Created minimalist.ico")

    # ICNS (macOS) - save as PNG, use iconutil or img2icns to convert
    for size in [16, 32, 64, 128, 256, 512, 1024]:
        resized = icon.resize((size, size), Image.LANCZOS)
        resized.save(f'icon_{size}x{size}.png')
    print("Created icon_*x*.png files (use iconutil to create .icns)")


if __name__ == '__main__':
    main()
