
import sqlite3
import os

# Find the database in the same folder as this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "contacts.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("Database path:", DB_PATH)
print("Database connected successfully!")

# Check tables
cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
""")

tables = cursor.fetchall()
print("\nTables in database:")

for table in tables:
    print(table[0])

# Check saved contacts
try:
    cursor.execute("SELECT id, name, email, phone FROM contacts")
    contacts = cursor.fetchall()

    print("\nSaved Contacts:")

    for contact in contacts:
        print(contact)

    print("\nTotal contacts:", len(contacts))

except sqlite3.Error as error:
    print("Database error:", error)

conn.close()
