-- Test queries for user profile creation feature

-- 1. Check if email already exists (validation query)
SELECT User_ID FROM Users WHERE Email = 'john.doe@email.com';

-- 2. Insert new user profile
INSERT INTO Users (Name, Email, Password, Cookify_Level) 
VALUES ('John Doe', 'john.doe@email.com', '$2b$12$hashed_password_example', '🐀 Street Rat');

-- 3. Verify user was created successfully
SELECT User_ID, Name, Email, Cookify_Level, Created_At 
FROM Users 
WHERE Email = 'john.doe@email.com';

-- 4. Insert another valid user (formerly duplicate test)
INSERT INTO Users (Name, Email, Password, Cookify_Level) 
VALUES ('Jane Smith', 'jane.doe@email.com', '$2b$12$another_hashed_password', '🐀 Street Rat');

-- 5. Create another valid user
INSERT INTO Users (Name, Email, Password, Cookify_Level) 
VALUES ('Sarah Chef', 'sarah.chef@email.com', '$2b$12$sarah_hashed_password', '🐀 Street Rat');

-- 6. View all created users
SELECT User_ID, Name, Email, Cookify_Level, Created_At FROM Users ORDER BY Created_At DESC; 



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

-- List all columns from Recipes
SELECT * FROM Recipes;

-- Insert new recipe:
INSERT INTO Recipes
    (Name, Duration, Difficulty, Cuisine, Instructions, Image_URL, User_ID)
VALUES
    (
      'Blueberry Pancakes',
      25,
      'Easy',
      'American',
      'Mix flour, milk, eggs, and blueberries; cook on griddle until golden brown; serve with syrup.',
      'https://example.com/images/blueberry_pancakes.jpg',
      1
    );

-- List all columns from Recipes
SELECT * FROM Recipes;

-- Update recipe:
UPDATE Recipes
SET
    Name         = 'Blueberry Banana Pancakes',
    Duration     = 30,
    Difficulty   = 'Easy',
    Cuisine      = 'American',
    Instructions = 'Combine flour, milk, eggs, mashed banana, and blueberries; cook on griddle until golden; serve with honey or syrup.',
    Image_URL    = 'https://example.com/images/blueberry_banana_pancakes.jpg'
WHERE
    Recipe_ID    = 1
  AND User_ID      = 1;

-- List all columns from Recipes
SELECT * FROM Recipes;