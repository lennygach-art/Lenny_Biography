import json
from pathlib import Path
import sqlite3

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
    
    new_columns = {
        "backdrop": "TEXT",
        "tagline": "TEXT",
        "official_rating": "TEXT",
        "community_rating": "REAL",
        "runtime": "INTEGER"
    }
    for col, dtype in new_columns.items():
        try:
            cursor.execute(f"ALTER TABLE movies ADD COLUMN {col} {dtype}")
        except sqlite3.OperationalError:
            pass


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
    import shutil
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    jellyfin_db_path = r"d:\Shared_Bridge\Projects\Jellyfin_data\data\jellyfin.db"
    if not Path(jellyfin_db_path).exists():
        print(f"Error: Jellyfin DB not found at {jellyfin_db_path}")
        return

    jellyfin_conn = sqlite3.connect(jellyfin_db_path)
    jf_cursor = jellyfin_conn.cursor()

    THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)

    cursor.execute("SELECT display_name FROM movies")
    local_movies = [row[0] for row in cursor.fetchall()]

    for name in local_movies:
        search_query = """
            SELECT Id, Overview, ProductionYear, Tagline, CommunityRating, OfficialRating, RunTimeTicks
            FROM BaseItems 
            WHERE {condition}
            LIMIT 1
        """
        
        # 1. Exact name match (Movie, Series, or BoxSet)
        jf_cursor.execute(search_query.format(condition="Name=? AND (Type LIKE '%Movie%' OR Type LIKE '%Series%' OR Type LIKE '%BoxSet%')"), (name,))
        row = jf_cursor.fetchone()
        
        # Regex clean
        import re
        clean_name = re.sub(r'(?i)SEASON\s*\d+|English Dub|\b(20\d{2}|19\d{2})\b', '', name).strip()
        
        # 2. Cleaned name exact
        if not row and clean_name and clean_name != name:
            jf_cursor.execute(search_query.format(condition="Name=? AND (Type LIKE '%Movie%' OR Type LIKE '%Series%' OR Type LIKE '%BoxSet%')"), (clean_name,))
            row = jf_cursor.fetchone()
                
        # 3. Cleaned name Starts-With
        if not row and clean_name:
            jf_cursor.execute(search_query.format(condition="Name LIKE ? AND (Type LIKE '%Movie%' OR Type LIKE '%Series%' OR Type LIKE '%BoxSet%')"), (f"{clean_name}%",))
            row = jf_cursor.fetchone()
            
        # 4. First 2 words Contains (salvaging weird Jellyfin scraped titles)
        if not row and clean_name:
            first_words = " ".join(clean_name.split()[:2])
            if first_words and len(first_words) > 3:
                jf_cursor.execute(search_query.format(condition="Name LIKE ? AND (Type LIKE '%Movie%' OR Type LIKE '%Series%' OR Type LIKE '%BoxSet%')"), (f"%{first_words}%",))
                row = jf_cursor.fetchone()

        # 5. Nuclear fallback: completely ignore Type filters
        if not row and clean_name:
            jf_cursor.execute(search_query.format(condition="Name LIKE ?"), (f"%{clean_name}%",))
            row = jf_cursor.fetchone()
            
        if not row:
            print(f"Skipping {name}: Not found in Jellyfin even with fuzzy match.")
            continue
            
        movie_guid_bytes, synopsis, year, tagline, comm_rating, off_rating, ticks = row
        synopsis = synopsis or "No description available."
        runtime = int(ticks / 600000000) if ticks else 0
        
        if isinstance(movie_guid_bytes, bytes):
            guid_str = movie_guid_bytes.hex()
        elif isinstance(movie_guid_bytes, str):
            guid_str = movie_guid_bytes.replace("-", "").lower()
        else:
            continue
            
        jf_cursor.execute(
            """
            SELECT ItemValues.CleanValue 
            FROM ItemValues 
            JOIN ItemValuesMap on ItemValues.ItemValueId = ItemValuesMap.ItemValueId 
            WHERE ItemValuesMap.ItemId = ? AND ItemValues.Type = 1
            """,
            (movie_guid_bytes,)
        )
        genres = ", ".join([g[0] for g in jf_cursor.fetchall()])
        
        CAST_DIR = PROJECT_ROOT / "static" / "cast"
        CAST_DIR.mkdir(parents=True, exist_ok=True)
        
        jf_cursor.execute(
            """
            SELECT Peoples.Name, PeopleBaseItemMap.Role, Peoples.Id 
            FROM Peoples 
            JOIN PeopleBaseItemMap on Peoples.Id = PeopleBaseItemMap.PeopleId 
            WHERE PeopleBaseItemMap.ItemId = ? 
            ORDER BY PeopleBaseItemMap.ListOrder 
            LIMIT 10
            """,
            (movie_guid_bytes,)
        )
        
        cast = []
        for person_name, role, person_id_bytes in jf_cursor.fetchall():
            person_img_url = None
            if person_name:
                initial = person_name[0].lower()
                jf_person_img = Path(fr"d:\Shared_Bridge\Projects\Jellyfin_data\metadata\people\{initial}\{person_name}\folder.jpg")
                if jf_person_img.exists():
                    person_guid_str = ""
                    if isinstance(person_id_bytes, bytes):
                        person_guid_str = person_id_bytes.hex()
                    elif isinstance(person_id_bytes, str):
                        person_guid_str = person_id_bytes.replace("-", "").lower()
                    else:
                        person_guid_str = "".join(x for x in person_name if x.isalnum())
                        
                    dest_filename = f"{person_guid_str}.jpg"
                    dest_path = CAST_DIR / dest_filename
                    shutil.copy2(jf_person_img, dest_path)
                    person_img_url = dest_filename
                    
            cast.append({"name": person_name, "role": role or "Actor", "image": person_img_url})
            
        cast_json = json.dumps(cast)
        
        prefix = guid_str[:2]
        jf_img_path = Path(fr"d:\Shared_Bridge\Projects\Jellyfin_data\metadata\library\{prefix}\{guid_str}\poster.jpg")
        jf_bg_path = Path(fr"d:\Shared_Bridge\Projects\Jellyfin_data\metadata\library\{prefix}\{guid_str}\backdrop.jpg")
        
        img_dest_path = THUMBNAILS_DIR / f"{guid_str}.jpg"
        bg_dest_path = THUMBNAILS_DIR / f"{guid_str}_bg.jpg"
        
        if jf_img_path.exists():
            shutil.copy2(jf_img_path, img_dest_path)
        if jf_bg_path.exists():
            shutil.copy2(jf_bg_path, bg_dest_path)
            
        cursor.execute(
            """
            UPDATE movies
            SET thumbnail = ?, synopsis = ?, cast_list = ?, genres = ?,
                backdrop = ?, tagline = ?, official_rating = ?, community_rating = ?, runtime = ?
            WHERE display_name = ?
            """,
            (
                str(img_dest_path) if jf_img_path.exists() else None, 
                synopsis, cast_json, genres,
                str(bg_dest_path) if jf_bg_path.exists() else None,
                tagline, off_rating, comm_rating, runtime,
                name
            ),
        )
        print(f"Harvested {name} from local Jellyfin data.")

    conn.commit()
    conn.close()
    jellyfin_conn.close()
    print("Harvest Complete! Extracted metadata directly from Jellyfin local database.")

if __name__ == "__main__":
    setup_database()
