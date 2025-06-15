from app import app, db
from sqlalchemy import text

def test_database_connection():
    with app.app_context():
        try:
            # Try to execute a simple query
            result = db.session.execute(text('SELECT 1'))
            print("✅ Database connection successful!")
            
            # Try to create a test table
            db.session.execute(text('''
                CREATE TABLE IF NOT EXISTS test_table (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    test_column VARCHAR(50)
                )
            '''))
            print("✅ Test table created successfully!")
            
            # Try to insert some test data
            db.session.execute(text('''
                INSERT INTO test_table (test_column) 
                VALUES ('test data')
            '''))
            print("✅ Test data inserted successfully!")
            
            # Try to query the test data
            result = db.session.execute(text('SELECT * FROM test_table'))
            print("✅ Test data queried successfully!")
            print("Data:", result.fetchall())
            
            # Clean up - drop the test table
            db.session.execute(text('DROP TABLE IF EXISTS test_table'))
            print("✅ Test table cleaned up successfully!")
            
            db.session.commit()
            print("\n✨ All database tests passed successfully!")
            
        except Exception as e:
            print("❌ Database test failed!")
            print("Error:", str(e))
            db.session.rollback()

if __name__ == "__main__":
    test_database_connection() 