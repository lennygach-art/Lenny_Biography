import json
from pathlib import Path
import re

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "Movies"
DATABASE_FILE = DATA_DIR / "movies.json"
MEDIA_DIRS = [
    Path(r"D:\Shared_Bridge\Movies"),
    Path(r"D:\Shared_Bridge\Anime")
]


def clean_movie_name(folder_name):
    ignore_list = ["Downloading", "aWatched", "WebToolTip"]
    if any(item in folder_name for item in ignore_list):
        return None, None, "Ignore"

    season_pattern = r"^(.*?)[\s\.\(\[]+([sS]\d+|[sS]eason\s*\d+)"
    year_pattern = r"^(.*?)[\s\.\(\[]+(\d{4})"

    match_season = re.search(season_pattern, folder_name)
    if match_season:
        title = match_season.group(1).replace(".", " ").strip(" .([")
        title = re.sub(r"\(\d{4}\)", "", title).strip()
        return title, match_season.group(2).upper(), "TV Show"

    match_year = re.search(year_pattern, folder_name)
    if match_year:
        title = match_year.group(1).replace(".", " ").strip(" .([")
        return title, match_year.group(2), "Movie"

    clean_title = folder_name.replace(".", " ").strip()
    return clean_title, "Unknown", "Other"


def scan_movies():
    movie_list = []
    
    for folder_path in MEDIA_DIRS:
        print(f"--- Starting Scan: {folder_path} ---\n")

        if not folder_path.exists():
            print(f" Error: Could not find path {folder_path}")
            continue

        for entry in folder_path.iterdir():
            if not entry.is_dir():
                continue

            title, year_or_season, media_type = clean_movie_name(entry.name)
            if media_type == "Ignore":
                print(f" Skipping: {entry.name}")
                continue

            movie_data = {
                "display_name": title,
                "year_or_season": year_or_season,
                "type": media_type,
                "folder_name": entry.name,
                "full_path": str(entry),
            }
            movie_list.append(movie_data)
            print(f" Found {media_type}: {title} ({year_or_season})")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with DATABASE_FILE.open("w", encoding="utf-8") as file:
        json.dump(movie_list, file, indent=4)

    print(f"\n---  Success! {len(movie_list)} items saved to {DATABASE_FILE} ---")


if __name__ == "__main__":
    scan_movies()
