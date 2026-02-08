#!/usr/bin/env python3
"""
Script to download Tottenham Hotspur player pictures from their official website
"""

import requests
from bs4 import BeautifulSoup
import os
import re
from urllib.parse import urljoin, urlparse
import time

def create_folder(folder_name):
    """Create folder if it doesn't exist"""
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"Created folder: {folder_name}")
    return folder_name

def sanitize_filename(filename):
    """Remove invalid characters from filename"""
    return re.sub(r'[<>:"/\\|?*]', '', filename)

def download_image(url, folder, filename):
    """Download an image from URL"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        filepath = os.path.join(folder, filename)
        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: {filename}")
        return True
    except Exception as e:
        print(f"Error downloading {filename}: {e}")
        return False

def main():
    url = "https://www.tottenhamhotspur.com/teams/men/players/"
    folder_name = "tottenham 2025 squad"
    
    print("Fetching player page...")
    
    try:
        # Fetch the page
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Create folder
        folder = create_folder(folder_name)
        
        # Find player images - looking for common patterns
        images = []
        
        # Look for player cards/images
        for img in soup.find_all('img'):
            src = img.get('src', '') or img.get('data-src', '')
            alt = img.get('alt', '')
            
            # Filter for player images
            if src and ('player' in src.lower() or 'squad' in src.lower() or 
                       'headshot' in src.lower() or 'portrait' in src.lower()):
                images.append({
                    'url': urljoin(url, src),
                    'alt': alt
                })
        
        # Also check for background images in style attributes
        for elem in soup.find_all(style=re.compile(r'background-image')):
            style = elem.get('style', '')
            urls = re.findall(r'url\(["\']?([^"\']+)["\']?\)', style)
            for img_url in urls:
                if 'player' in img_url.lower() or 'squad' in img_url.lower():
                    images.append({
                        'url': urljoin(url, img_url),
                        'alt': 'player'
                    })
        
        if not images:
            print("No player images found. The page might use JavaScript to load content.")
            print("Trying alternative approach...")
            
            # Look for any images in the page
            all_images = soup.find_all('img')
            print(f"Found {len(all_images)} total images on the page")
            
            # Save first few images as examples
            for i, img in enumerate(all_images[:10]):
                src = img.get('src', '') or img.get('data-src', '')
                if src:
                    print(f"Sample image {i+1}: {src[:100]}...")
        
        # Download images
        downloaded = 0
        for i, img_data in enumerate(images):
            img_url = img_data['url']
            alt_text = sanitize_filename(img_data['alt']) or f"player_{i+1}"
            
            # Get file extension
            parsed = urlparse(img_url)
            ext = os.path.splitext(parsed.path)[1] or '.jpg'
            
            filename = f"{alt_text}_{i+1}{ext}"
            
            if download_image(img_url, folder, filename):
                downloaded += 1
            
            time.sleep(0.5)  # Be polite to the server
        
        print(f"\nDownload complete! {downloaded} images saved to '{folder_name}'")
        
        if downloaded == 0:
            print("\nNote: This page appears to load content dynamically with JavaScript.")
            print("You may need to use a browser automation tool like Selenium to access the images.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
