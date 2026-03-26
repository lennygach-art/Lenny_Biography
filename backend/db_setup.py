import json
from pathlib import Path
import sqlite3

import requests

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
MOVIES_JSON_PATH = DATA_DIR / "Movies" / "movies.json"
DATABASE_PATH = BACKEND_DIR / "data" / "portal_db.db"
THUMBNAILS_DIR = PROJECT_ROOT / "static" / "thumbnails"

JELLYFIN_URL = "http://localhost:8096"
API_KEY = "YOUR_API_KEY"
USER_ID = "YOUR_USER_ID"


def setup_database():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            display_name TEXT,
            year TEXT,
            type TEXT,
            full_path TEXT UNIQUE,
            thumbnail TEXT,
            synopsis TEXT,
            cast_list TEXT,
            genres TEXT,
            is_favorite INTEGER DEFAULT 0,
            last_position INTEGER DEFAULT 0
        )
        """
    )

    if MOVIES_JSON_PATH.exists():
        with MOVIES_JSON_PATH.open("r", encoding="utf-8") as file:
            movies_data = json.load(file)

        for movie in movies_data:
            cursor.execute(
                """
                INSERT OR IGNORE INTO movies (display_name, year, type, full_path)
                VALUES (?, ?, ?, ?)
                """,
                (
                    movie["display_name"],
                    movie["year_or_season"],
                    movie["type"],
                    movie["full_path"],
                ),
            )

    conn.commit()
    conn.close()
    print("Database synced with movies.json successfully!")


def harvest():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    url = (
        f"{JELLYFIN_URL}/Users/{USER_ID}/Items?api_key={API_KEY}"
        "&IncludeItemTypes=Movie&Recursive=true"
        "&Fields=Overview,People,Genres,ProductionYear"
    )
    response = requests.get(url, timeout=30).json()

    THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)

    for item in response.get("Items", []):
        name = item.get("Name")
        movie_id = item.get("Id")
        synopsis = item.get("Overview", "No description available.")
        genres = ", ".join(item.get("Genres", []))

        cast = [
            {"name": person["Name"], "role": person.get("Role", "Actor")}
            for person in item.get("People", [])[:5]
        ]
        cast_json = json.dumps(cast)

        img_path = THUMBNAILS_DIR / f"{movie_id}.jpg"
        img_data = requests.get(
            f"{JELLYFIN_URL}/Items/{movie_id}/Images/Primary",
            timeout=30,
        ).content
        with img_path.open("wb") as file:
            file.write(img_data)

        cursor.execute(
            """
            UPDATE movies
            SET thumbnail = ?, synopsis = ?, cast_list = ?, genres = ?
            WHERE display_name = ?
            """,
            (str(img_path), synopsis, cast_json, genres, name),
        )

    conn.commit()
    conn.close()
    print("Harvest Complete! You can now turn off Jellyfin.")


if __name__ == "__main__":
    setup_database()
