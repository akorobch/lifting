import os
import mysql.connector
from mysql.connector import errorcode

# ===============================
# 1. Load .env file manually
# ===============================
env_path = '.env'  # adjust path if needed
db_config = {}

with open(env_path, 'r') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        key, value = line.split('=', 1)
        # Remove quotes if present
        value = value.strip().strip("'").strip('"')
        db_config[key] = value

# Map to MySQL connector keys
db_params = {
    'user': db_config.get('DB_USERNAME'),
    'password': db_config.get('DB_PASSWORD'),
    'host': db_config.get('DB_HOST'),
    'database': db_config.get('DB_NAME')
}

# ===============================
# 2. Load SQL script
# ===============================
sql_file_path = 'C:\\Users\\akoro\\OneDrive\\Documents\\GitHub\\Lifting\\DB\\data.sql'
with open(sql_file_path, 'r', encoding='utf-8') as f:
    sql_script = f.read()

# ===============================
# 3. Connect and execute
# ===============================
try:
    conn = mysql.connector.connect(**db_params)
    cursor = conn.cursor()

    # Split the script by semicolons to execute statements one by one
    statements = [s.strip() for s in sql_script.split(';') if s.strip()]
    for stmt in statements:
        cursor.execute(stmt)

    conn.commit()
    print("SQL script executed successfully!")

except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Error: Invalid username or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Error: Database does not exist")
    else:
        print(f"MySQL Error: {err}")

finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals() and conn.is_connected():
        conn.close()
