import mysql.connector
from config import Config

def create_tables():
    try:
        # Connect to MySQL
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB
        )
        cursor = connection.cursor()

        # Create Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                User_ID INT AUTO_INCREMENT PRIMARY KEY,
                Name VARCHAR(255) NOT NULL,
                Email VARCHAR(255) UNIQUE NOT NULL,
                Password VARCHAR(255) NOT NULL,
                Date_of_Birth DATE,
                Profile_Image TEXT,
                Cookify_Level INT DEFAULT 1
            )
        ''')

        # Create Recipes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Recipes (
                Recipe_ID INT AUTO_INCREMENT PRIMARY KEY,
                Name VARCHAR(255) NOT NULL,
                Duration INT,
                Difficulty VARCHAR(50),
                Cuisine VARCHAR(100),
                Instructions TEXT,
                Recipe_Link VARCHAR(255)
            )
        ''')

        # Create Ingredients table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Ingredients (
                Ingredient_ID INT AUTO_INCREMENT PRIMARY KEY,
                Name VARCHAR(255) NOT NULL,
                Season VARCHAR(50),
                Price FLOAT,
                Nutritional_Info TEXT
            )
        ''')

        # Create Recipe_Ingredients table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Recipe_Ingredients (
                Recipe_ID INT,
                Ingredient_ID INT,
                Quantity VARCHAR(100),
                Note TEXT,
                PRIMARY KEY (Recipe_ID, Ingredient_ID),
                FOREIGN KEY (Recipe_ID) REFERENCES Recipes(Recipe_ID),
                FOREIGN KEY (Ingredient_ID) REFERENCES Ingredients(Ingredient_ID)
            )
        ''')

        # Create CookList table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS CookList (
                CookList_ID INT AUTO_INCREMENT PRIMARY KEY,
                User_ID INT,
                Name VARCHAR(255) NOT NULL,
                Description TEXT,
                Created_At DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (User_ID) REFERENCES Users(User_ID)
            )
        ''')

        # Create CookList_Recipes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS CookList_Recipes (
                CookList_ID INT,
                Recipe_ID INT,
                PRIMARY KEY (CookList_ID, Recipe_ID),
                FOREIGN KEY (CookList_ID) REFERENCES CookList(CookList_ID),
                FOREIGN KEY (Recipe_ID) REFERENCES Recipes(Recipe_ID)
            )
        ''')

        # Create Recipe_Likes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Recipe_Likes (
                User_ID INT,
                Recipe_ID INT,
                Liked_At DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (User_ID, Recipe_ID),
                FOREIGN KEY (User_ID) REFERENCES Users(User_ID),
                FOREIGN KEY (Recipe_ID) REFERENCES Recipes(Recipe_ID)
            )
        ''')

        # Create CookList_Likes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS CookList_Likes (
                User_ID INT,
                CookList_ID INT,
                Liked_At DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (User_ID, CookList_ID),
                FOREIGN KEY (User_ID) REFERENCES Users(User_ID),
                FOREIGN KEY (CookList_ID) REFERENCES CookList(CookList_ID)
            )
        ''')

        connection.commit()
        print("✅ All tables created successfully!")

    except Exception as e:
        print("❌ Error creating tables:")
        print(str(e))
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Database connection closed.")

if __name__ == "__main__":
    create_tables() 