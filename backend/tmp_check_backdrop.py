import sqlite3
import os
import glob

conn = sqlite3.connect(r"d:\Shared_Bridge\Projects\Jellyfin_data\data\jellyfin.db")
cursor = conn.cursor()

cursor.execute("SELECT Id, Name, Tagline, CommunityRating, OfficialRating, RunTimeTicks FROM BaseItems WHERE Name='Blink Twice' LIMIT 1")
row = cursor.fetchone()
if row:
    guid_bytes, name, tagline, rating, official, ticks = row
    print("Movie:", name)
    print("Tagline:", tagline)
    print("CommunityRating:", rating)
    print("OfficialRating:", official)
    minutes = ticks / 600000000 if ticks else None # 1 tick = 100ns -> 10,000 ticks/ms -> 10,000,000 ticks/s -> 600,000,000 ticks/min
    print("Runtime (minutes):", minutes)
    
    guid_str = ""
    if isinstance(guid_bytes, bytes):
        guid_str = guid_bytes.hex()
    elif isinstance(guid_bytes, str):
        guid_str = guid_bytes.replace("-", "").lower()
        
    prefix = guid_str[:2]
    img_dir = fr"d:\Shared_Bridge\Projects\Jellyfin_data\metadata\library\{prefix}\{guid_str}"
    print("Image dir files:", os.listdir(img_dir) if os.path.exists(img_dir) else "Directory does not exist")
    
conn.close()
