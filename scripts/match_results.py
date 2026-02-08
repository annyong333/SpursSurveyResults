"""Match results for Tottenham 2024-25 season.

Manually compiled from Wikipedia's 2024-25 Tottenham Hotspur F.C. season article.
Source: https://en.wikipedia.org/wiki/2024%E2%80%9325_Tottenham_Hotspur_F.C._season

Scores are always (tottenham_score, opponent_score) regardless of venue.
"""

# (date, opponent, tottenham_score, opponent_score, is_tottenham_home, venue)
# is_tottenham_home: True = home, False = away, None = neutral
RESULTS = [
    # Premier League
    ("2024-08-19", "Leicester City",    1, 1, False, "King Power Stadium"),          # Leicester 1-1 Spurs
    ("2024-08-24", "Everton",           4, 0, True,  "Tottenham Hotspur Stadium"),   # Spurs 4-0 Everton
    ("2024-09-01", "Newcastle Utd",     1, 2, False, "St James' Park"),              # Newcastle 2-1 Spurs
    ("2024-09-15", "Arsenal",           0, 1, True,  "Tottenham Hotspur Stadium"),   # Spurs 0-1 Arsenal
    ("2024-09-21", "Brentford",         3, 1, True,  "Tottenham Hotspur Stadium"),   # Spurs 3-1 Brentford
    ("2024-09-29", "Manchester Utd",    3, 0, False, "Old Trafford"),                # Man Utd 0-3 Spurs
    ("2024-10-06", "Brighton",          2, 3, False, "Falmer Stadium"),              # Brighton 3-2 Spurs
    ("2024-10-19", "West Ham",          4, 1, True,  "Tottenham Hotspur Stadium"),   # Spurs 4-1 West Ham
    ("2024-10-27", "Crystal Palace",    0, 1, False, "Selhurst Park"),               # Palace 1-0 Spurs
    ("2024-11-03", "Aston Villa",       4, 1, True,  "Tottenham Hotspur Stadium"),   # Spurs 4-1 Villa
    ("2024-11-10", "Ipswich Town",      1, 2, True,  "Tottenham Hotspur Stadium"),   # Spurs 1-2 Ipswich
    ("2024-11-23", "Manchester City",   4, 0, False, "City of Manchester Stadium"),  # Man City 0-4 Spurs
    ("2024-12-01", "Fulham",            1, 1, True,  "Tottenham Hotspur Stadium"),   # Spurs 1-1 Fulham
    ("2024-12-05", "Bournemouth",       0, 1, False, "Dean Court"),                  # Bournemouth 1-0 Spurs
    ("2024-12-08", "Chelsea",           3, 4, True,  "Tottenham Hotspur Stadium"),   # Spurs 3-4 Chelsea
    ("2024-12-15", "Southampton",       5, 0, False, "St Mary's Stadium"),           # Southampton 0-5 Spurs
    ("2024-12-22", "Liverpool",         3, 6, True,  "Tottenham Hotspur Stadium"),   # Spurs 3-6 Liverpool
    ("2024-12-26", "Nott'ham Forest",   0, 1, False, "City Ground"),                 # Forest 1-0 Spurs
    ("2024-12-29", "Wolves",            2, 2, True,  "Tottenham Hotspur Stadium"),   # Spurs 2-2 Wolves
    ("2025-01-04", "Newcastle Utd",     1, 2, True,  "Tottenham Hotspur Stadium"),   # Spurs 1-2 Newcastle
    ("2025-01-15", "Arsenal",           1, 2, False, "Emirates Stadium"),            # Arsenal 2-1 Spurs
    ("2025-01-19", "Everton",           2, 3, False, "Goodison Park"),               # Everton 3-2 Spurs
    ("2025-01-26", "Leicester City",    1, 2, True,  "Tottenham Hotspur Stadium"),   # Spurs 1-2 Leicester
    ("2025-02-02", "Brentford",         2, 0, False, "Brentford Community Stadium"), # Brentford 0-2 Spurs
    ("2025-02-16", "Manchester Utd",    1, 0, True,  "Tottenham Hotspur Stadium"),   # Spurs 1-0 Man Utd
    ("2025-02-22", "Ipswich Town",      4, 1, False, "Portman Road"),                # Ipswich 1-4 Spurs
    ("2025-02-26", "Manchester City",   0, 1, True,  "Tottenham Hotspur Stadium"),   # Spurs 0-1 Man City
    ("2025-03-09", "Bournemouth",       2, 2, True,  "Tottenham Hotspur Stadium"),   # Spurs 2-2 Bournemouth
    ("2025-03-16", "Fulham",            0, 2, False, "Craven Cottage"),              # Fulham 2-0 Spurs
    ("2025-04-02", "Chelsea",           0, 1, False, "Stamford Bridge"),             # Chelsea 1-0 Spurs
    ("2025-04-05", "Southampton",       3, 1, True,  "Tottenham Hotspur Stadium"),   # Spurs 3-1 Southampton
    ("2025-04-12", "Wolves",            2, 4, False, "Molineux Stadium"),            # Wolves 4-2 Spurs
    ("2025-04-19", "Nott'ham Forest",   1, 2, True,  "Tottenham Hotspur Stadium"),   # Spurs 1-2 Forest
    ("2025-04-26", "Liverpool",         1, 5, False, "Anfield"),                     # Liverpool 5-1 Spurs
    ("2025-05-03", "West Ham",          1, 2, False, "London Stadium"),              # West Ham 2-1 Spurs
    ("2025-05-10", "Crystal Palace",    2, 0, True,  "Tottenham Hotspur Stadium"),   # Spurs 2-0 Palace
    ("2025-05-18", "Aston Villa",       0, 1, False, "Villa Park"),                  # Villa 1-0 Spurs
    ("2025-05-25", "Brighton",          1, 3, True,  "Tottenham Hotspur Stadium"),   # Spurs 1-3 Brighton
    # EFL Cup
    ("2024-09-18", "Coventry City",     2, 1, True,  "Tottenham Hotspur Stadium"),   # Spurs 2-1 Coventry
    ("2024-10-30", "Manchester City",   2, 1, True,  "Tottenham Hotspur Stadium"),   # Spurs 2-1 Man City
    ("2024-12-19", "Manchester Utd",    4, 3, True,  "Tottenham Hotspur Stadium"),   # Spurs 4-3 Man Utd
    ("2025-01-08", "Liverpool",         1, 0, True,  "Tottenham Hotspur Stadium"),   # Spurs 1-0 Liverpool
    ("2025-02-06", "Liverpool",         0, 4, False, "Anfield"),                     # Liverpool 4-0 Spurs
    # FA Cup
    ("2025-01-12", "Tamworth",          3, 0, False, "The Lamb Ground"),             # Tamworth 0-3 Spurs
    ("2025-02-09", "Aston Villa",       0, 2, False, "Villa Park"),                  # Villa 2-0 Spurs
    # Europa League
    ("2024-09-26", "az Qarabağ",        3, 0, True,  "Tottenham Hotspur Stadium"),   # Spurs 3-0 Qarabag
    ("2024-10-03", "hu Ferencváros",    2, 1, True,  "Tottenham Hotspur Stadium"),   # Spurs 2-1 Ferencvaros
    ("2024-10-24", "nl AZ Alkmaar",     1, 0, False, "AFAS Stadion"),                # AZ 0-1 Spurs
    ("2024-11-07", "tr Galatasaray",    3, 2, True,  "Tottenham Hotspur Stadium"),   # Spurs 3-2 Galatasaray
    ("2024-11-28", "it Roma",           2, 2, False, "Stadio Olimpico"),             # Roma 2-2 Spurs
    ("2024-12-12", "sct Rangers",       1, 1, False, "Ibrox Stadium"),               # Rangers 1-1 Spurs
    ("2025-01-23", "de Hoffenheim",     3, 0, True,  "Tottenham Hotspur Stadium"),   # Spurs 3-0 Hoffenheim
    ("2025-01-30", "se Elfsborg",       3, 0, True,  "Tottenham Hotspur Stadium"),   # Spurs 3-0 Elfsborg
    ("2025-03-06", "nl AZ Alkmaar",     1, 0, True,  "Tottenham Hotspur Stadium"),   # Spurs 1-0 AZ
    ("2025-03-13", "nl AZ Alkmaar",     3, 2, False, "AFAS Stadion"),                # AZ 2-3 Spurs
    ("2025-04-10", "de Eint Frankfurt", 1, 0, True,  "Tottenham Hotspur Stadium"),   # Spurs 1-0 Frankfurt
    ("2025-04-17", "de Eint Frankfurt", 1, 1, False, "Deutsche Bank Park"),          # Frankfurt 1-1 Spurs
    ("2025-05-01", "no Bodø/Glimt",     3, 1, True,  "Tottenham Hotspur Stadium"),   # Spurs 3-1 Bodo/Glimt
    ("2025-05-08", "no Bodø/Glimt",     2, 0, False, "Aspmyra Stadion"),             # Bodo/Glimt 0-2 Spurs
    ("2025-05-21", "Manchester Utd",    1, 0, None,  "San Mamés Stadium"),           # EL Final (neutral) Spurs 1-0 Man Utd
]
