"""
One-click CLI utility to set up and verify the MySQL Database.
Usage:
    python setup_db.py
"""
import sys
import getpass
from app import config, db

def main():
    print("=" * 60)
    print("  BLOOD DONATION MANAGEMENT SYSTEM - DATABASE SETUP")
    print("=" * 60)
    
    host = input(f"MySQL Host [{config.DB_HOST}]: ").strip() or config.DB_HOST
    port_input = input(f"MySQL Port [{config.DB_PORT}]: ").strip()
    port = int(port_input) if port_input else config.DB_PORT
    user = input(f"MySQL User [{config.DB_USER}]: ").strip() or config.DB_USER
    password = getpass.getpass(f"MySQL Password for '{user}' (press Enter if empty): ")

    print("\nConnecting to MySQL and executing schema.sql...")
    success, msg = db.init_database(host=host, user=user, password=password, port=port)
    
    if success:
        print(f"\n[SUCCESS] {msg}")
        print("\nTesting database query...")
        # Update config in memory for test
        config.DB_HOST = host
        config.DB_PORT = port
        config.DB_USER = user
        config.DB_PASSWORD = password
        
        donors = db.fetch_all("SELECT COUNT(*) as count FROM donors;")
        hospitals = db.fetch_all("SELECT COUNT(*) as count FROM hospitals;")
        requests = db.fetch_all("SELECT COUNT(*) as count FROM blood_requests;")
        inventory = db.fetch_all("SELECT COUNT(*) as count FROM blood_inventory;")
        
        print(f"  - Donors loaded:    {donors[0]['count'] if donors else 0}")
        print(f"  - Hospitals loaded: {hospitals[0]['count'] if hospitals else 0}")
        print(f"  - Requests loaded:  {requests[0]['count'] if requests else 0}")
        print(f"  - Blood Groups:     {inventory[0]['count'] if inventory else 0}")
        
        # Save working configuration to .env for Streamlit application
        try:
            with open(".env", "w", encoding="utf-8") as f:
                f.write(f"DB_HOST={host}\n")
                f.write(f"DB_PORT={port}\n")
                f.write(f"DB_USER={user}\n")
                f.write(f"DB_PASSWORD={password}\n")
                f.write(f"DB_NAME=blood_donation_db\n")
            print("  - Configuration saved to .env file for Streamlit auto-connect.")
        except Exception as e:
            print(f"  - Note: Could not save .env: {e}")

        print("\nDatabase is ready! You can now run the application:")
        print("  streamlit run app/main.py")
    else:
        print(f"\n[ERROR] {msg}")
        print("\nPlease ensure MySQL is running and your password is correct.")
        sys.exit(1)

if __name__ == "__main__":
    main()
