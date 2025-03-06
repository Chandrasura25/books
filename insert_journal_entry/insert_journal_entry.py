import json
import sqlite3
from datetime import datetime

# Load JSON data from a file
def load_json_data(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)

# Insert data into the database
def insert_journal_entry(data, db_path):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get the current date and time
    current_datetime = datetime.now().isoformat()

    try:
        # Check if the journal entry name already exists
        cursor.execute("SELECT COUNT(*) FROM JournalEntry WHERE name = ?", (data['name'],))
        if cursor.fetchone()[0] > 0:
            raise ValueError(f"Journal entry with name '{data['name']}' already exists.")

        # Insert into the main JournalEntry table
        cursor.execute("""
            INSERT INTO JournalEntry (name, numberSeries, entryType, date, referenceNumber, userRemark, createdBy, modifiedBy, created, modified, submitted, cancelled)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (data['name'], data['numberSeries'], data['entryType'], data['date'], data['referenceNumber'], data['userRemark'], 'default_user', 'default_user', current_datetime, current_datetime, 1, 0))
        
        for index, account in enumerate(data['accounts'], start=1):
            # Ensure unique name for each JournalEntryAccount
            unique_name = f"{data['name']}_Account_Entry_{index}"
            cursor.execute("""
                INSERT INTO JournalEntryAccount (name, account, debit, credit, idx, parent, parentSchemaName, parentFieldname)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                unique_name,              # name
                account['account'],       # account
                account['debit'],         # debit
                account['credit'],        # credit
                index,                    # idx
                data['name'],             # parent
                'JournalEntry',           # parentSchemaName
                'accounts'                # parentFieldname
            ))

        # Commit the changes
        conn.commit() 
        print("Journal entry inserted successfully.", data['name'])
    except ValueError as ve:
        print("Validation error:", ve)
    except Exception as e: 
        print("An error occurred:", e)
        conn.rollback()  # Roll back changes on error
    finally:
        conn.close()

# Main function to execute the script
def main():
    json_data = load_json_data('journal_entry.json')  # Load JSON data from a file
    insert_journal_entry(json_data, 'C:/Users/ASURA/Desktop/Alpharithm/books/demo.db')  # Insert data into the database

if __name__ == "__main__":
    main()
