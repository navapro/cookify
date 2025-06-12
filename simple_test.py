import mysql.connector

try:
    # Try to connect to MySQL
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Judy@2004",
        database="cookify"
    )
    print("✅ Successfully connected to MySQL!")
    connection.close()
except Exception as e:
    print("❌ Connection failed!")
    print("Error:", str(e)) 