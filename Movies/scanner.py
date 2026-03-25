import os
import re
import json

# 1. Configuration - Point this to your actual movie folder
# Since you are on Windows, we use the 'r' prefix for the path
MOVIE_DIR = r"D:\Shared_Bridge\Movies"
DATABASE_FILE = "movies.json"

def clean_movie_name(folder_name): #Cleans messy folder names into professional Titles, Years/Seasons, and Media Types.
    # Folders to ignore completely (Junk/System folders)
    ignore_list = ['Downloading', 'aWatched', 'WebToolTip']
    if any(x in folder_name for x in ignore_list):
        return None, None, "Ignore"

    # Pattern for TV Shows (Looking for S01, S1, or Season 1)
    # We check this first to avoid mislabeling shows that have a year in the title
    season_pattern = r"^(.*?)[\s\. \(\[]+([sS]\d+|[sS]eason\s*\d+)"
    
    # Pattern for Movies (Looking for 4-digit years 1900-2099)
    year_pattern = r"^(.*?)[\s\. \(\[]+(\d{4})"

    # CHECK FOR TV SHOWS FIRST
    match_season = re.search(season_pattern, folder_name)
    if match_season:
        title = match_season.group(1).replace('.', ' ').strip(' .([')
        # Remove the year from titles like "BoJack Horseman (2014)" if it exists
        title = re.sub(r'\(\d{4}\)', '', title).strip() 
        return title, match_season.group(2).upper(), "TV Show"

    # CHECK FOR MOVIES SECOND
    match_year = re.search(year_pattern, folder_name)
    if match_year:
        title = match_year.group(1).replace('.', ' ').strip(' .([')
        return title, match_year.group(2), "Movie"

    # FALLBACK (For things like "Blue Exorcist English Dub")
    clean_title = folder_name.replace('.', ' ').strip()
    return clean_title, "Unknown", "Other"

def scan_movies():
    movie_list = []
    print(f"--- Starting Scan: {MOVIE_DIR} ---\n")

    # The Loop: Iterate through every item in your directory
    if not os.path.exists(MOVIE_DIR):
        print(f" Error: Could not find path {MOVIE_DIR}")
        return

    for entry in os.listdir(MOVIE_DIR):
        full_path = os.path.join(MOVIE_DIR, entry)
        
        # We only want to scan folders, not random files
        if os.path.isdir(full_path):
            title, year_or_season, media_type = clean_movie_name(entry)
            
            # Skip junk folders defined in the ignore list
            if media_type == "Ignore":
                print(f" Skipping: {entry}")
                continue
            
            # Create the Virtual Map (Data Entry for your website)
            movie_data = {
                "display_name": title,
                "year_or_season": year_or_season,
                "type": media_type,
                "folder_name": entry,
                "full_path": full_path
            }
            movie_list.append(movie_data)
            print(f" Found {media_type}: {title} ({year_or_season})")

    # Save to Local JSON Database
    with open(DATABASE_FILE, 'w') as f:
        json.dump(movie_list, f, indent=4)
    
    print(f"\n---  Success! {len(movie_list)} items saved to {DATABASE_FILE} ---")

if __name__ == "__main__":
    scan_movies()