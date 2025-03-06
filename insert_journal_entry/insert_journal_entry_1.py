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
    unique_suffix = datetime.now().strftime("%Y%m%d%H%M%S%f")  # Unique suffix based on current timestamp

    # Modify the name to include a unique suffix for guaranteed uniqueness
    unique_name = f"{data['name']}_{unique_suffix}"

    try:
        # Insert into the main JournalEntry table
        cursor.execute("""
            INSERT INTO JournalEntry (name, numberSeries, entryType, date, referenceNumber, userRemark, createdBy, modifiedBy, created, modified, submitted, cancelled)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (unique_name, data['numberSeries'], data['entryType'], data['date'], data['referenceNumber'], data['userRemark'], 'default_user', 'default_user', current_datetime, current_datetime, 1, 0))
        
        journal_entry_id = cursor.lastrowid  # Get the ID of the last inserted row

        # Insert associated accounts with unique names
        for index, account in enumerate(data['accounts'], start=1):
            account_unique_name = f"{unique_name}_Account_{index}"
            cursor.execute("""
                INSERT INTO JournalEntryAccount (name, account, debit, credit, idx, parent, parentSchemaName, parentFieldname)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                account_unique_name,       # unique name for account
                account['account'],        # account
                account['debit'],          # debit
                account['credit'],         # credit
                index,                     # idx
                unique_name,               # parent using journal entry's unique name
                'JournalEntry',            # parentSchemaName
                'accounts'                 # parentFieldname
            ))

        # Commit the changes
        conn.commit()
        print(f"Journal entry '{unique_name}' inserted successfully.")
        return unique_name  # Return the unique name to be used in ledger entries
    except Exception as e:
        print("An error occurred while inserting journal entry:", e)
        conn.rollback()  # Roll back changes on error
    finally:
        conn.close()

def insert_ledger_entries(journal_entry_id, journal_entry_name, accounts, db_path, user_id='default_user'):
    print(f"Inserting ledger entries for journal entry ID: {journal_entry_id}, Name: {journal_entry_name}")  # Log the start of the function
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    current_datetime = datetime.now().isoformat()
    
    try:
        for index, account in enumerate(accounts, start=1):
            ledger_entry_name = f"{journal_entry_name}_Ledger_{index}"  # Ensure uniqueness in ledger entry names
            print(f"Inserting ledger entry: {ledger_entry_name} for account: {account['account']}")  # Log each ledger entry
            cursor.execute("""
                INSERT INTO AccountingLedgerEntry (name, date, party, account, debit, credit, referenceType, referenceName, reverted, reverts, createdBy, modifiedBy, created, modified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ledger_entry_name,           # unique ledger entry name
                current_datetime,            # date
                account.get('party', ''),    # party
                account['account'],          # account
                account.get('debit', 0),     # debit
                account.get('credit', 0),    # credit
                'JournalEntry',              # referenceType
                journal_entry_id,            # referenceName
                False,                       # reverted
                '',                          # reverts
                user_id,                     # createdBy
                user_id,                     # modifiedBy
                current_datetime,            # created
                current_datetime             # modified
            ))
        conn.commit()
        print(f"Ledger entries for journal entry '{journal_entry_name}' inserted successfully.")
    except Exception as e:
        print("An error occurred while inserting ledger entries:", e)
        conn.rollback()
    finally:
        conn.close()

# Main function to execute the script
def main():
    json_data = load_json_data('journal_entry.json')  # Load JSON data from a file
    unique_journal_name = insert_journal_entry(json_data, 'C:/Users/ASURA/Desktop/Alpharithm/books/demo.db')  # Insert data into the database
    if unique_journal_name:
        insert_ledger_entries(1, unique_journal_name, json_data['accounts'], 'C:/Users/ASURA/Desktop/Alpharithm/books/demo.db')  # Insert ledger entries into the database

if __name__ == "__main__":
    main()
