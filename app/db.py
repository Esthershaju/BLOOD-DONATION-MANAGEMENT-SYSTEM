"""
Database Access Layer for Blood Donation Management System.
Encapsulates MySQL connections, queries, schema setup, and error handling.
"""
import os
import mysql.connector
from mysql.connector import Error
from app import config

def get_connection(host=None, user=None, password=None, port=None, database=None):
    """
    Creates and returns a MySQL database connection.
    Falls back to config values if parameters are not provided.
    """
    return mysql.connector.connect(
        host=host or config.DB_HOST,
        user=user or config.DB_USER,
        password=password if password is not None else config.DB_PASSWORD,
        port=port or config.DB_PORT,
        database=database if database is not None else config.DB_NAME,
        autocommit=False
    )

def test_connection(host=None, user=None, password=None, port=None, database=None):
    """
    Tests if a database connection can be established.
    Returns: (is_successful: bool, message: str)
    """
    try:
        conn = get_connection(host, user, password, port, database)
        if conn.is_connected():
            conn.close()
            return True, "Connected successfully to MySQL database!"
        return False, "Unable to establish connection."
    except Error as e:
        return False, str(e)

def execute_query(sql, params=None, commit=True):
    """
    Executes an INSERT, UPDATE, or DELETE query.
    Returns:
        dict: {'lastrowid': int, 'rowcount': int, 'success': bool, 'error': str}
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params or ())
        lastrowid = cursor.lastrowid
        rowcount = cursor.rowcount
        if commit:
            conn.commit()
        return {
            "success": True,
            "lastrowid": lastrowid,
            "rowcount": rowcount,
            "error": None
        }
    except Error as e:
        if conn:
            conn.rollback()
        return {
            "success": False,
            "lastrowid": None,
            "rowcount": 0,
            "error": str(e)
        }
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def fetch_all(sql, params=None):
    """
    Executes a SELECT query and returns all matching rows as dictionaries.
    Returns:
        list of dicts
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        records = cursor.fetchall()
        return records
    except Error as e:
        print(f"[DB Error in fetch_all]: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def fetch_one(sql, params=None):
    """
    Executes a SELECT query and returns the first row as a dictionary.
    Returns:
        dict or None
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        record = cursor.fetchone()
        return record
    except Error as e:
        print(f"[DB Error in fetch_one]: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def init_database(host=None, user=None, password=None, port=None, schema_file=None):
    """
    Executes schema.sql to initialize database and tables.
    Returns (success: bool, message: str)
    """
    host = host or config.DB_HOST
    user = user or config.DB_USER
    password = password if password is not None else config.DB_PASSWORD
    port = port or config.DB_PORT

    if not schema_file:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        schema_file = os.path.join(base_dir, "database", "schema.sql")

    if not os.path.exists(schema_file):
        return False, f"Schema file not found at: {schema_file}"

    conn = None
    cursor = None
    try:
        # First connect without specifying database to create it
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            port=port
        )
        cursor = conn.cursor()

        with open(schema_file, "r", encoding="utf-8") as f:
            sql_script = f.read()

        # Split commands by semicolon while respecting strings
        statements = sql_script.split(";")
        for stmt in statements:
            cleaned = stmt.strip()
            if cleaned:
                cursor.execute(cleaned)

        conn.commit()
        return True, "Database initialized and seeded successfully!"
    except Error as e:
        return False, f"MySQL Initialization Error: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
