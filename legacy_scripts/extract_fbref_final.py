#!/usr/bin/env python3
"""
Extract Tottenham stats from FBRef using requests with proper handling
"""

import requests
import pandas as pd
import re
from bs4 import BeautifulSoup, Comment
import time

def main():
    url = "https://fbref.com/en/squads/361ca564/2024-2025/Tottenham-Hotspur-Stats"
    
    print("Fetching Tottenham 2024-2025 stats from FBRef...\n")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    session = requests.Session()
    
    try:
        # First request to get cookies
        response = session.get(url, headers=headers, timeout=30)
        time.sleep(2)
        
        # Second request with cookies
        response = session.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract tables from HTML comments
        print("Parsing HTML and extracting tables...\n")
        
        comments = soup.find_all(string=lambda text: isinstance(text, Comment))
        
        all_tables = []
        for comment in comments:
            if '<table' in comment:
                comment_soup = BeautifulSoup(comment, 'html.parser')
                tables = comment_soup.find_all('table')
                all_tables.extend(tables)
        
        # Also get visible tables
        visible_tables = soup.find_all('table')
        all_tables.extend(visible_tables)
        
        print(f"Found {len(all_tables)} total tables\n")
        
        # Table IDs we want
        table_mapping = {
            'stats_standard_9': 'Standard Stats',
            'matchlogs_for': 'Scores & Fixtures',
            'stats_keeper_9': 'Goalkeeping',
            'stats_keeper_adv_9': 'Advanced Goalkeeping',
            'stats_shooting_9': 'Shooting',
            'stats_passing_9': 'Passing',
            'stats_passing_types_9': 'Pass Types',
            'stats_gca_9': 'Goal and Shot Creation',
            'stats_defense_9': 'Defensive Actions',
            'stats_possession_9': 'Possession',
            'stats_playing_time_9': 'Playing Time',
            'stats_misc_9': 'Miscellaneous Stats'
        }
        
        # Create Excel writer
        output_file = 'Tottenham_2024-2025_Stats.xlsx'
        writer = pd.ExcelWriter(output_file, engine='openpyxl')
        
        print("Extracting tables...\n")
        
        tables_extracted = 0
        
        for table_id, table_name in table_mapping.items():
            print(f"[{tables_extracted+1}/12] {table_name}...", end=' ')
            
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
                    print(f"✗ Error: {str(e)[:50]}")
            else:
                print(f"✗ Not found (ID: {table_id})")
        
        # Save the Excel file
        if tables_extracted > 0:
            writer.close()
            print(f"\n{'='*60}")
            print(f"Success! {tables_extracted}/12 tables saved to:")
            print(f"{output_file}")
            print(f"{'='*60}")
        else:
            # Create a dummy sheet to avoid error
            pd.DataFrame({'Note': ['No tables were extracted']}).to_excel(writer, sheet_name='Info', index=False)
            writer.close()
            print("\nNo tables were extracted. Check if the page structure has changed.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
