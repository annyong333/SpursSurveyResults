#!/usr/bin/env python3
"""
Script to download Tottenham Hotspur player pictures using Selenium
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
        
        filepath = os.path.join(folder, filename)
        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f"✓ Downloaded: {filename}")
        return True
    except Exception as e:
        print(f"✗ Error downloading {filename}: {e}")
        return False

def main():
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.chrome.options import Options
    except ImportError:
        print("Selenium not installed. Installing...")
        os.system("pip3 install selenium --quiet")
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.chrome.options import Options
    
    url = "https://www.tottenhamhotspur.com/teams/men/players/"
    folder_name = "tottenham 2025 squad"
    
    print("Setting up browser...")
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
    except Exception as e:
        print(f"Chrome driver error: {e}")
        print("\nTrying Firefox...")
        try:
            from selenium.webdriver.firefox.options import Options as FirefoxOptions
            firefox_options = FirefoxOptions()
            firefox_options.add_argument('--headless')
            driver = webdriver.Firefox(options=firefox_options)
        except Exception as e2:
            print(f"Firefox driver error: {e2}")
            print("\nPlease install Chrome/Firefox driver or use manual method.")
            return
    
    try:
        print(f"Loading page: {url}")
        driver.get(url)
        
        # Wait for page to load
        time.sleep(5)
        
        # Scroll to load lazy images
        print("Scrolling to load all images...")
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        
        # Create folder
        folder = create_folder(folder_name)
        
        # Find all images
        images = driver.find_elements(By.TAG_NAME, 'img')
        
        print(f"\nFound {len(images)} images on page")
        print("Filtering for player images...")
        
        player_images = []
        for img in images:
            src = img.get_attribute('src') or img.get_attribute('data-src')
            alt = img.get_attribute('alt') or ''
            
            if src and not src.startswith('data:'):
                # Look for player-related images
                if any(keyword in src.lower() for keyword in ['player', 'squad', 'headshot', 'portrait']) or \
                   any(keyword in alt.lower() for keyword in ['player', 'squad']) or \
                   '/media/' in src:
                    player_images.append({
                        'url': src,
                        'alt': alt
                    })
        
        print(f"Found {len(player_images)} potential player images")
        
        # Download images
        downloaded = 0
        for i, img_data in enumerate(player_images):
            img_url = img_data['url']
            alt_text = sanitize_filename(img_data['alt'])
            
            # Create filename
            if alt_text:
                filename = f"{alt_text}_{i+1}"
            else:
                filename = f"player_{i+1}"
            
            # Get file extension
            parsed = urlparse(img_url)
            path = parsed.path.split('?')[0]  # Remove query params
            ext = os.path.splitext(path)[1] or '.jpg'
            
            filename = f"{filename}{ext}"
            
            if download_image(img_url, folder, filename):
                downloaded += 1
            
            time.sleep(0.3)
        
        print(f"\n{'='*50}")
        print(f"Download complete!")
        print(f"Successfully downloaded {downloaded} images to '{folder_name}'")
        print(f"{'='*50}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
