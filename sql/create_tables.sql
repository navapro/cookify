-- Cookify Database Schema

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS cookify;
USE cookify;

-- Drop tables if they exist (for clean slate)
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS CookList_Likes;
DROP TABLE IF EXISTS Recipe_Likes;
DROP TABLE IF EXISTS CookList_Recipes;
DROP TABLE IF EXISTS Recipe_Ingredients;
DROP TABLE IF EXISTS User_Ingredients;
DROP TABLE IF EXISTS CookLists;
DROP TABLE IF EXISTS Ingredients;
DROP TABLE IF EXISTS Recipes;
DROP TABLE IF EXISTS User_Levels;
DROP TABLE IF EXISTS Users;
SET FOREIGN_KEY_CHECKS = 1;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS Users (
    User_ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    Email VARCHAR(255) UNIQUE NOT NULL,
    Password VARCHAR(255) NOT NULL,
    Date_of_Birth DATE,
    Profile_Image TEXT,
    Cookify_Level VARCHAR(50) DEFAULT 'Street Rat',
    Points INT DEFAULT 0
);

-- 2. Recipes Table
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
);

-- 3. Ingredients Table
CREATE TABLE IF NOT EXISTS Ingredients (
    Ingredient_ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL
);

-- 4. User_Ingredients Table
CREATE TABLE IF NOT EXISTS User_Ingredients (
    User_ID INT NOT NULL,
    Ingredient_ID INT NOT NULL,
    Quantity INT NOT NULL,
    PRIMARY KEY (User_ID, Ingredient_ID),
    FOREIGN KEY (User_ID) REFERENCES Users(User_ID) ON DELETE CASCADE,
    FOREIGN KEY (Ingredient_ID) REFERENCES Ingredients(Ingredient_ID) ON DELETE CASCADE
);

-- 5. Recipe_Ingredients Table
CREATE TABLE IF NOT EXISTS Recipe_Ingredients (
    Recipe_ID INT,
    Ingredient_ID INT,
    Quantity INT NOT NULL,
    Unit VARCHAR(255),
    PRIMARY KEY (Recipe_ID, Ingredient_ID),
    FOREIGN KEY (Recipe_ID) REFERENCES Recipes(Recipe_ID),
    FOREIGN KEY (Ingredient_ID) REFERENCES Ingredients(Ingredient_ID)
);

-- 6. CookLists Table
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

-- 7. CookList_Recipes Table
CREATE TABLE CookList_Recipes (
    CookList_ID INT NOT NULL,
    Recipe_ID INT NOT NULL,
    Added_At DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (CookList_ID, Recipe_ID),
    FOREIGN KEY (CookList_ID) REFERENCES CookLists(CookList_ID) ON DELETE CASCADE,
    FOREIGN KEY (Recipe_ID) REFERENCES Recipes(Recipe_ID) ON DELETE CASCADE
);

-- 8. Recipe_Likes Table
CREATE TABLE IF NOT EXISTS Recipe_Likes (
    User_ID INT,
    Recipe_ID INT,
    Liked_At DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (User_ID, Recipe_ID),
    FOREIGN KEY (User_ID) REFERENCES Users(User_ID),
    FOREIGN KEY (Recipe_ID) REFERENCES Recipes(Recipe_ID)
);

-- 9. CookList_Likes Table
CREATE TABLE IF NOT EXISTS CookList_Likes (
    User_ID INT,
    CookList_ID INT,
    Liked_At DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (User_ID, CookList_ID),
    FOREIGN KEY (User_ID) REFERENCES Users(User_ID),
    FOREIGN KEY (CookList_ID) REFERENCES CookLists(CookList_ID)
);

-- 10. User_Levels Table for leveling system
CREATE TABLE IF NOT EXISTS User_Levels (
    Level_Name VARCHAR(50) PRIMARY KEY,
    Min_Points INT NOT NULL,
    Image_Path VARCHAR(1024) NOT NULL
);

-- Insert level data
INSERT INTO User_Levels (Level_Name, Min_Points, Image_Path) VALUES
('Street Rat', 0, 'rat'),
('Dishwasher', 10, 'dishwasher'),
('Prep Cook', 25, 'prepcook'),
('Chef', 50, 'chef'),
('Sous Chef', 250, 'souschef'),
('Head Chef', 500, 'headchef'),
('Michelin Star Chef', 1000, 'starchef'),
('Remy the Rat', 10000, 'remy');

-- Drop existing triggers before creating new ones
DROP TRIGGER IF EXISTS After_Cooklist_Like;
DROP TRIGGER IF EXISTS After_Recipe_Like;
DROP TRIGGER IF EXISTS CreateLikedRecipes;
DROP TRIGGER IF EXISTS UniqueLikedCooklist;
DROP TRIGGER IF EXISTS AddToLikedRecipes;

-- ADVANCED FEATURE 2 & 3: Triggers for points and leveling system
DELIMITER //
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
END//

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
END//

-- BASIC FEATURE 5: Trigger for automatically generating 'Liked Recipes' cooklist
delimiter //
CREATE TRIGGER CreateLikedRecipes
AFTER INSERT ON Users
FOR EACH ROW
	BEGIN
    IF ((SELECT COUNT(*) FROM Cooklists WHERE User_ID = NEW.User_ID AND Name = 'Liked Recipes') = 0) THEN
		  INSERT INTO Cooklists (User_ID, Name, Description, Is_Public) VALUES (NEW.User_ID, 'Liked Recipes', 'All your liked recipes in one place!', TRUE);
    END IF;
	END; //

-- trigger for rejecting when a user attempts to create a 'Liked Recipes' cooklist on their own
delimiter //
CREATE TRIGGER UniqueLikedCooklist
BEFORE INSERT ON Cooklists
FOR EACH ROW
	BEGIN
		IF (NEW.Name = 'Liked Recipes' AND (SELECT COUNT(*) FROM Cooklists WHERE User_ID = NEW.User_ID AND Name = 'Liked Recipes') > 0) THEN
			SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Only one Liked Recipes cooklist can exist!';
		END IF;
	END; //

-- creating trigger for automatically adding liked recipes to Liked Recipes
delimiter //
CREATE TRIGGER AddToLikedRecipes
AFTER INSERT ON Recipe_Likes
FOR EACH ROW
	BEGIN
		IF ((SELECT COUNT(*) FROM Cooklists WHERE User_ID = NEW.User_ID AND Name = 'Liked Recipes') = 0) THEN
			INSERT INTO Cooklists (User_ID, Name, Description, Is_Public) VALUES (NEW.User_ID, 'Liked Recipes', 'All your liked recipes in one place!', TRUE);
		END IF;
		INSERT INTO Cooklist_Recipes VALUES ((SELECT Cooklist_ID FROM Cooklists WHERE User_ID = NEW.User_ID AND Name = 'Liked Recipes'), NEW.Recipe_ID, NEW.Liked_At);
	END; //

-- Performance Indexes (matching Python schema)
CREATE INDEX idx_ingredients_name ON Ingredients (Name);
CREATE INDEX idx_ri_recipe ON Recipe_Ingredients (Recipe_ID);
CREATE INDEX idx_ri_ingredient ON Recipe_Ingredients (Ingredient_ID);
CREATE INDEX idx_ui_user ON User_Ingredients (User_ID);
CREATE INDEX idx_ui_ingredient ON User_Ingredients (Ingredient_ID);
CREATE INDEX idx_recipe_cuisine ON Recipes (Cuisine);
CREATE INDEX idx_recipe_duration ON Recipes (Duration);
CREATE INDEX idx_added_at ON CookList_Recipes (CookList_ID, Added_At);
CREATE INDEX idx_recipes_name ON Recipes (Name);

-- Insert sample data for testing
INSERT INTO Users (Name, Email, Password, Date_of_Birth, Points, Cookify_Level) VALUES
('Alice Chef', 'alice@cookify.com', '$2b$10$hashedpassword1', '1995-03-15', 45, 'Chef'),
('Bob Novice', 'bob@cookify.com', '$2b$10$hashedpassword2', '1988-07-22', 8, 'Street Rat'),
('Carol Expert', 'carol@cookify.com', '$2b$10$hashedpassword3', '1992-11-03', 150, 'Sous Chef'),
('Dave Beginner', 'dave@cookify.com', '$2b$10$hashedpassword4', '1990-05-18', 2, 'Street Rat'),
('Emma Master', 'emma@cookify.com', '$2b$10$hashedpassword5', '1985-12-08', 350, 'Sous Chef');

-- Sample ingredients
INSERT INTO Ingredients (Name) VALUES
('Chicken Breast'),
('Ground Beef'),
('Salmon Fillet'),
('Eggs'),
('Tomatoes'),
('Onion'),
('Garlic'),
('Bell Peppers'),
('Spinach'),
('Carrots'),
('Basil'),
('Oregano'),
('Black Pepper'),
('Salt'),
('Paprika'),
('Pasta'),
('Rice'),
('Bread'),
('Parmesan Cheese'),
('Mozzarella'),
('Butter'),
('Olive Oil'),
('Lemon');

-- Sample recipes
INSERT INTO Recipes (User_ID, Name, Duration, Difficulty, Cuisine, Instructions, Image_URL) VALUES
(1, 'Classic Spaghetti Carbonara', 20, 'Medium', 'Italian', 'Cook pasta. Mix eggs and cheese. Combine with hot pasta and bacon. Serve immediately.', '/images/carbonara.jpg'),
(2, 'Simple Tomato Salad', 10, 'Easy', 'Mediterranean', 'Slice tomatoes. Add basil, olive oil, salt and pepper. Let sit for 10 minutes.', '/images/tomato-salad.jpg'),
(2, 'Garlic Butter Chicken', 25, 'Easy', 'American', 'Season chicken with salt and pepper. Saute with garlic and butter until golden.', '/images/garlic-chicken.jpg'),
(3, 'Beef Stir Fry', 15, 'Medium', 'Asian', 'Cut beef into strips. Stir fry with vegetables and soy sauce over high heat.', '/images/beef-stirfry.jpg'),
(5, 'Gordon Ramsay Beef Wellington', 180, 'Hard', 'British', 'Sear beef, wrap in pâté and pastry. Bake until golden. Advanced technique required.', '/images/beef-wellington.jpg');

-- Link recipes to ingredients
INSERT INTO Recipe_Ingredients (Recipe_ID, Ingredient_ID, Quantity, Unit) VALUES
-- Classic Spaghetti Carbonara (Recipe_ID = 1)
(1, 16, 400, 'grams'),     -- Pasta
(1, 4, 3, 'large'),        -- Eggs
(1, 19, 100, 'grams'),     -- Parmesan
(1, 13, 1, 'teaspoon'),    -- Black Pepper
(1, 14, 1, 'pinch'),       -- Salt

-- Simple Tomato Salad (Recipe_ID = 2)
(2, 5, 4, 'large'),        -- Tomatoes
(2, 11, 1, 'cup'),         -- Basil
(2, 22, 3, 'tablespoons'), -- Olive Oil
(2, 14, 1, 'pinch'),       -- Salt
(2, 13, 1, 'pinch'),       -- Black Pepper

-- Garlic Butter Chicken (Recipe_ID = 3)
(3, 1, 4, 'pieces'),       -- Chicken Breast
(3, 7, 4, 'cloves'),       -- Garlic
(3, 21, 2, 'tablespoons'), -- Butter
(3, 14, 1, 'teaspoon'),    -- Salt
(3, 13, 1, 'teaspoon'),    -- Black Pepper

-- Beef Stir Fry (Recipe_ID = 4)
(4, 2, 500, 'grams'),      -- Ground Beef
(4, 8, 2, 'medium'),       -- Bell Peppers
(4, 6, 1, 'large'),        -- Onion
(4, 7, 3, 'cloves'),       -- Garlic
(4, 22, 2, 'tablespoons'), -- Olive Oil

-- Beef Wellington (Recipe_ID = 5)
(5, 2, 1, 'kg'),           -- Ground Beef
(5, 7, 6, 'cloves'),       -- Garlic
(5, 21, 4, 'tablespoons'), -- Butter
(5, 14, 2, 'teaspoons'),   -- Salt
(5, 13, 1, 'teaspoon');    -- Black Pepper

-- Create sample cook lists
INSERT INTO CookLists (User_ID, Name, Description, Is_Public) VALUES
(1, 'Quick Weeknight Dinners', 'Easy recipes for busy weekdays under 30 minutes', TRUE),
(2, 'Beginner Friendly Recipes', 'Simple recipes to build confidence in the kitchen', TRUE),
(3, 'Italian Classics', 'Traditional Italian dishes I love to make', TRUE),
(4, 'Learning to Cook', 'My journey from instant noodles to real meals', FALSE),
(5, 'Master Chef Challenge', 'Advanced recipes for experienced cooks', TRUE);

-- Add recipes to cook lists
INSERT INTO CookList_Recipes (CookList_ID, Recipe_ID) VALUES
(1, 2), (1, 3), (1, 4),  -- Quick Weeknight Dinners
(2, 2), (2, 3),          -- Beginner Friendly
(3, 1), (3, 2),          -- Italian Classics
(4, 2), (4, 3),          -- Learning to Cook
(5, 1), (5, 5);          -- Master Chef Challenge

-- Add some user ingredients (pantry items)
INSERT INTO User_Ingredients (User_ID, Ingredient_ID, Quantity) VALUES
(1, 1, 2), (1, 5, 6), (1, 6, 3), (1, 7, 1), (1, 11, 1), (1, 16, 2), (1, 22, 500),  -- Alice's pantry
(2, 4, 12), (2, 6, 2), (2, 14, 1), (2, 17, 2),                                       -- Bob's basic pantry
(3, 1, 3), (3, 2, 2), (3, 3, 1), (3, 19, 200), (3, 21, 2), (3, 7, 2),              -- Carol's advanced pantry
(4, 16, 1), (4, 14, 1), (4, 13, 1),                                                  -- Dave's minimal pantry
(5, 2, 5), (5, 19, 500), (5, 11, 2), (5, 15, 1), (5, 22, 1000);                    -- Emma's gourmet pantry

-- Display success message and basic stats
SELECT 'Database setup complete!' as Status;
SELECT COUNT(*) as Total_Users FROM Users;
SELECT COUNT(*) as Total_Recipes FROM Recipes;
SELECT COUNT(*) as Total_Ingredients FROM Ingredients;
SELECT COUNT(*) as Total_CookLists FROM CookLists;
