#!/usr/bin/env python3
"""
Script to extract Tottenham statistics tables from FBRef and save to one Excel file
"""

import time
import pandas as pd
from bs4 import BeautifulSoup

def main():
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
    except ImportError:
        print("Installing selenium...")
        import os
        os.system("pip3 install selenium --quiet")
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
    
    try:
        import pandas as pd
    except ImportError:
        print("Installing pandas and openpyxl...")
        import os
        os.system("pip3 install pandas openpyxl --quiet")
        import pandas as pd
    
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
        
        # Scroll multiple times to load all content
        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
        
        # Get the page source
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Debug: Check if tables exist
        all_tables = soup.find_all('table')
        print(f"Found {len(all_tables)} total tables in page\n")
        
        # Table IDs we want (tables 1-12)
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
            print(f"[{i}/12] Extracting: {table_name}...")
            
            table = soup.find('table', {'id': table_id})
            
            if table:
                try:
                    # Convert table to pandas DataFrame
                    df = pd.read_html(str(table))[0]
                    
                    # Clean up sheet name (Excel has 31 char limit)
                    sheet_name = table_name[:31]
                    
                    # Write to Excel
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    
                    print(f"    ✓ {len(df)} rows extracted")
                    tables_extracted += 1
                except Exception as e:
                    print(f"    ✗ Error parsing table: {e}")
            else:
                print(f"    ✗ Table with ID '{table_id}' not found")
                # Try to find it by index
                if i <= len(all_tables):
                    try:
                        df = pd.read_html(str(all_tables[i-1]))[0]
                        sheet_name = table_name[:31]
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                        print(f"    ✓ Found by index: {len(df)} rows extracted")
                        tables_extracted += 1
                    except:
                        pass
        
        # Save the Excel file only if we have data
        if tables_extracted > 0:
            writer.close()
        else:
            writer.close()
            import os
            os.remove(output_file)
        
        print(f"\n{'='*60}")
        print(f"Success! All tables saved to: {output_file}")
        print(f"{'='*60}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
