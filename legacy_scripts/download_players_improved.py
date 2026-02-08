#!/usr/bin/env python3
"""
Improved script to download actual Tottenham player profile photos
"""

import requests
import os
import re
import time
from urllib.parse import urljoin, urlparse

def create_folder(folder_name):
    """Create folder if it doesn't exist"""
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"Created folder: {folder_name}")
    return folder_name

def sanitize_filename(filename):
    """Remove invalid characters from filename"""
    return re.sub(r'[<>:"/\\|?*]', '', filename).strip()

def download_image(url, folder, filename):
    """Download an image from URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Check if it's actually an image and has content
        if len(response.content) < 1000:  # Skip tiny images (likely icons)
            return False
            
        filepath = os.path.join(folder, filename)
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        # Get file size
        size_kb = len(response.content) / 1024
        print(f"✓ Downloaded: {filename} ({size_kb:.1f} KB)")
        return True
    except Exception as e:
        print(f"✗ Error downloading {filename}: {e}")
        return False

def main():
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
    except ImportError:
        print("Selenium not installed. Installing...")
        os.system("pip3 install selenium --quiet")
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
    
    url = "https://www.tottenhamhotspur.com/teams/men/players/"
    folder_name = "tottenham 2025 squad"
    
    print("Setting up browser...")
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print(f"Loading page: {url}")
        driver.get(url)
        
        # Wait for content to load
        print("Waiting for player cards to load...")
        time.sleep(5)
        
        # Scroll to load all content
        print("Scrolling to load all players...")
        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
        
        # Create folder
        folder = create_folder(folder_name)
        
        # Look for player card elements - try different selectors
        print("\nSearching for player images...")
        
        player_images = []
        
        # Method 1: Look for player card containers
        player_cards = driver.find_elements(By.CSS_SELECTOR, '[class*="player"], [class*="Player"], [class*="squad"], [class*="Squad"]')
        print(f"Found {len(player_cards)} potential player card elements")
        
        for card in player_cards:
            try:
                # Look for images within player cards
                imgs = card.find_elements(By.TAG_NAME, 'img')
                for img in imgs:
                    src = img.get_attribute('src') or img.get_attribute('data-src')
                    alt = img.get_attribute('alt') or ''
                    
                    if src and not src.startswith('data:'):
                        # Filter out small icons and logos
                        if 'logo' not in src.lower() and 'icon' not in src.lower():
                            player_images.append({
                                'url': src,
                                'alt': alt,
                                'src': src
                            })
            except:
                pass
        
        # Method 2: Look for all images with player-related URLs
        all_images = driver.find_elements(By.TAG_NAME, 'img')
        for img in all_images:
            src = img.get_attribute('src') or img.get_attribute('data-src')
            alt = img.get_attribute('alt') or ''
            
            if src and not src.startswith('data:'):
                # Look for images in /media/ path (Tottenham's media folder)
                if '/media/' in src and 'logo' not in src.lower() and 'icon' not in src.lower():
                    # Check if it's a reasonable size (player photos are usually larger)
                    width = img.get_attribute('width')
                    height = img.get_attribute('height')
                    
                    player_images.append({
                        'url': src,
                        'alt': alt,
                        'src': src
                    })
        
        # Remove duplicates
        seen_urls = set()
        unique_images = []
        for img in player_images:
            # Get base URL without query params for deduplication
            base_url = img['url'].split('?')[0]
            if base_url not in seen_urls:
                seen_urls.add(base_url)
                unique_images.append(img)
        
        print(f"\nFound {len(unique_images)} unique images to download")
        
        # Download images
        downloaded = 0
        for i, img_data in enumerate(unique_images):
            img_url = img_data['url']
            
            # Try to get player name from alt text
            alt_text = sanitize_filename(img_data['alt'])
            if alt_text and len(alt_text) > 3:
                filename = f"{alt_text}"
            else:
                filename = f"player_{i+1}"
            
            # Get file extension
            parsed = urlparse(img_url)
            path = parsed.path.split('?')[0]
            ext = os.path.splitext(path)[1] or '.jpg'
            
            filename = f"{filename}{ext}"
            
            if download_image(img_url, folder, filename):
                downloaded += 1
            
            time.sleep(0.3)
        
        print(f"\n{'='*60}")
        print(f"Download complete!")
        print(f"Successfully downloaded {downloaded} images to '{folder_name}'")
        print(f"{'='*60}")
        
        if downloaded == 0:
            print("\nNo images were downloaded. Let me show you what's on the page...")
            print("\nPage source snippet:")
            print(driver.page_source[:2000])
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
