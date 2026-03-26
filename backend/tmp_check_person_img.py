import sqlite3
import os

conn = sqlite3.connect(r"d:\Shared_Bridge\Projects\Jellyfin_data\data\jellyfin.db")
cursor = conn.cursor()

cursor.execute("SELECT hex(Id), Name FROM Peoples WHERE Name='Channing Tatum' LIMIT 1")
row = cursor.fetchone()
if row:
    print("Found person:", row)
    hex_id, name = row
    
    guid_str = hex_id.lower()
    
    # Check possible paths
    paths_to_check = [
        fr"d:\Shared_Bridge\Projects\Jellyfin_data\metadata\people\{name[0].lower()}\{name}\folder.jpg",
        fr"d:\Shared_Bridge\Projects\Jellyfin_data\metadata\people\{name[0].lower()}\{name}\poster.jpg",
        fr"d:\Shared_Bridge\Projects\Jellyfin_data\metadata\library\{guid_str[:2]}\{guid_str}\folder.jpg",
    ]
    
    for path in paths_to_check:
        print(f"Checking {path}: {os.path.exists(path)}")
else:
    print("Not found")

conn.close()
