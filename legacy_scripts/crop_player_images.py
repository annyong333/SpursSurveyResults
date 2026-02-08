#!/usr/bin/env python3
"""
Script to crop the bottom half of player images
"""

import os
from PIL import Image

def crop_bottom_half(input_path, output_path):
    """Crop out the bottom half of an image"""
    try:
        # Open the image
        img = Image.open(input_path)
        width, height = img.size
        
        # Calculate crop box (keep top half)
        # (left, top, right, bottom)
        crop_box = (0, 0, width, height // 2)
        
        # Crop the image
        cropped_img = img.crop(crop_box)
        
        # Save the cropped image
        cropped_img.save(output_path)
        
        print(f"✓ Cropped: {os.path.basename(input_path)} ({width}x{height} → {width}x{height//2})")
        return True
    except Exception as e:
        print(f"✗ Error cropping {os.path.basename(input_path)}: {e}")
        return False

def main():
    # Install Pillow if needed
    try:
        from PIL import Image
    except ImportError:
        print("Installing Pillow...")
        os.system("pip3 install Pillow --quiet")
        from PIL import Image
    
    source_folder = "tottenham 2025 squad"
    output_folder = os.path.join(source_folder, "cropped images")
    
    # Create output folder
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created folder: {output_folder}\n")
    
    # Get all image files
    image_files = [f for f in os.listdir(source_folder) 
                   if f.lower().endswith(('.png', '.jpg', '.jpeg')) 
                   and os.path.isfile(os.path.join(source_folder, f))]
    
    print(f"Found {len(image_files)} images to crop\n")
    
    # Process each image
    cropped_count = 0
    for image_file in sorted(image_files):
        input_path = os.path.join(source_folder, image_file)
        output_path = os.path.join(output_folder, image_file)
        
        if crop_bottom_half(input_path, output_path):
            cropped_count += 1
    
    print(f"\n{'='*60}")
    print(f"Successfully cropped {cropped_count} images")
    print(f"Cropped images saved to: {output_folder}")
    print(f"Original images remain in: {source_folder}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
