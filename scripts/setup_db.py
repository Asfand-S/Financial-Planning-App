import mysql.connector
import os
from dotenv import load_dotenv
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()

DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

def setup_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        print("[+] Connected to MySQL database.")

        # --- Create tables ---
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        print("[+] Created 'admins' table (if not exists).")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        print("[+] Created 'users' table (if not exists).")

        # --- Check if admin already exists ---
        cursor.execute("SELECT id FROM admins WHERE username = %s", (DEFAULT_ADMIN_USERNAME,))
        if cursor.fetchone():
            print("[!] Default admin already exists. Skipping insert.")
        else:
            # --- Hash password and insert admin ---
            hashed_pw = generate_password_hash(DEFAULT_ADMIN_PASSWORD)
            cursor.execute(
                "INSERT INTO admins (username, password_hash) VALUES (%s, %s)",
                (DEFAULT_ADMIN_USERNAME, hashed_pw)
            )
            conn.commit()
            print(f"[+] Default admin user '{DEFAULT_ADMIN_USERNAME}' created.")

    except mysql.connector.Error as err:
        print(f"[ERROR] MySQL Error: {err}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()
            print("[+] MySQL connection closed.")

if __name__ == "__main__":
    setup_db()