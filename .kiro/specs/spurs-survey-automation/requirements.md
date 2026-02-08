# Requirements Document

## Introduction

An automated system for managing post-match player rating surveys for the Tottenham Hotspur subreddit (r/coys). The system replaces a manual workflow of creating Google Forms surveys, collecting responses, and generating results infographics. It fetches match data (lineups, formations, substitutions) from free APIs, creates surveys automatically, compiles results with statistics, generates visual infographics, and hosts a browsable archive of all past match surveys.

## Glossary

- **Survey_Generator**: The component responsible for creating post-match rating surveys from match data
- **Match_Data_Fetcher**: The component that retrieves lineup, formation, and substitution data from external football APIs
- **Infographic_Generator**: The component that produces visual results images from survey response data
- **Results_Archive**: The web-based repository for browsing and sharing past match survey results
- **Rating_Scale**: The 0–10 integer scale used for all player, coach, team, and referee ratings
- **Formation**: The tactical arrangement of players on the pitch (e.g., 4-4-2, 3-5-2)
- **Starting_Player**: A player in the starting eleven lineup for a match
- **Substitute_Player**: A player who enters the match as a replacement for a Starting_Player
- **Man_of_the_Match**: A single player voted as the best performer by survey respondents
- **Match_Metadata**: Information identifying a match including opponent name, competition name, matchday label, and date

## Requirements

### Requirement 1: Fetch Match Data

**User Story:** As a survey administrator, I want the system to automatically retrieve match lineups, formations, and substitutions from free APIs, so that I do not have to manually look up and enter this data.

#### Acceptance Criteria

1. WHEN a Tottenham match lineup is released (approximately one hour before kickoff), THE Match_Data_Fetcher SHALL retrieve the starting eleven lineup, formation, and coach name from a free football data API
2. WHEN lineup data is retrieved, THE Match_Data_Fetcher SHALL map each player name to the corresponding player image filename in the local image directory
3. WHEN substitution events occur during a match, THE Match_Data_Fetcher SHALL retrieve the list of Substitute_Players and the Starting_Players they replaced
4. IF the external API is unavailable or returns incomplete data, THEN THE Match_Data_Fetcher SHALL report the specific missing fields and allow manual entry of the missing data
5. WHEN match data is retrieved, THE Match_Data_Fetcher SHALL extract the Match_Metadata including opponent name, competition name, matchday label, and match date

### Requirement 2: Generate Post-Match Survey

**User Story:** As a survey administrator, I want the system to automatically create a post-match rating survey from match data, so that I do not have to manually build a form for every match.

#### Acceptance Criteria

1. WHEN match data including lineup and substitutions is available, THE Survey_Generator SHALL create a survey containing sections in this order: team rating, opponent rating, coach ratings (starting eleven selection, on-field tactics, substitution decisions), referee rating, Starting_Player ratings, Substitute_Player ratings, and Man_of_the_Match vote
2. THE Survey_Generator SHALL use the Rating_Scale (0–10 integers) for all rating questions and display the rating scale descriptions (0 = "Worst Performance of the Year Contender" through 10 = "Perfect Performance") once at the top of the survey as a reference guide
3. WHEN generating the Man_of_the_Match question, THE Survey_Generator SHALL include all Starting_Players and all Substitute_Players as selectable options
4. WHEN a match has zero substitutions, THE Survey_Generator SHALL omit the Substitute_Player ratings section and include only Starting_Players in the Man_of_the_Match vote
5. THE Survey_Generator SHALL produce a shareable survey link that can be posted to the subreddit

### Requirement 3: Compile Survey Results

**User Story:** As a survey administrator, I want the system to compile survey responses into structured statistics, so that I can present accurate match ratings to the community.

#### Acceptance Criteria

1. WHEN survey responses are collected, THE Survey_Generator SHALL compute the arithmetic mean and standard deviation for each rated entity (team, opponent, referee, each Starting_Player, each Substitute_Player, and each tactical category: starting eleven selection, on-field tactics, substitutions)
2. WHEN computing Man_of_the_Match results, THE Survey_Generator SHALL determine the player with the most votes
3. WHEN two or more players tie for the most Man_of_the_Match votes, THE Survey_Generator SHALL report all tied players as co-winners
4. THE Survey_Generator SHALL compute an overall rating as the mean of all individual player ratings in the match
5. THE Survey_Generator SHALL record the total number of survey responses
6. THE Survey_Generator SHALL output compiled results as structured data (JSON) containing all computed statistics, Match_Metadata, and total response count

### Requirement 4: Generate Results Infographic

**User Story:** As a survey administrator, I want the system to generate a visual infographic from compiled survey results, so that I can share a polished image on the subreddit.

#### Acceptance Criteria

1. WHEN compiled results data is provided, THE Infographic_Generator SHALL produce a 16:9 landscape image using a three-column layout: left sidebar (match info), main content (formation), and right sidebar (substitutions)
2. THE Infographic_Generator SHALL render the left sidebar with a navy background containing: match header (competition week, venue, date), score block with both team names and scores alongside team ratings, an overall rating displayed in a diamond shape, a manager card with coach name and tactical ratings (starting eleven selection, on-field tactics, substitutions), a "Photo of the Match" area, and a "Quote of the Match" text area
3. WHEN rendering the main content area, THE Infographic_Generator SHALL arrange Starting_Players visually according to the Formation they played (e.g., 4-3-3 layout with goalkeeper at bottom, defenders, midfielders, and forwards in rows) over a blurred stadium background with a blue overlay
4. WHEN rendering each player card, THE Infographic_Generator SHALL display the player image, an uppercase name on a black pill-shaped plate, a yellow circle containing the average rating rounded to one decimal place, and the standard deviation as a small gray number beside the rating circle
5. THE Infographic_Generator SHALL display event badges on player cards for goals (soccer ball icon), assists (boot icon), own goals, and Man_of_the_Match (MOTM badge)
6. WHEN rendering the right sidebar, THE Infographic_Generator SHALL display Substitute_Players in a vertical list using the same player card format as the main content area
7. THE Infographic_Generator SHALL display the referee rating in the main content area
8. THE Infographic_Generator SHALL display the total number of survey responses in the main content header
9. WHEN a player image file is not found for a player, THE Infographic_Generator SHALL render a placeholder silhouette image instead of failing
10. THE Infographic_Generator SHALL include a legend explaining the visual symbols (yellow circle for average rating, soccer ball for goal, boot for assist, gray number for standard deviation)

### Requirement 5: Host Results Archive

**User Story:** As a subreddit member, I want to browse past match survey results on a website, so that I can view historical ratings and share specific match results via link.

#### Acceptance Criteria

1. THE Results_Archive SHALL display a list of all past match surveys sorted by match date with the most recent match first
2. WHEN a user selects a match from the list, THE Results_Archive SHALL display the results infographic for that match
3. THE Results_Archive SHALL allow filtering matches by opponent name, competition name, and date range
4. THE Results_Archive SHALL generate a unique shareable URL for each match result page
5. THE Results_Archive SHALL store raw survey response data alongside compiled results for each match

### Requirement 6: Serialize and Deserialize Match Results

**User Story:** As a system maintainer, I want match results to be stored in a structured format and faithfully restored, so that data integrity is preserved across storage and retrieval cycles.

#### Acceptance Criteria

1. WHEN compiled results are produced, THE Survey_Generator SHALL serialize the results to JSON format for storage
2. WHEN results are loaded from storage, THE Results_Archive SHALL deserialize the JSON back into the original data structure
3. FOR ALL valid compiled results, serializing to JSON and then deserializing SHALL produce a data structure equivalent to the original
