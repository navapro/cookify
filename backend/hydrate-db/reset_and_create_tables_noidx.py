import mysql.connector
import sys
from pathlib import Path

# Add parent directory to path to import config.py
sys.path.append(str(Path(__file__).parent.parent))
from config import Config

def reset_and_create_tables():
    config = Config()

    DB_CONFIG = {
        "host": config.MYSQL_HOST,
        "user": config.MYSQL_USER,
        "password": config.MYSQL_PASSWORD,
        "database": config.MYSQL_DB,
        "charset": "utf8mb4",
        "use_unicode": True,
        "port": config.MYSQL_PORT
    }

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
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        for tbl in sorted(tables):  # alphabetical order
            cursor.execute(f"DROP TABLE IF EXISTS {tbl};")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        connection.commit()

        # Users
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Users (
                User_ID INT AUTO_INCREMENT PRIMARY KEY,
                Name VARCHAR(255) NOT NULL,
                Email VARCHAR(255) UNIQUE NOT NULL,
                Password VARCHAR(255) NOT NULL,
                Date_of_Birth DATE,
                Profile_Image TEXT,
                Cookify_Level INT DEFAULT 0,
                Points INT DEFAULT 0
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
                Image_URL VARCHAR(255),
                User_ID INT,
                FOREIGN KEY (User_ID) REFERENCES Users(User_ID)
            )
        """)

        # Ingredients
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Ingredients (
                Ingredient_ID INT AUTO_INCREMENT PRIMARY KEY,
                Name VARCHAR(255) NOT NULL
            )
        """)

        # Recipe_Ingredients
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Recipe_Ingredients (
                Recipe_ID INT,
                Ingredient_ID INT,
                Quantity VARCHAR(100),
                Unit VARCHAR(255),
                PRIMARY KEY (Recipe_ID, Ingredient_ID),
                FOREIGN KEY (Recipe_ID) REFERENCES Recipes(Recipe_ID),
                FOREIGN KEY (Ingredient_ID) REFERENCES Ingredients(Ingredient_ID)
            )
        """)

        # CookLists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS CookLists (
                CookList_ID INT AUTO_INCREMENT PRIMARY KEY,
                User_ID INT NOT NULL,
                Name VARCHAR(100) NOT NULL,
                Description TEXT,
                Is_Public BOOLEAN DEFAULT TRUE,
                Created_At DATETIME DEFAULT CURRENT_TIMESTAMP,
                Updated_At DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (User_ID) REFERENCES Users(User_ID) ON DELETE CASCADE
            );
        """)

        # CookList_Recipes
        cursor.execute("""
            CREATE TABLE CookList_Recipes (
            CookList_ID INT NOT NULL,
            Recipe_ID INT NOT NULL,
            Added_At DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (CookList_ID, Recipe_ID),
            FOREIGN KEY (CookList_ID) REFERENCES CookLists(CookList_ID) ON DELETE CASCADE,
            FOREIGN KEY (Recipe_ID) REFERENCES Recipes(Recipe_ID) ON DELETE CASCADE
            );
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
                FOREIGN KEY (CookList_ID) REFERENCES CookLists(CookList_ID)
            )
        """)

        # for basic feature 5
        # dropping all triggers
        cursor.execute("DROP TRIGGER IF EXISTS CreateLikedRecipes;")
        cursor.execute("DROP TRIGGER IF EXISTS UniqueLikedCooklist;")
        cursor.execute("DROP TRIGGER IF EXISTS AddToLikedRecipes;")

        # trigger for automatically generating 'Liked Recipes' cooklist
        cursor.execute("""delimiter //
                        CREATE TRIGGER CreateLikedRecipes
                        AFTER INSERT ON Users
                        FOR EACH ROW
                            BEGIN
                            IF ((SELECT COUNT(*) FROM Cooklists WHERE User_ID = NEW.User_ID AND Name = 'Liked Recipes') = 0) THEN
                                INSERT INTO Cooklists (User_ID, Name, Description, Is_Public) VALUES (NEW.User_ID, 'Liked Recipes', 'All your liked recipes in one place!', TRUE);
                            END IF;
                            END; //""")
        
        # trigger for rejecting when a user attempts to create a 'Liked Recipes' cooklist on their own
        cursor.execute("""delimiter //
                        CREATE TRIGGER UniqueLikedCooklist
                        BEFORE INSERT ON Cooklists
                        FOR EACH ROW
                            BEGIN
                                IF (NEW.Name = 'Liked Recipes' AND (SELECT COUNT(*) FROM Cooklists WHERE User_ID = NEW.User_ID AND Name = 'Liked Recipes') > 0) THEN
                                    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Only one Liked Recipes cooklist can exist!';
                                END IF;
                            END; //""")

        # creating trigger for automatically adding liked recipes to Liked Recipes
        cursor.execute("""delimiter //
                        CREATE TRIGGER AddToLikedRecipes
                        AFTER INSERT ON Recipe_Likes
                        FOR EACH ROW
                            BEGIN
                                IF ((SELECT COUNT(*) FROM Cooklists WHERE User_ID = NEW.User_ID AND Name = 'Liked Recipes') = 0) THEN
                                    INSERT INTO Cooklists (User_ID, Name, Description, Is_Public) VALUES (NEW.User_ID, 'Liked Recipes', 'All your liked recipes in one place!', TRUE);
                                END IF;
                                INSERT INTO Cooklist_Recipes VALUES ((SELECT Cooklist_ID FROM Cooklists WHERE User_ID = NEW.User_ID AND Name = 'Liked Recipes'), NEW.Recipe_ID, NEW.Liked_At);
                            END; //""")
        
        connection.commit()
        print("Database reset and tables recreated successfully!")

    except Exception as exc:
        print("Error while resetting/creating tables:")
        print(exc)

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()
            print("Database connection closed.")

if __name__ == "__main__":
    reset_and_create_tables()
