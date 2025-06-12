-- Cookify Database Schema - Complete Implementation
-- Replace your existing schema.sql with this file

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS cookify_db;
USE cookify_db;

-- Drop tables if they exist (for clean slate)
DROP TABLE IF EXISTS User_Activities;
DROP TABLE IF EXISTS CookList_Likes;
DROP TABLE IF EXISTS Recipe_Likes;
DROP TABLE IF EXISTS CookList_Recipes;
DROP TABLE IF EXISTS Recipe_Ingredients;
DROP TABLE IF EXISTS CookLists;
DROP TABLE IF EXISTS Ingredients;
DROP TABLE IF EXISTS Recipes;
DROP TABLE IF EXISTS Users;

-- 1. Users Table - The chefs in our app
CREATE TABLE Users (
  User_ID INT AUTO_INCREMENT PRIMARY KEY,
  Name VARCHAR(50) NOT NULL,
  Email VARCHAR(100) NOT NULL UNIQUE,
  Password VARCHAR(255) NOT NULL, -- For hashed passwords (bcrypt needs ~60 chars)
  Date_of_Birth DATE,
  Profile_Image VARCHAR(255), -- Store file path/URL
  Cookify_Level INT DEFAULT 0,
  Points INT DEFAULT 0,
  Created_At DATETIME DEFAULT CURRENT_TIMESTAMP,
  Updated_At DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 2. Recipes Table - The dishes in our cookbook
CREATE TABLE Recipes (
  Recipe_ID INT AUTO_INCREMENT PRIMARY KEY,
  Name VARCHAR(100) NOT NULL,
  Duration INT, -- Duration in minutes
  Difficulty ENUM('Easy', 'Medium', 'Hard'),
  Cuisine VARCHAR(50),
  Instructions TEXT,
  Recipe_Link VARCHAR(255),
  Image_URL VARCHAR(255),
  Servings INT DEFAULT 1,
  Created_At DATETIME DEFAULT CURRENT_TIMESTAMP,
  Updated_At DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 3. Ingredients Table - Our pantry
CREATE TABLE Ingredients (
  Ingredient_ID INT AUTO_INCREMENT PRIMARY KEY,
  Name VARCHAR(100) NOT NULL UNIQUE,
  Season VARCHAR(50),
  Price DECIMAL(8,2), -- Supports prices up to 999,999.99
  Nutritional_Info TEXT,
  Category VARCHAR(50), -- e.g., 'Protein', 'Vegetable', 'Spice'
  Created_At DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 4. Recipe-Ingredients Junction Table - What goes into each recipe
CREATE TABLE Recipe_Ingredients (
  Recipe_ID INT NOT NULL,
  Ingredient_ID INT NOT NULL,
  Quantity VARCHAR(50), -- e.g., "2 cups", "1 tablespoon"
  Unit VARCHAR(20),     -- e.g., "cups", "grams", "pieces"
  Is_Optional BOOLEAN DEFAULT FALSE,
  PRIMARY KEY (Recipe_ID, Ingredient_ID),
  FOREIGN KEY (Recipe_ID) REFERENCES Recipes(Recipe_ID) ON DELETE CASCADE,
  FOREIGN KEY (Ingredient_ID) REFERENCES Ingredients(Ingredient_ID)
);

-- 5. Cook Lists Table - User's recipe collections (like Spotify playlists)
CREATE TABLE CookLists (
  CookList_ID INT AUTO_INCREMENT PRIMARY KEY,
  User_ID INT NOT NULL,
  Name VARCHAR(100) NOT NULL,
  Description TEXT,
  Is_Public BOOLEAN DEFAULT TRUE,
  Created_At DATETIME DEFAULT CURRENT_TIMESTAMP,
  Updated_At DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (User_ID) REFERENCES Users(User_ID) ON DELETE CASCADE
);

-- 6. CookList-Recipes Junction Table - Which recipes are in each cook list
CREATE TABLE CookList_Recipes (
  CookList_ID INT NOT NULL,
  Recipe_ID INT NOT NULL,
  Added_At DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (CookList_ID, Recipe_ID),
  FOREIGN KEY (CookList_ID) REFERENCES CookLists(CookList_ID) ON DELETE CASCADE,
  FOREIGN KEY (Recipe_ID) REFERENCES Recipes(Recipe_ID) ON DELETE CASCADE
);

-- 7. Recipe Likes Table - Which recipes users have liked
CREATE TABLE Recipe_Likes (
  User_ID INT NOT NULL,
  Recipe_ID INT NOT NULL,
  Liked_At DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (User_ID, Recipe_ID),
  FOREIGN KEY (User_ID) REFERENCES Users(User_ID) ON DELETE CASCADE,
  FOREIGN KEY (Recipe_ID) REFERENCES Recipes(Recipe_ID) ON DELETE CASCADE
);

-- 8. CookList Likes Table - Which cook lists users have liked
CREATE TABLE CookList_Likes (
  User_ID INT NOT NULL,
  CookList_ID INT NOT NULL,
  Liked_At DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (User_ID, CookList_ID),
  FOREIGN KEY (User_ID) REFERENCES Users(User_ID) ON DELETE CASCADE,
  FOREIGN KEY (CookList_ID) REFERENCES CookLists(CookList_ID) ON DELETE CASCADE
);

-- 9. User Activity Table - Track actions for leveling system
CREATE TABLE User_Activities (
  Activity_ID INT AUTO_INCREMENT PRIMARY KEY,
  User_ID INT NOT NULL,
  Activity_Type ENUM('recipe_liked', 'recipe_cooked', 'cooklist_created', 'cooklist_shared'),
  Points_Earned INT DEFAULT 0,
  Activity_Date DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (User_ID) REFERENCES Users(User_ID) ON DELETE CASCADE
);

-- Performance Indexes for faster queries
CREATE INDEX idx_recipes_cuisine ON Recipes(Cuisine);
CREATE INDEX idx_recipes_difficulty ON Recipes(Difficulty);
CREATE INDEX idx_recipes_duration ON Recipes(Duration);
CREATE INDEX idx_ingredients_category ON Ingredients(Category);
CREATE INDEX idx_ingredients_season ON Ingredients(Season);
CREATE INDEX idx_users_points ON Users(Points);
CREATE INDEX idx_recipe_likes_recipe ON Recipe_Likes(Recipe_ID);
CREATE INDEX idx_cooklist_likes_cooklist ON CookList_Likes(CookList_ID);

-- Insert sample data for testing
-- Sample users with different levels
INSERT INTO Users (Name, Email, Password, Date_of_Birth, Points, Cookify_Level) VALUES
('Alice Chef', 'alice@cookify.com', '$2b$10$hashedpassword1', '1995-03-15', 45, 4),
('Bob Novice', 'bob@cookify.com', '$2b$10$hashedpassword2', '1988-07-22', 8, 2),
('Carol Expert', 'carol@cookify.com', '$2b$10$hashedpassword3', '1992-11-03', 150, 6),
('Dave Beginner', 'dave@cookify.com', '$2b$10$hashedpassword4', '1990-05-18', 2, 1),
('Emma Master', 'emma@cookify.com', '$2b$10$hashedpassword5', '1985-12-08', 350, 8);

-- Sample ingredients organized by category
INSERT INTO Ingredients (Name, Season, Price, Category) VALUES
-- Proteins
('Chicken Breast', 'All Year', 8.99, 'Protein'),
('Ground Beef', 'All Year', 6.50, 'Protein'),
('Salmon Fillet', 'All Year', 15.99, 'Protein'),
('Eggs', 'All Year', 4.25, 'Protein'),

-- Vegetables
('Tomatoes', 'Summer', 3.50, 'Vegetable'),
('Onion', 'All Year', 2.25, 'Vegetable'),
('Garlic', 'All Year', 1.50, 'Vegetable'),
('Bell Peppers', 'Summer', 4.99, 'Vegetable'),
('Spinach', 'Spring', 2.75, 'Vegetable'),
('Carrots', 'Fall', 1.99, 'Vegetable'),

-- Herbs & Spices
('Basil', 'Summer', 2.99, 'Herb'),
('Oregano', 'All Year', 3.50, 'Herb'),
('Black Pepper', 'All Year', 3.99, 'Spice'),
('Salt', 'All Year', 0.99, 'Seasoning'),
('Paprika', 'All Year', 4.50, 'Spice'),

-- Grains & Carbs
('Pasta', 'All Year', 1.99, 'Grain'),
('Rice', 'All Year', 3.25, 'Grain'),
('Bread', 'All Year', 2.50, 'Grain'),

-- Dairy
('Parmesan Cheese', 'All Year', 8.50, 'Dairy'),
('Mozzarella', 'All Year', 5.99, 'Dairy'),
('Butter', 'All Year', 4.75, 'Dairy'),

-- Others
('Olive Oil', 'All Year', 12.99, 'Oil'),
('Lemon', 'All Year', 0.75, 'Citrus');

-- Sample recipes with varying difficulties
INSERT INTO Recipes (Name, Duration, Difficulty, Cuisine, Instructions, Servings, Image_URL) VALUES
('Classic Spaghetti Carbonara', 20, 'Medium', 'Italian', 'Cook pasta. Mix eggs and cheese. Combine with hot pasta and bacon. Serve immediately.', 4, '/images/carbonara.jpg'),
('Simple Tomato Salad', 10, 'Easy', 'Mediterranean', 'Slice tomatoes. Add basil, olive oil, salt and pepper. Let sit for 10 minutes.', 2, '/images/tomato-salad.jpg'),
('Garlic Butter Chicken', 25, 'Easy', 'American', 'Season chicken with salt and pepper. Sauté with garlic and butter until golden.', 3, '/images/garlic-chicken.jpg'),
('Beef Stir Fry', 15, 'Medium', 'Asian', 'Cut beef into strips. Stir fry with vegetables and soy sauce over high heat.', 4, '/images/beef-stirfry.jpg'),
('Gordon Ramsay Beef Wellington', 180, 'Hard', 'British', 'Sear beef, wrap in pâté and pastry. Bake until golden. Advanced technique required.', 6, '/images/beef-wellington.jpg');

-- Link recipes to ingredients (the crucial many-to-many relationships)
INSERT INTO Recipe_Ingredients (Recipe_ID, Ingredient_ID, Quantity, Unit) VALUES
-- Classic Spaghetti Carbonara (Recipe_ID = 1)
(1, 16, '400', 'grams'),     -- Pasta
(1, 4, '3', 'large'),        -- Eggs
(1, 19, '100', 'grams'),     -- Parmesan
(1, 13, '1', 'teaspoon'),    -- Black Pepper
(1, 14, '1', 'pinch'),       -- Salt

-- Simple Tomato Salad (Recipe_ID = 2)
(2, 5, '4', 'large'),        -- Tomatoes
(2, 11, '1/4', 'cup'),       -- Basil
(2, 22, '3', 'tablespoons'), -- Olive Oil
(2, 14, '1', 'pinch'),       -- Salt
(2, 13, '1', 'pinch'),       -- Black Pepper

-- Garlic Butter Chicken (Recipe_ID = 3)
(3, 1, '4', 'pieces'),       -- Chicken Breast
(3, 7, '4', 'cloves'),       -- Garlic
(3, 21, '2', 'tablespoons'), -- Butter
(3, 14, '1', 'teaspoon'),    -- Salt
(3, 13, '1/2', 'teaspoon'),  -- Black Pepper

-- Beef Stir Fry (Recipe_ID = 4)
(4, 2, '500', 'grams'),      -- Ground Beef
(4, 8, '2', 'medium'),       -- Bell Peppers
(4, 6, '1', 'large'),        -- Onion
(4, 7, '3', 'cloves'),       -- Garlic
(4, 22, '2', 'tablespoons'), -- Olive Oil

-- Beef Wellington (Recipe_ID = 5) - Gordon Ramsay level!
(5, 2, '1', 'kg'),           -- Ground Beef (substitute for beef tenderloin)
(5, 7, '6', 'cloves'),       -- Garlic
(5, 21, '4', 'tablespoons'), -- Butter
(5, 14, '2', 'teaspoons'),   -- Salt
(5, 13, '1', 'teaspoon');    -- Black Pepper

-- Create sample cook lists
INSERT INTO CookLists (User_ID, Name, Description, Is_Public) VALUES
(1, 'Quick Weeknight Dinners', 'Easy recipes for busy weekdays under 30 minutes', TRUE),
(2, 'Beginner Friendly Recipes', 'Simple recipes to build confidence in the kitchen', TRUE),
(3, 'Italian Classics', 'Traditional Italian dishes I love to make', TRUE),
(4, 'Learning to Cook', 'My journey from instant noodles to real meals', FALSE),
(5, 'Master Chef Challenge', 'Advanced recipes for experienced cooks', TRUE);

-- Add recipes to cook lists
INSERT INTO CookList_Recipes (CookList_ID, Recipe_ID) VALUES
-- Quick Weeknight Dinners
(1, 2), -- Tomato Salad
(1, 3), -- Garlic Chicken
(1, 4), -- Beef Stir Fry

-- Beginner Friendly
(2, 2), -- Tomato Salad
(2, 3), -- Garlic Chicken

-- Italian Classics
(3, 1), -- Carbonara
(3, 2), -- Tomato Salad

-- Learning to Cook
(4, 2), -- Tomato Salad
(4, 3), -- Garlic Chicken

-- Master Chef Challenge
(5, 1), -- Carbonara
(5, 5); -- Beef Wellington

-- Add some likes to make the data realistic
INSERT INTO Recipe_Likes (User_ID, Recipe_ID) VALUES
(1, 2), -- Alice likes Tomato Salad
(1, 4), -- Alice likes Beef Stir Fry
(2, 1), -- Bob likes Carbonara
(2, 3), -- Bob likes Garlic Chicken
(3, 1), -- Carol likes Carbonara
(3, 5), -- Carol likes Beef Wellington
(4, 2), -- Dave likes Tomato Salad
(4, 3), -- Dave likes Garlic Chicken
(5, 5); -- Emma likes Beef Wellington

INSERT INTO CookList_Likes (User_ID, CookList_ID) VALUES
(2, 1), -- Bob likes Quick Weeknight Dinners
(4, 2), -- Dave likes Beginner Friendly
(1, 3), -- Alice likes Italian Classics
(3, 5), -- Carol likes Master Chef Challenge
(2, 4); -- Bob likes Learning to Cook

-- Add some activity tracking for the leveling system
INSERT INTO User_Activities (User_ID, Activity_Type, Points_Earned) VALUES
(1, 'recipe_liked', 5),
(1, 'cooklist_created', 10),
(2, 'recipe_liked', 5),
(2, 'recipe_cooked', 15),
(3, 'cooklist_created', 10),
(3, 'recipe_cooked', 20),
(4, 'recipe_liked', 5),
(5, 'recipe_cooked', 25);

-- Display success message and basic stats
SELECT 'Database setup complete!' as Status;
SELECT COUNT(*) as Total_Users FROM Users;
SELECT COUNT(*) as Total_Recipes FROM Recipes;
SELECT COUNT(*) as Total_Ingredients FROM Ingredients;
SELECT COUNT(*) as Total_CookLists FROM CookLists;
