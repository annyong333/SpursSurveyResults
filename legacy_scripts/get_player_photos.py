#!/usr/bin/env python3
"""
Script to get actual player profile photos from Tottenham website
"""

import requests
import os
import re
import time
from urllib.parse import urljoin

def create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    return folder_name

def download_image(url, folder, filename):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        filepath = os.path.join(folder, filename)
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        size_kb = len(response.content) / 1024
        print(f"✓ {filename} ({size_kb:.1f} KB)")
        return True
    except Exception as e:
        print(f"✗ {filename}: {e}")
        return False

def main():
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.options import Options
    except ImportError:
        os.system("pip3 install selenium --quiet")
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.options import Options
    
    url = "https://www.tottenhamhotspur.com/teams/men/players/"
    folder_name = "tottenham 2025 squad"
    
    print("Loading Tottenham squad page...\n")
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get(url)
        time.sleep(5)
        
        # Scroll to load all players
        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
        
        folder = create_folder(folder_name)
        
        # Get all links that might lead to player profiles
        print("Finding player profile links...")
        player_links = []
        
        # Look for links in the players section
        links = driver.find_elements(By.TAG_NAME, 'a')
        for link in links:
            href = link.get_attribute('href')
            if href and '/players/' in href and href != url:
                player_links.append(href)
        
        # Remove duplicates
        player_links = list(set(player_links))
        print(f"Found {len(player_links)} player profile pages\n")
        
        if len(player_links) == 0:
            print("No player links found. Trying to get images directly from main page...")
            
            # Try to find large images (player photos are typically larger)
            all_imgs = driver.find_elements(By.TAG_NAME, 'img')
            large_images = []
            
            for img in all_imgs:
                src = img.get_attribute('src') or img.get_attribute('data-src')
                if not src or src.startswith('data:'):
                    continue
                
                # Check image dimensions
                try:
                    width = int(img.get_attribute('naturalWidth') or 0)
                    height = int(img.get_attribute('naturalHeight') or 0)
                    
                    # Player photos are usually at least 200x200
                    if width >= 200 and height >= 200:
                        alt = img.get_attribute('alt') or ''
                        if 'logo' not in alt.lower() and 'logo' not in src.lower():
                            large_images.append({'url': src, 'alt': alt})
                except:
                    pass
            
            print(f"Found {len(large_images)} large images")
            
            downloaded = 0
            for i, img in enumerate(large_images[:30]):  # Limit to 30
                filename = f"player_{i+1}.jpg"
                if download_image(img['url'], folder, filename):
                    downloaded += 1
                time.sleep(0.3)
            
            print(f"\nDownloaded {downloaded} images to '{folder_name}'")
        else:
            # Visit each player page and get their photo
            downloaded = 0
            for i, player_url in enumerate(player_links[:30], 1):  # Limit to first 30 players
                try:
                    print(f"[{i}/{min(len(player_links), 30)}] Visiting {player_url.split('/')[-2]}...")
                    driver.get(player_url)
                    time.sleep(2)
                    
                    # Look for the main player image
                    imgs = driver.find_elements(By.TAG_NAME, 'img')
                    for img in imgs:
                        src = img.get_attribute('src') or img.get_attribute('data-src')
                        alt = img.get_attribute('alt') or ''
                        
                        if src and not src.startswith('data:'):
                            # Look for large images that might be the player photo
                            if '/media/' in src and 'logo' not in src.lower():
                                player_name = player_url.split('/')[-2].replace('-', '_')
                                ext = '.jpg' if '.jpg' in src else '.png'
                                filename = f"{player_name}{ext}"
                                
                                if download_image(src, folder, filename):
                                    downloaded += 1
                                    break
                    
                    time.sleep(1)
                except Exception as e:
                    print(f"Error processing {player_url}: {e}")
            
            print(f"\n{'='*60}")
            print(f"Downloaded {downloaded} player photos to '{folder_name}'")
            print(f"{'='*60}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
