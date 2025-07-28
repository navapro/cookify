-- Test Sample SQL
-- Updated to match the new schema and test all features including triggers

-- Feature 1: User Creation
-- Test queries for user profile creation feature

-- 1. Check if email already exists (validation query)
SELECT User_ID FROM Users WHERE Email = 'john.doe@email.com';

-- 2. Insert new user profile
INSERT INTO Users (Name, Email, Password, Cookify_Level) 
VALUES ('John Doe', 'john.doe@email.com', '$2b$12$hashed_password_example', 'Street Rat');

-- 3. Verify user was created successfully
SELECT User_ID, Name, Email, Cookify_Level, Points, Profile_Image
FROM Users 
WHERE Email = 'john.doe@email.com';

-- 4. Insert another valid user
INSERT INTO Users (Name, Email, Password, Cookify_Level) 
VALUES ('Jane Smith', 'jane.smith@email.com', '$2b$12$another_hashed_password', 'Street Rat');

-- 5. Create another valid user
INSERT INTO Users (Name, Email, Password, Cookify_Level) 
VALUES ('Sarah Chef', 'sarah.chef@email.com', '$2b$12$sarah_hashed_password', 'Street Rat');

-- 6. View all created users
SELECT User_ID, Name, Email, Cookify_Level, Points, Profile_Image FROM Users ORDER BY User_ID DESC; 

-- feature 2: searching for recipes
-- adding more recipes
INSERT INTO Recipes (User_ID, Name, Duration, Difficulty, Cuisine, Instructions, Image_URL) VALUES
(1, 'Rosemary Focaccia', 120, 'Medium', 'Italian', 'cook good. good cook.', 'very real link'),
(1, 'Tamagoyaki', 15, 'Medium', 'Japanese', 'also cook good. please.', 'slightly real link'),
(2, 'Okonomiyaki', 30, 'Medium', 'Japanese', 'cook good (optional)', 'very fake link'),
(3, 'Fried Rice', 15, 'Easy', 'Chinese', 'a (blank) fried this rice!?!?!?', 'very real link'),
(4, 'Croissants', 300, 'Hard', 'French', 'hon hon hon', 'very real link');

-- selecting with parameters:
--      Duration: < 30 minutes
SELECT r.Recipe_ID, r.User_ID, r.Name, r.Duration, r.Difficulty, r.Cuisine, r.Instructions
FROM Recipes r
WHERE r.duration < 30;

-- selecting with parameters:
--      Cuisine: 'Japanese'
SELECT r.Recipe_ID, r.User_ID, r.Name, r.Duration, r.Difficulty, r.Cuisine, r.Instructions
FROM Recipes r
WHERE r.cuisine = 'Japanese';

-- selecting with parameters:
--      Search: "yaki"
SELECT r.Recipe_ID, r.User_ID, r.Name, r.Duration, r.Difficulty, r.Cuisine, r.Instructions
FROM Recipes r
WHERE r.name LIKE '%yaki%';

-- selecting with parameters:
--      Duration: > 60 minutes
--      Search: "Rosemary"
SELECT r.Recipe_ID, r.User_ID, r.Name, r.Duration, r.Difficulty, r.Cuisine, r.Instructions
FROM Recipes r
WHERE r.duration > 60
AND r.name LIKE '%Rosemary%';


-- feature 3: viewing a cooklist sample queries
-- creating a cooklist
INSERT INTO CookLists (User_ID, Name, Description, Is_Public) 
VALUES (1, 'Vegetarian recipes', 'veggie tales themed dinner party XD', TRUE);

-- add a recipe to a cooklist
INSERT INTO CookList_Recipes (CookList_ID, Recipe_ID) 
VALUES (6, 2);
INSERT INTO CookList_Recipes (CookList_ID, Recipe_ID) VALUES (6, 4);

-- select ordered list of cooklist recipes (ordered by date, from most recent to earliest)
SELECT r.Recipe_ID, r.Name, r.Cuisine, r.Difficulty, r.Instructions, clr.Added_At AS Added_To_List_At 
FROM CookList_Recipes clr 
JOIN Recipes r ON clr.Recipe_ID = r.Recipe_ID 
WHERE clr.CookList_ID = 6 
ORDER BY clr.Added_At DESC; 

-- select ordered list of cooklist recipes (ordered by date)
SELECT r.Recipe_ID, r.Name, r.Cuisine, r.Difficulty, r.Instructions, clr.Added_At AS Added_To_List_At  
FROM CookList_Recipes clr  
JOIN Recipes r ON clr.Recipe_ID = r.Recipe_ID  
WHERE clr.CookList_ID = 6  
ORDER BY r.Name ASC; 


-- Feature 4: Updating a Recipe
-- List all columns from Recipes
SELECT * FROM Recipes;

-- Insert new recipe for testing updates
INSERT INTO Recipes
    (Name, Duration, Difficulty, Cuisine, Instructions, Image_URL, User_ID)
VALUES
    (
      'Test Blueberry Pancakes',
      25,
      'Easy',
      'American',
      'Mix flour, milk, eggs, and blueberries; cook on griddle until golden brown; serve with syrup.',
      'https://example.com/images/blueberry_pancakes.jpg',
      1
    );

-- Get the Recipe_ID of the recipe we just inserted
SELECT Recipe_ID, Name FROM Recipes WHERE Name = 'Test Blueberry Pancakes' AND User_ID = 1;

-- Update recipe (replace LAST_INSERT_ID() with actual Recipe_ID if needed)
UPDATE Recipes
SET
    Name         = 'Test Blueberry Banana Pancakes',
    Duration     = 30,
    Difficulty   = 'Easy',
    Cuisine      = 'American',
    Instructions = 'Combine flour, milk, eggs, mashed banana, and blueberries; cook on griddle until golden; serve with honey or syrup.',
    Image_URL    = 'https://example.com/images/blueberry_banana_pancakes.jpg'
WHERE
    Name = 'Test Blueberry Pancakes'
  AND User_ID = 1;

-- List all columns from Recipes to verify update
SELECT * FROM Recipes WHERE Name LIKE '%Blueberry%';

-- feature 5: trigger to update liked cooklists
-- trigger for automatically generating 'Liked Recipes' cooklist (trigger in create_tables.sql)
-- Creating user and their Liked Recipes cooklist (should auto-create via trigger)
INSERT INTO Users (Name, Email, Password, Date_of_Birth, Points, Cookify_Level) VALUES
('Wayne Ju', 'w4ju@uwaterloo.ca', '$2b$10$hashedpassword1', '2005-09-11', 0, 'Street Rat');

-- Get Wayne's User_ID
SET @wayne_id = (SELECT User_ID FROM Users WHERE Email = 'w4ju@uwaterloo.ca');

-- Check that Liked Recipes cooklist was automatically created
SELECT * FROM CookLists WHERE User_ID = @wayne_id AND Name = 'Liked Recipes';

-- Adding recipes to like (using existing Recipe_IDs)
INSERT INTO Recipe_Likes (User_ID, Recipe_ID) VALUES
(@wayne_id, 1),  -- Like Carbonara
(@wayne_id, 3),  -- Like Garlic Chicken
(@wayne_id, 5);  -- Like Beef Wellington

-- View Wayne's liked recipes
SELECT * FROM Recipe_Likes WHERE User_ID = @wayne_id;

-- View recipes in Wayne's Liked Recipes cooklist (should be automatically added)
SELECT r.Recipe_ID, r.Name, r.Cuisine, r.Difficulty 
FROM Recipes r 
WHERE EXISTS (
    SELECT Recipe_ID 
    FROM CookList_Recipes 
    WHERE CookList_ID = (SELECT CookList_ID FROM CookLists WHERE User_ID = @wayne_id AND Name = 'Liked Recipes') 
    AND Recipe_ID = r.Recipe_ID
);

-- attempting to create a new Liked Recipes Cooklist for Wayne (which intentionally gives an error)
-- INSERT INTO Cooklists (User_ID, Name, Description, Is_Public) VALUES (6, 'Liked Recipes', 'All your liked recipes in one place!', TRUE);

-- advanced feature 1: 
-- inserting extra ingredients so that user 2 has enough to make recipe 1
INSERT INTO User_Ingredients (User_ID, Ingredient_ID, Quantity) VALUES (2, 2, 2);

-- Drop the view if it exists to prevent errors on rerun
DROP VIEW IF EXISTS My_Ingredients;
-- creating view (if you're user 2)
CREATE VIEW My_Ingredients AS
SELECT i.Ingredient_ID, i.Name, ui.Quantity
FROM Ingredients i, User_Ingredients ui
WHERE ui.User_ID = 2 AND i.Ingredient_ID = ui.Ingredient_ID;

-- query for all recipes you can make
SELECT has.Recipe_ID
FROM (SELECT ri.Recipe_ID, COUNT(*) AS IngredientCount
FROM Recipe_Ingredients ri
GROUP BY ri.Recipe_ID) AS required,
(SELECT ri.Recipe_ID, COUNT(*) AS IngredientCount
FROM Recipe_Ingredients ri, My_Ingredients mi
WHERE ri.Ingredient_ID = mi.Ingredient_ID AND ri.Quantity <= mi.Quantity
GROUP BY ri.Recipe_ID) AS has
WHERE required.Recipe_ID = has.Recipe_ID AND required.IngredientCount = has.IngredientCount;


-- Advanced Features 2 & 3: Point System and Leveling Triggers
-- 1. Create a test user at Street Rat level (0 points)
INSERT INTO Users (User_ID, Name, Email, Password, Cookify_Level, Points)
VALUES (9999, 'Test Leveling User', 'test.level@example.com', '$2b$12$test_password_hash', 'Street Rat', 9)
ON DUPLICATE KEY UPDATE Points = 9, Cookify_Level = 'Street Rat';

-- 2. Show initial level and points
SELECT User_ID, Name, Points, Cookify_Level, Profile_Image 
FROM Users 
WHERE User_ID = 9999;

-- 3. Create a recipe for this user
INSERT INTO Recipes (Recipe_ID, Name, Duration, Difficulty, Cuisine, Instructions, User_ID)
VALUES (9999, 'Level Testing Recipe', 30, 'Easy', 'Test', 'This recipe is for testing the level system', 9999)
ON DUPLICATE KEY UPDATE Recipe_ID = Recipe_ID;

-- 4. Have two users like the recipe (should add 2 points)
INSERT INTO Recipe_Likes (User_ID, Recipe_ID)
VALUES (1, 9999)
ON DUPLICATE KEY UPDATE User_ID = User_ID;

INSERT INTO Recipe_Likes (User_ID, Recipe_ID)
VALUES (2, 9999)
ON DUPLICATE KEY UPDATE User_ID = User_ID;

-- 5. Check the user's new level after 10 total likes (should be Dishwasher)
SELECT User_ID, Name, Points, Cookify_Level, Profile_Image 
FROM Users 
WHERE User_ID = 9999;

-- 6. Display the leveling system for reference
SELECT Level_Name, Min_Points, Image_Path
FROM User_Levels
ORDER BY Min_Points;

-- Final verification
SELECT 'Test Sample Complete!' as Status;