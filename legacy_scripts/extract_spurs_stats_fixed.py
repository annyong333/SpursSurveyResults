#!/usr/bin/env python3
"""
Script to extract Tottenham statistics tables from FBRef (handles commented tables)
"""

import time
import pandas as pd
import re
from bs4 import BeautifulSoup, Comment

def main():
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
    except ImportError:
        import os
        os.system("pip3 install selenium --quiet")
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
    
    url = "https://fbref.com/en/squads/361ca564/2024-2025/Tottenham-Hotspur-Stats"
    
    print("Loading Tottenham 2024-2025 stats from FBRef...\n")
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get(url)
        time.sleep(8)
        
        # Scroll to load all content
        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
        
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # FBRef hides tables in HTML comments to prevent scraping
        # We need to extract them from comments
        print("Extracting tables from HTML comments...\n")
        
        # Find all comments
        comments = soup.find_all(string=lambda text: isinstance(text, Comment))
        
        # Parse tables from comments
        all_tables = []
        for comment in comments:
            comment_soup = BeautifulSoup(comment, 'html.parser')
            tables = comment_soup.find_all('table')
            all_tables.extend(tables)
        
        # Also get visible tables
        visible_tables = soup.find_all('table')
        all_tables.extend(visible_tables)
        
        print(f"Found {len(all_tables)} total tables\n")
        
        # Table IDs we want
        table_ids = [
            'stats_standard_9',
            'matchlogs_for',
            'stats_keeper_9',
            'stats_keeper_adv_9',
            'stats_shooting_9',
            'stats_passing_9',
            'stats_passing_types_9',
            'stats_gca_9',
            'stats_defense_9',
            'stats_possession_9',
            'stats_playing_time_9',
            'stats_misc_9'
        ]
        
        table_names = [
            'Standard Stats',
            'Scores & Fixtures',
            'Goalkeeping',
            'Advanced Goalkeeping',
            'Shooting',
            'Passing',
            'Pass Types',
            'Goal and Shot Creation',
            'Defensive Actions',
            'Possession',
            'Playing Time',
            'Miscellaneous Stats'
        ]
        
        # Create Excel writer
        output_file = 'Tottenham_2024-2025_Stats.xlsx'
        writer = pd.ExcelWriter(output_file, engine='openpyxl')
        
        print("Extracting tables...\n")
        
        tables_extracted = 0
        
        for i, (table_id, table_name) in enumerate(zip(table_ids, table_names), 1):
            print(f"[{i}/12] {table_name}...", end=' ')
            
            # Find table by ID
            table = None
            for t in all_tables:
                if t.get('id') == table_id:
                    table = t
                    break
            
            if table:
                try:
                    # Convert table to pandas DataFrame
                    df = pd.read_html(str(table))[0]
                    
                    # Clean up sheet name (Excel has 31 char limit)
                    sheet_name = table_name[:31]
                    
                    # Write to Excel
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    
                    print(f"✓ {len(df)} rows")
                    tables_extracted += 1
                except Exception as e:
                    print(f"✗ Error: {e}")
            else:
                print(f"✗ Not found")
        
        # Save the Excel file
        if tables_extracted > 0:
            writer.close()
            print(f"\n{'='*60}")
            print(f"Success! {tables_extracted}/12 tables saved to:")
            print(f"{output_file}")
            print(f"{'='*60}")
        else:
            writer.close()
            import os
            os.remove(output_file)
            print("\nNo tables were extracted.")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
