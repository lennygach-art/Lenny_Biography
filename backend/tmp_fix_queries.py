import sqlite3

conn = sqlite3.connect(r"d:\Shared_Bridge\Projects\Jellyfin_data\data\jellyfin.db")
cursor = conn.cursor()

cursor.execute("SELECT Id FROM BaseItems WHERE Name='Blink Twice' LIMIT 1")
row = cursor.fetchone()
if not row:
    print("Movie not found!")
    exit()
item_id = row[0]
print("ItemId type:", type(item_id))

try:
    cursor.execute(
        """
        SELECT ItemValues.CleanValue 
        FROM ItemValues 
        JOIN ItemValuesMap on ItemValues.ItemValueId = ItemValuesMap.ItemValueId 
        WHERE ItemValuesMap.ItemId = ? AND ItemValues.Type = 1
        """,
        (item_id,)
    )
    print("Genres:", [g[0] for g in cursor.fetchall()])
except Exception as e:
    print("Genre Error:", e)

try:
    cursor.execute(
        """
        SELECT Peoples.Name, PeopleBaseItemMap.Role 
        FROM Peoples 
        JOIN PeopleBaseItemMap on Peoples.Id = PeopleBaseItemMap.PeopleId 
        WHERE PeopleBaseItemMap.ItemId = ? 
        ORDER BY PeopleBaseItemMap.ListOrder 
        LIMIT 5
        """,
        (item_id,)
    )
    print("Cast:", cursor.fetchall())
except Exception as e:
    print("Cast Error:", e)

conn.close()
