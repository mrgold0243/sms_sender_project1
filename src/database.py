import sqlite3

def create_connection(db_file):
    """Create a database connection to the SQLite database."""
    conn = sqlite3.connect(db_file)
    return conn

def create_table():
    """Create the subscribers table if it doesn't exist."""
    conn = create_connection('sms_sender.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            subscription_expiry TEXT NOT NULL
        );
    ''')
    conn.commit()
    conn.close()

def insert_subscriber(username, password, subscription_expiry):
    """Insert a new subscriber into the database."""
    conn = create_connection('sms_sender.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO subscribers (username, password, subscription_expiry) 
            VALUES (?, ?, ?);
        ''', (username, password, subscription_expiry))
        conn.commit()
        print(f"Subscriber '{username}' added successfully.")
    except sqlite3.IntegrityError:
        print(f"Error: The username '{username}' already exists.")
    finally:
        conn.close()

def load_subscriber(username):
    """Load subscriber data by username."""
    conn = create_connection('sms_sender.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT username, password, subscription_expiry FROM subscribers WHERE username = ?', (username,))
    user_data = cursor.fetchone()
    
    conn.close()
    return user_data

def list_subscribers():
    """List all subscribers in the database."""
    conn = create_connection('sms_sender.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT username, subscription_expiry FROM subscribers;')
    all_subscribers = cursor.fetchall()
    
    conn.close()
    return all_subscribers

if __name__ == "__main__":
    create_table()  # Ensure the table is created on script execution

    # Insert the specific subscriber details
    username = "Mrgold"
    password = "Johnnygill$0243"
    subscription_expiry = "9999-12-31"  # Set to a far future date for lifetime

    insert_subscriber(username, password, subscription_expiry)
    
    # List all subscribers
    subscribers = list_subscribers()
    print("Current Subscribers:")
    for subscriber in subscribers:
        print(subscriber)
