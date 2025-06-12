import mysql.connector
from config import Config
from datetime import date

def add_test_data():
    try:
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB
        )
        cursor = connection.cursor()

        # Add test user
        cursor.execute('''
            INSERT INTO Users (Name, Email, Password, Date_of_Birth, Cookify_Level)
            VALUES (%s, %s, %s, %s, %s)
        ''', ('Test User', 'test@example.com', 'password123', date(1990, 1, 1), 1))
        user_id = cursor.lastrowid

        # Add test recipe
        cursor.execute('''
            INSERT INTO Recipes (Name, Duration, Difficulty, Cuisine, Instructions)
            VALUES (%s, %s, %s, %s, %s)
        ''', ('Test Recipe', 30, 'Easy', 'Italian', 'Test instructions'))
        recipe_id = cursor.lastrowid

        # Add test ingredient
        cursor.execute('''
            INSERT INTO Ingredients (Name, Season, Price, Nutritional_Info)
            VALUES (%s, %s, %s, %s)
        ''', ('Test Ingredient', 'Summer', 5.99, 'Test nutritional info'))
        ingredient_id = cursor.lastrowid

        # Link recipe and ingredient
        cursor.execute('''
            INSERT INTO Recipe_Ingredients (Recipe_ID, Ingredient_ID, Quantity, Note)
            VALUES (%s, %s, %s, %s)
        ''', (recipe_id, ingredient_id, '2 cups', 'Test note'))

        # Create test cooklist
        cursor.execute('''
            INSERT INTO CookList (User_ID, Name, Description)
            VALUES (%s, %s, %s)
        ''', (user_id, 'Test CookList', 'Test description'))
        cooklist_id = cursor.lastrowid

        # Add recipe to cooklist
        cursor.execute('''
            INSERT INTO CookList_Recipes (CookList_ID, Recipe_ID)
            VALUES (%s, %s)
        ''', (cooklist_id, recipe_id))

        # Add a like
        cursor.execute('''
            INSERT INTO Recipe_Likes (User_ID, Recipe_ID)
            VALUES (%s, %s)
        ''', (user_id, recipe_id))

        connection.commit()
        print("✅ Test data added successfully!")

    except Exception as e:
        print("❌ Error adding test data:")
        print(str(e))
        connection.rollback()
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    add_test_data() 