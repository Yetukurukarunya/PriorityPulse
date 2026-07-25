import sys

def test_connection():
    print("Testing MySQL Connection...")
    print("=" * 50)
    
    # Try different MySQL connectors
    mysql_connector = None
    connector_name = None
    
    # Try mysql.connector first
    try:
        import mysql.connector
        mysql_connector = mysql.connector
        connector_name = "mysql.connector"
        print(f"✓ Using {connector_name}")
    except ImportError:
        pass
    
    # Try pymysql as fallback
    if mysql_connector is None:
        try:
            import pymysql
            mysql_connector = pymysql
            connector_name = "pymysql"
            print(f"✓ Using {connector_name}")
        except ImportError:
            pass
    
    if mysql_connector is None:
        print("\n❌ No MySQL connector found!")
        print("\nPlease install one of these:")
        print("  pip install mysql-connector-python")
        print("  OR")
        print("  pip install pymysql")
        return False
    
    # Your MySQL credentials - UPDATE THESE
    config = {
        'host': 'localhost',
        'user': 'root',        # Change this to your MySQL username
        'password': 'karunya599@',        # Change this to your MySQL password
        'database': 'prioritypulse_db'
    }
    
    print(f"\nAttempting to connect to MySQL...")
    print(f"Host: {config['host']}")
    print(f"User: {config['user']}")
    print(f"Database: {config['database']}")
    print()
    
    try:
        # Attempt connection
        conn = mysql_connector.connect(**config)
        print("✓ Connected to MySQL successfully!")
        
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        db_exists = False
        for db in databases:
            if db[0] == config['database']:
                db_exists = True
                break
        
        if db_exists:
            print(f"✓ Database '{config['database']}' exists")
            
            # Switch to the database
            cursor.execute(f"USE {config['database']}")
            
            # Check tables
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            if tables:
                print(f"\n✓ Tables in database:")
                for table in tables:
                    print(f"  - {table[0]}")
                
                # Check users table
                try:
                    cursor.execute("SELECT COUNT(*) FROM users")
                    user_count = cursor.fetchone()[0]
                    print(f"\n✓ Users in database: {user_count}")
                except:
                    print("\n⚠ Users table not found or empty")
                
                # Check complaints table
                try:
                    cursor.execute("SELECT COUNT(*) FROM complaints")
                    complaint_count = cursor.fetchone()[0]
                    print(f"✓ Complaints in database: {complaint_count}")
                except:
                    print("⚠ Complaints table not found or empty")
                
            else:
                print("\n⚠ No tables found in the database")
                print("You need to create the tables using your SQL script.")
        else:
            print(f"❌ Database '{config['database']}' does not exist")
            print("\nCreate it using MySQL:")
            print(f"CREATE DATABASE {config['database']};")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 50)
        print("✅ Database connection test completed!")
        return True
        
    except Exception as err:
        print(f"\n❌ Connection failed!")
        print(f"Error: {err}")
        
        # Provide helpful error messages
        error_msg = str(err).lower()
        if "access denied" in error_msg or "1045" in error_msg:
            print("\n🔧 Troubleshooting:")
            print("  - Incorrect username or password")
            print("  - Check your MySQL credentials")
            print("  - Default XAMPP: username='root', password=''")
            print("  - Default MAMP: username='root', password='root'")
            print("\n  Update the config in this file:")
            print("    config = {")
            print("        'host': 'localhost',")
            print("        'user': 'root',        # ← CHANGE THIS")
            print("        'password': '',        # ← CHANGE THIS")
            print("        'database': 'prioritypulse_db'")
            print("    }")
        elif "unknown database" in error_msg or "1049" in error_msg:
            print("\n🔧 Troubleshooting:")
            print(f"  - Database '{config['database']}' does not exist")
            print("  - Create it using: CREATE DATABASE prioritypulse_db;")
        elif "can't connect" in error_msg or "2003" in error_msg:
            print("\n🔧 Troubleshooting:")
            print("  - MySQL server is not running")
            print("  - Start MySQL service:")
            print("    Windows: net start MySQL")
            print("    Or via XAMPP/WAMP control panel")
        else:
            print("\n🔧 Check:")
            print("  1. Is MySQL installed?")
            print("  2. Is MySQL service running?")
            print("  3. Are credentials correct?")
        
        return False

if __name__ == "__main__":
    test_connection()