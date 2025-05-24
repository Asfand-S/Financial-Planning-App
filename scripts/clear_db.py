from scripts.setup_db import *

def delete_all_tables():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        print("[+] Connected to MySQL database.")

        # --- Get list of all tables ---
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()

        if not tables:
            print("[*] No tables found. Database is already empty.")
        else:
            # Disable foreign key checks to allow dropping in any order
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

            for (table_name,) in tables:
                print(f"[-] Dropping table: {table_name}")
                cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`;")

            # Re-enable foreign key checks
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
            conn.commit()
            print("[+] All tables dropped successfully.")

    except mysql.connector.Error as err:
        print(f"[ERROR] MySQL Error: {err}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()
            print("[+] MySQL connection closed.")

if __name__ == '__main__':
    delete_all_tables()