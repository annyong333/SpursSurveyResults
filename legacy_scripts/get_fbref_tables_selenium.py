#!/usr/bin/env python3
"""
Script to identify all tables on the FBRef Tottenham stats page using Selenium
"""

import time
from bs4 import BeautifulSoup

def main():
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
    except ImportError:
        print("Selenium not installed. Installing...")
        import os
        os.system("pip3 install selenium --quiet")
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
    
    url = "https://fbref.com/en/squads/361ca564/2024-2025/Tottenham-Hotspur-Stats"
    
    print("Loading Tottenham stats page from FBRef...\n")
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get(url)
        time.sleep(5)  # Wait for page to load
        
        # Scroll to load any lazy-loaded content
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        # Get page source and parse with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Find all tables
        tables = soup.find_all('table')
        
        print(f"Found {len(tables)} tables on the page\n")
        print("="*80)
        
        table_info = []
        
        for i, table in enumerate(tables, 1):
            # Get table ID
            table_id = table.get('id', 'No ID')
            
            # Try to find table caption/title
            caption = table.find('caption')
            if caption:
                title = caption.get_text(strip=True)
            else:
                # Try to find a heading before the table
                title = "No title found"
                # Look for h2 with data-label attribute
                parent = table.find_parent('div')
                if parent:
                    heading = parent.find_previous(['h2', 'h3', 'h4'])
                    if heading:
                        title = heading.get_text(strip=True)
            
            # Get number of rows and columns
            rows = table.find_all('tr')
            num_rows = len(rows)
            num_cols = 0
            if rows:
                # Count columns from header row
                header_row = rows[0] if rows else None
                if header_row:
                    num_cols = len(header_row.find_all(['th', 'td']))
            
            # Get first few column headers
            headers = []
            if rows:
                header_cells = rows[0].find_all(['th', 'td'])
                headers = [cell.get_text(strip=True) for cell in header_cells[:5]]
            
            table_info.append({
                'number': i,
                'id': table_id,
                'title': title,
                'rows': num_rows,
                'cols': num_cols,
                'headers': headers
            })
            
            print(f"Table {i}:")
            print(f"  ID: {table_id}")
            print(f"  Title: {title}")
            print(f"  Size: {num_rows} rows × {num_cols} columns")
            if headers:
                print(f"  First columns: {', '.join(headers[:5])}")
            print("-"*80)
        
        print("\n" + "="*80)
        print("SUMMARY - ALL TABLES:")
        print("="*80)
        
        for info in table_info:
            print(f"\n{info['number']:2d}. {info['title']}")
            print(f"    ID: {info['id']}")
            print(f"    Size: {info['rows']} rows × {info['cols']} columns")
        
        print("\n" + "="*80)
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
