from extensions import db
from wsgi import app
from sqlalchemy import text

with app.app_context():
    try:
        # Query the users table
        result = db.session.execute(text("SELECT * FROM users"))
        users = result.fetchall()
        print("\nUsers in database:")
        for user in users:
            print(f"ID: {user[0]}, Username: {user[1]}, Email: {user[2]}")
    except Exception as e:
        print("❌ Database query failed!")
        print("Error:", str(e)) 