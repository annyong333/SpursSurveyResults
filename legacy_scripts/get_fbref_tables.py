#!/usr/bin/env python3
"""
Script to identify all tables on the FBRef Tottenham stats page
"""

import requests
from bs4 import BeautifulSoup

def main():
    url = "https://fbref.com/en/squads/361ca564/2024-2025/Tottenham-Hotspur-Stats"
    
    print("Fetching Tottenham stats page from FBRef...\n")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
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
                parent = table.find_parent()
                if parent:
                    heading = parent.find_previous(['h2', 'h3', 'h4'])
                    if heading:
                        title = heading.get_text(strip=True)
            
            # Get number of rows and columns
            rows = table.find_all('tr')
            num_rows = len(rows)
            num_cols = 0
            if rows:
                first_row = rows[0]
                num_cols = len(first_row.find_all(['th', 'td']))
            
            table_info.append({
                'number': i,
                'id': table_id,
                'title': title,
                'rows': num_rows,
                'cols': num_cols
            })
            
            print(f"Table {i}:")
            print(f"  ID: {table_id}")
            print(f"  Title: {title}")
            print(f"  Size: {num_rows} rows × {num_cols} columns")
            print("-"*80)
        
        print("\n" + "="*80)
        print("SUMMARY OF ALL TABLES:")
        print("="*80)
        
        for info in table_info:
            print(f"{info['number']:2d}. [{info['id']}]")
            print(f"    {info['title']}")
            print()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
