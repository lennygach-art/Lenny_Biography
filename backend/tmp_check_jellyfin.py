import sqlite3
import json

conn = sqlite3.connect(r"d:\Shared_Bridge\Projects\Jellyfin_data\data\jellyfin.db")
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(ItemValuesMap);")
print("ItemValuesMap columns:", [c[1] for c in cursor.fetchall()])

cursor.execute("PRAGMA table_info(PeopleBaseItemMap);")
print("PeopleBaseItemMap columns:", [c[1] for c in cursor.fetchall()])

cursor.execute("SELECT * FROM ItemValuesMap LIMIT 1;")
print("ItemValuesMap sample:", cursor.fetchone())

cursor.close()
conn.close()
