# FBRef Data Extraction Guide for Tottenham Stats

FBRef has strong anti-scraping protections. Here are your options:

## Option 1: Manual Download (Recommended)
1. Visit: https://fbref.com/en/squads/361ca564/2024-2025/Tottenham-Hotspur-Stats
2. For each table you want:
   - Click the "Share & Export" button (usually at top-right of each table)
   - Select "Get table as CSV (for Excel)"
   - Save the CSV file
3. Use the script below to combine all CSVs into one Excel file

## Option 2: Browser Extension
Use a browser extension like "Table Capture" or "Data Scraper" to extract tables directly from your browser.

## Option 3: StatsBomb/Opta Data
Consider using official data providers:
- StatsBomb Open Data (free): https://github.com/statsbomb/open-data
- Opta (paid)
- Understat (free API for some data)

## Tables Available on FBRef Page:

1. **Standard Stats** (ID: stats_standard_9)
   - Goals, assists, minutes played, etc.

2. **Scores & Fixtures** (ID: matchlogs_for)
   - Match results and schedule

3. **Goalkeeping** (ID: stats_keeper_9)
   - Saves, clean sheets, goals against

4. **Advanced Goalkeeping** (ID: stats_keeper_adv_9)
   - PSxG, launch %, pass completion

5. **Shooting** (ID: stats_shooting_9)
   - Shots, shots on target, xG

6. **Passing** (ID: stats_passing_9)
   - Pass completion, progressive passes

7. **Pass Types** (ID: stats_passing_types_9)
   - Through balls, crosses, corners

8. **Goal and Shot Creation** (ID: stats_gca_9)
   - Shot-creating actions, goal-creating actions

9. **Defensive Actions** (ID: stats_defense_9)
   - Tackles, interceptions, blocks

10. **Possession** (ID: stats_possession_9)
    - Touches, dribbles, carries

11. **Playing Time** (ID: stats_playing_time_9)
    - Minutes, starts, subs

12. **Miscellaneous Stats** (ID: stats_misc_9)
    - Cards, fouls, aerial duels

## Script to Combine CSV Files

Once you've downloaded the CSV files, use this script:

```python
import pandas as pd
import glob

# Put all your CSV files in a folder called "fbref_csvs"
csv_files = glob.glob("fbref_csvs/*.csv")

writer = pd.ExcelWriter('Tottenham_2024-2025_Stats.xlsx', engine='openpyxl')

for csv_file in csv_files:
    df = pd.read_csv(csv_file)
    sheet_name = csv_file.split('/')[-1].replace('.csv', '')[:31]
    df.to_excel(writer, sheet_name=sheet_name, index=False)

writer.close()
print("All CSV files combined into Excel!")
```

## For Historical Data (2012-2024)

You'll need to visit each season's page:
- 2024-2025: /en/squads/361ca564/2024-2025/Tottenham-Hotspur-Stats
- 2023-2024: /en/squads/361ca564/2023-2024/Tottenham-Hotspur-Stats
- 2022-2023: /en/squads/361ca564/2022-2023/Tottenham-Hotspur-Stats
- etc.

Change the year in the URL for each season back to 2012-2013.
