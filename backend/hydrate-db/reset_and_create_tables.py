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
        "CookLists",
        "CookList_Likes",
        "CookList_Recipes",
        "Ingredients",
        "Recipe_Ingredients",
        "User_Ingredients",
        "Recipe_Likes",
        "Recipes",
        "Users",
        "User_Levels",
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
                Cookify_Level VARCHAR(50) DEFAULT 'Street Rat',
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

        # User_Ingredients
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS User_Ingredients (
                User_ID INT NOT NULL,
                Ingredient_ID INT NOT NULL,
                Quantity VARCHAR(100) NOT NULL,
                PRIMARY KEY (User_ID, Ingredient_ID),
                FOREIGN KEY (User_ID) REFERENCES Users(User_ID) ON DELETE CASCADE,
                FOREIGN KEY (Ingredient_ID) REFERENCES Ingredients(Ingredient_ID) ON DELETE CASCADE
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
      
        # advanced feature 2 + 3: drop triggers beforehand
        cursor.execute("DROP TRIGGER IF EXISTS After_Cooklist_Like;")
        cursor.execute("DROP TRIGGER IF EXISTS After_Recipe_Like;")
        # cursor.execute("DROP TRIGGER IF EXISTS Points_Update;")

        # ADVANCED FEATURE #3
        # NOTE: IF MYSQL SUPPORTED ASSERTIONS, WE WOULD IMPLEMENT FEATURE 3 WITH AN ASSERTION LIKE THIS:
        # CREATE ASSERTION CheckCooklistEditors
        # CHECK (
        # NOT EXISTS (
        #     SELECT * FROM CookList_Recipes cr
        #     WHERE NOT EXISTS (
        #       SELECT * FROM Cooklist_Editors ce
        #       WHERE ce.CookList_ID = cr.CookList_ID
        #       AND ce.User_ID = cr.Added_By
        #     )
        # )
        # );

        # TRIGGERS
        # Advanced feature 2: trigger for levelling up
        # when they plan a cooklist/add a recipe/make a recipe/other ppl like their recipes → 
        # all contribute to increasing the user’s points via a trigger → 
        # when they reach a certain threshold of points, it’ll trigger them to level up!
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS User_Levels (
                Level_Name VARCHAR(50) PRIMARY KEY,
                Min_Points INT NOT NULL,
                Image_Path varchar(1024) NOT NULL
            )
        """) # this represents the levels where users level up

        cursor.execute("""
            INSERT INTO User_Levels (Level_Name, Min_Points, Image_Path) VALUES
            ('Street Rat', 0, 'rat'),
            ('Dishwasher', 10, 'dishwasher'),
            ('Prep Cook', 25, 'prepcook'),
            ('Chef', 100, 'chef'),
            ('Sous Chef', 250, 'souschef'),
            ('Head Chef', 500, 'headchef'),
            ('Michelin Star Chef', 1000, 'starchef'),
            ('Remy the Rat', 10000, 'remy')
        """)

        # Trigger for when a user likes a cooklist
        cursor.execute("""
            CREATE TRIGGER After_Cooklist_Like
            AFTER INSERT ON CookList_Likes
            FOR EACH ROW
            BEGIN
                DECLARE cooklist_owner INT;
                DECLARE new_level VARCHAR(50);
                DECLARE new_image_path VARCHAR(1024);
                DECLARE updated_points INT;
                
                IF @TRIGGER_DISABLED IS NULL THEN
                    -- Find the cooklist owner
                    SELECT User_ID INTO cooklist_owner
                    FROM CookLists 
                    WHERE CookList_ID = NEW.CookList_ID;
                    
                    -- Calculate new points
                    SET updated_points = (SELECT Points + 1 FROM Users WHERE User_ID = cooklist_owner);
                    
                    -- Find appropriate level for new points
                    SELECT Level_Name, Image_Path 
                    INTO new_level, new_image_path
                    FROM User_Levels
                    WHERE Min_Points <= updated_points
                    ORDER BY Min_Points DESC
                    LIMIT 1;
                    
                    -- Update both points and level at once
                    UPDATE Users 
                    SET Points = updated_points,
                        Cookify_Level = new_level,
                        Profile_Image = new_image_path
                    WHERE User_ID = cooklist_owner;
                END IF;
            END
        """)

        # Trigger for when a user likes a recipe
        cursor.execute("""
            CREATE TRIGGER After_Recipe_Like
            AFTER INSERT ON Recipe_Likes
            FOR EACH ROW
            BEGIN
                DECLARE recipe_owner INT;
                DECLARE new_level VARCHAR(50);
                DECLARE new_image_path VARCHAR(1024);
                DECLARE updated_points INT;
                
                IF @TRIGGER_DISABLED IS NULL THEN
                    -- Find the recipe owner
                    SELECT User_ID INTO recipe_owner 
                    FROM Recipes 
                    WHERE Recipe_ID = NEW.Recipe_ID;
                    
                    -- Calculate new points
                    SET updated_points = (SELECT Points + 1 FROM Users WHERE User_ID = recipe_owner);
                    
                    -- Find appropriate level for new points
                    SELECT Level_Name, Image_Path 
                    INTO new_level, new_image_path
                    FROM User_Levels
                    WHERE Min_Points <= updated_points
                    ORDER BY Min_Points DESC
                    LIMIT 1;
                    
                    -- Update both points and level at once
                    UPDATE Users 
                    SET Points = updated_points,
                        Cookify_Level = new_level,
                        Profile_Image = new_image_path
                    WHERE User_ID = recipe_owner;
                END IF;
            END
        """)
        
        # ──────────────── Indexes ────────────────
        # speed up ingredient name lookups
        cursor.execute("CREATE INDEX idx_ingredients_name ON Ingredients (Name);")
        
        # speed up joins/filtering on Recipe_Ingredients
        cursor.execute("CREATE INDEX idx_ri_recipe ON Recipe_Ingredients (Recipe_ID);")
        cursor.execute("CREATE INDEX idx_ri_ingredient ON Recipe_Ingredients (Ingredient_ID);")

        # speed up joins/filtering on User_Ingredients
        cursor.execute("CREATE INDEX idx_ui_user ON User_Ingredients (User_ID);")
        cursor.execute("CREATE INDEX idx_ui_ingredient ON User_Ingredients (Ingredient_ID);")

        # for basic feature 2
        # speeds up filtering for recipes
        cursor.execute("CREATE INDEX idx_recipe_cuisine ON Recipes (Cuisine);")
        cursor.execute("CREATE INDEX idx_recipe_duration ON Recipes (Duration);")
        
        # for basic feature 3
        # speeds up ordering by date added
        cursor.execute("CREATE INDEX idx_added_at ON CookList_Recipes (CookList_ID, Added_At);")
        # speeds up ordering by recipe name/name lookups in general
        cursor.execute("CREATE INDEX idx_recipes_name ON Recipes (Name);")

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
                                INSERT INTO Cooklist_Recipes (CookList_ID, Recipe_ID, Added_At)
                                VALUES (
                                    (SELECT Cooklist_ID FROM Cooklists WHERE User_ID = NEW.User_ID AND Name = 'Liked Recipes'),
                                    NEW.Recipe_ID,
                                    NEW.Liked_At
                                );
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
