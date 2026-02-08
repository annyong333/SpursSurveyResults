"""Match results for Tottenham 2024-25 season.

Manually compiled from Wikipedia's 2024-25 Tottenham Hotspur F.C. season article.
Source: https://en.wikipedia.org/wiki/2024%E2%80%9325_Tottenham_Hotspur_F.C._season
"""

# (date, opponent_in_spreadsheet, home_score, away_score, is_tottenham_home, venue)
RESULTS = [
    # Premier League
    ("2024-08-19", "Leicester City", 1, 1, False, "King Power Stadium"),
    ("2024-08-24", "Everton", 4, 0, True, "Tottenham Hotspur Stadium"),
    ("2024-09-01", "Newcastle Utd", 2, 1, False, "St James' Park"),
    ("2024-09-15", "Arsenal", 0, 1, True, "Tottenham Hotspur Stadium"),
    ("2024-09-21", "Brentford", 3, 1, True, "Tottenham Hotspur Stadium"),
    ("2024-09-29", "Manchester Utd", 0, 3, False, "Old Trafford"),
    ("2024-10-06", "Brighton", 3, 2, False, "Falmer Stadium"),
    ("2024-10-19", "West Ham", 4, 1, True, "Tottenham Hotspur Stadium"),
    ("2024-10-27", "Crystal Palace", 1, 0, False, "Selhurst Park"),
    ("2024-11-03", "Aston Villa", 4, 1, True, "Tottenham Hotspur Stadium"),
    ("2024-11-10", "Ipswich Town", 1, 2, True, "Tottenham Hotspur Stadium"),
    ("2024-11-23", "Manchester City", 0, 4, False, "City of Manchester Stadium"),
    ("2024-12-01", "Fulham", 1, 1, True, "Tottenham Hotspur Stadium"),
    ("2024-12-05", "Bournemouth", 1, 0, False, "Dean Court"),
    ("2024-12-08", "Chelsea", 3, 4, True, "Tottenham Hotspur Stadium"),
    ("2024-12-15", "Southampton", 0, 5, False, "St Mary's Stadium"),
    ("2024-12-22", "Liverpool", 3, 6, True, "Tottenham Hotspur Stadium"),
    ("2024-12-26", "Nott'ham Forest", 1, 0, False, "City Ground"),
    ("2024-12-29", "Wolves", 2, 2, True, "Tottenham Hotspur Stadium"),
    ("2025-01-04", "Newcastle Utd", 1, 2, True, "Tottenham Hotspur Stadium"),
    ("2025-01-15", "Arsenal", 2, 1, False, "Emirates Stadium"),
    ("2025-01-19", "Everton", 3, 2, False, "Goodison Park"),
    ("2025-01-26", "Leicester City", 1, 2, True, "Tottenham Hotspur Stadium"),
    ("2025-02-02", "Brentford", 0, 2, False, "Brentford Community Stadium"),
    ("2025-02-16", "Manchester Utd", 1, 0, True, "Tottenham Hotspur Stadium"),
    ("2025-02-22", "Ipswich Town", 1, 4, False, "Portman Road"),
    ("2025-02-26", "Manchester City", 0, 1, True, "Tottenham Hotspur Stadium"),
    ("2025-03-09", "Bournemouth", 2, 2, True, "Tottenham Hotspur Stadium"),
    ("2025-03-16", "Fulham", 2, 0, False, "Craven Cottage"),
    ("2025-04-02", "Chelsea", 1, 0, False, "Stamford Bridge"),
    ("2025-04-05", "Southampton", 3, 1, True, "Tottenham Hotspur Stadium"),
    ("2025-04-12", "Wolves", 4, 2, False, "Molineux Stadium"),
    ("2025-04-19", "Nott'ham Forest", 1, 2, True, "Tottenham Hotspur Stadium"),
    ("2025-04-26", "Liverpool", 5, 1, False, "Anfield"),
    ("2025-05-03", "West Ham", 2, 1, False, "London Stadium"),
    ("2025-05-10", "Crystal Palace", 2, 0, True, "Tottenham Hotspur Stadium"),
    ("2025-05-18", "Aston Villa", 1, 0, False, "Villa Park"),
    ("2025-05-25", "Brighton", 1, 3, True, "Tottenham Hotspur Stadium"),
    # EFL Cup
    ("2024-09-18", "Coventry City", 2, 1, True, "Tottenham Hotspur Stadium"),
    ("2024-10-30", "Manchester City", 2, 1, True, "Tottenham Hotspur Stadium"),
    ("2024-12-19", "Manchester Utd", 4, 3, True, "Tottenham Hotspur Stadium"),
    ("2025-01-08", "Liverpool", 1, 0, True, "Tottenham Hotspur Stadium"),
    ("2025-02-06", "Liverpool", 0, 4, False, "Anfield"),
    # FA Cup
    ("2025-01-12", "Tamworth", 3, 0, False, "The Lamb Ground"),
    ("2025-02-09", "Aston Villa", 0, 2, False, "Villa Park"),
    # Europa League
    ("2024-09-26", "az Qarabağ", 3, 0, True, "Tottenham Hotspur Stadium"),
    ("2024-10-03", "hu Ferencváros", 2, 1, True, "Tottenham Hotspur Stadium"),
    ("2024-10-24", "nl AZ Alkmaar", 1, 0, False, "AFAS Stadion"),
    ("2024-11-07", "tr Galatasaray", 3, 2, True, "Tottenham Hotspur Stadium"),
    ("2024-11-28", "it Roma", 2, 2, False, "Stadio Olimpico"),
    ("2024-12-12", "sct Rangers", 1, 1, False, "Ibrox Stadium"),
    ("2025-01-23", "de Hoffenheim", 3, 0, True, "Tottenham Hotspur Stadium"),
    ("2025-01-30", "se Elfsborg", 3, 0, True, "Tottenham Hotspur Stadium"),
    ("2025-03-06", "nl AZ Alkmaar", 1, 0, True, "Tottenham Hotspur Stadium"),
    ("2025-03-13", "nl AZ Alkmaar", 3, 2, False, "AFAS Stadion"),
    ("2025-04-10", "de Eint Frankfurt", 1, 0, True, "Tottenham Hotspur Stadium"),
    ("2025-04-17", "de Eint Frankfurt", 1, 1, False, "Deutsche Bank Park"),
    ("2025-05-01", "no Bodø/Glimt", 3, 1, True, "Tottenham Hotspur Stadium"),
    ("2025-05-08", "no Bodø/Glimt", 2, 0, False, "Aspmyra Stadion"),
    ("2025-05-21", "Manchester Utd", 1, 0, False, "San Mamés Stadium"),  # EL Final (neutral)
]
