import mysql.connector
from config import Config

def test_relationships():
    try:
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB
        )
        cursor = connection.cursor(dictionary=True)

        print("\n🔍 Testing Relationships:")

        # Test User -> Recipe relationship through likes
        cursor.execute('''
            SELECT u.Name as User_Name, r.Name as Recipe_Name
            FROM Users u
            JOIN Recipe_Likes rl ON u.User_ID = rl.User_ID
            JOIN Recipes r ON rl.Recipe_ID = r.Recipe_ID
        ''')
        print("\nUser -> Recipe Likes:")
        for row in cursor.fetchall():
            print(f"  - {row['User_Name']} likes {row['Recipe_Name']}")

        # Test Recipe -> Ingredients relationship
        cursor.execute('''
            SELECT r.Name as Recipe_Name, i.Name as Ingredient_Name, ri.Quantity
            FROM Recipes r
            JOIN Recipe_Ingredients ri ON r.Recipe_ID = ri.Recipe_ID
            JOIN Ingredients i ON ri.Ingredient_ID = i.Ingredient_ID
        ''')
        print("\nRecipe -> Ingredients:")
        for row in cursor.fetchall():
            print(f"  - {row['Recipe_Name']} uses {row['Quantity']} of {row['Ingredient_Name']}")

        # Test User -> CookList relationship
        cursor.execute('''
            SELECT u.Name as User_Name, cl.Name as CookList_Name
            FROM Users u
            JOIN CookList cl ON u.User_ID = cl.User_ID
        ''')
        print("\nUser -> CookList:")
        for row in cursor.fetchall():
            print(f"  - {row['User_Name']} has cooklist: {row['CookList_Name']}")

    except Exception as e:
        print("❌ Error testing relationships:")
        print(str(e))
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    test_relationships() 