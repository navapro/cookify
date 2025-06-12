import mysql.connector
from config import Config  # keep this if you still use Config elsewhere

def reset_and_create_tables():
    # ---- Connection details -------------------------------------------------
    DB_CONFIG = {
        "host": "127.0.0.1",
        "user": "root",
        "password": "password",
        "database": "cookify",
        "charset": "utf8mb4",
        "use_unicode": True,
    }

    # ---- All table names (one place!) ---------------------------------------
    tables = [
        "CookList",
        "CookList_Likes",
        "CookList_Recipes",
        "Ingredients",
        "Recipe_Ingredients",
        "Recipe_Likes",
        "Recipes",
        "Users",
    ]

    connection = None
    cursor = None
    try:
        # ---------------------------------------------------------------------
        # Connect
        # ---------------------------------------------------------------------
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # ---------------------------------------------------------------------
        # DROP every existing table
        # ---------------------------------------------------------------------
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        for tbl in sorted(tables):          # alphabetical order
            cursor.execute(f"DROP TABLE IF EXISTS {tbl};")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        connection.commit()

        # ---------------------------------------------------------------------
        # Re-create schema
        # ---------------------------------------------------------------------

        # Users
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Users (
                User_ID INT AUTO_INCREMENT PRIMARY KEY,
                Name VARCHAR(255) NOT NULL,
                Email VARCHAR(255) UNIQUE NOT NULL,
                Password VARCHAR(255) NOT NULL,
                Date_of_Birth DATE,
                Profile_Image TEXT,
                Cookify_Level INT DEFAULT 1
            )
        """)

        # Recipes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Recipes (
                Recipe_ID INT AUTO_INCREMENT PRIMARY KEY,
                Name VARCHAR(255) NOT NULL,
                Duration INT,
                Difficulty VARCHAR(50),
                Cuisine VARCHAR(100),
                Instructions TEXT,
                Recipe_Link VARCHAR(255),
                Image_URL VARCHAR(255)
            )
        """)

        # Ingredients
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Ingredients (
                Ingredient_ID INT AUTO_INCREMENT PRIMARY KEY,
                Name VARCHAR(255) NOT NULL,
                Season VARCHAR(50),
                Price FLOAT,
                Nutritional_Info TEXT
            )
        """)

        # Recipe_Ingredients
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Recipe_Ingredients (
                Recipe_ID INT,
                Ingredient_ID INT,
                Quantity VARCHAR(100),
                Unit VARCHAR(255),
                Is_Optional VARCHAR(255),
                Note TEXT,
                PRIMARY KEY (Recipe_ID, Ingredient_ID),
                FOREIGN KEY (Recipe_ID) REFERENCES Recipes(Recipe_ID),
                FOREIGN KEY (Ingredient_ID) REFERENCES Ingredients(Ingredient_ID)
            )
        """)

        # CookList
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS CookList (
                CookList_ID INT AUTO_INCREMENT PRIMARY KEY,
                User_ID INT,
                Name VARCHAR(255) NOT NULL,
                Description TEXT,
                Created_At DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (User_ID) REFERENCES Users(User_ID)
            )
        """)

        # CookList_Recipes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS CookList_Recipes (
                CookList_ID INT,
                Recipe_ID INT,
                PRIMARY KEY (CookList_ID, Recipe_ID),
                FOREIGN KEY (CookList_ID) REFERENCES CookList(CookList_ID),
                FOREIGN KEY (Recipe_ID) REFERENCES Recipes(Recipe_ID)
            )
        """)

        # Recipe_Likes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Recipe_Likes (
                User_ID INT,
                Recipe_ID INT,
                Liked_At DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (User_ID, Recipe_ID),
                FOREIGN KEY (User_ID) REFERENCES Users(User_ID),
                FOREIGN KEY (Recipe_ID) REFERENCES Recipes(Recipe_ID)
            )
        """)

        # CookList_Likes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS CookList_Likes (
                User_ID INT,
                CookList_ID INT,
                Liked_At DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (User_ID, CookList_ID),
                FOREIGN KEY (User_ID) REFERENCES Users(User_ID),
                FOREIGN KEY (CookList_ID) REFERENCES CookList(CookList_ID)
            )
        """)

        connection.commit()
        print("✅ Database reset and tables recreated successfully!")

    except Exception as exc:
        print("❌ Error while resetting/creating tables:")
        print(exc)

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()
            print("Database connection closed.")

# ---------------------------------------------------------------------------
# Run directly
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    reset_and_create_tables()
