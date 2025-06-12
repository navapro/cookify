import mysql.connector
from config import Config

def check_tables():
    try:
        # Connect to MySQL
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB
        )
        cursor = connection.cursor()

        # Get all tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("\n📋 Database Tables:")
        for table in tables:
            print(f"\nTable: {table[0]}")
            # Get table structure
            cursor.execute(f"DESCRIBE {table[0]}")
            columns = cursor.fetchall()
            for column in columns:
                print(f"  - {column[0]}: {column[1]}")

    except Exception as e:
        print("❌ Error checking tables:")
        print(str(e))
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    check_tables() 