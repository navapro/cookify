-- Feature 1: User Creation
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

-- feature 2: searching for recipes
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
VALUES (2, 'Vegetarian recipes', 'veggie tales themed dinner party XD', TRUE);

-- add a recipe to a cooklist
INSERT INTO CookList_Recipes (CookList_ID, Recipe_ID) VALUES (6, 2);
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


-- feature 4: updating a recipe
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
    Recipe_ID    = 2
  AND User_ID      = 1;

-- List all columns from Recipes
SELECT * FROM Recipes;

-- feature 5: trigger to update liked cooklists
-- trigger for automatically generating 'Liked Recipes' cooklist
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
		IF ((SELECT COUNT(*) FROM Cooklists WHERE User_ID = NEW.User_ID AND Name = 'Liked Recipes') > 0) THEN
			SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Only one Liked Recipes cooklist can exist!';
		END IF;
	END; //

-- creating trigger, assumes all users have a liked recipes cooklist by default
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

-- creating user and their Liked Recipes cooklist
INSERT INTO Users (Name, Email, Password, Date_of_Birth, Points, Cookify_Level) VALUES
('Wayne Ju', 'w4ju@uwaterloo.ca', '$2b$10$hashedpassword1', '2005-09-11', 45, '🏠 Restaurant Owner');

-- checking that Liked Recipes exists
SELECT * FROM Cooklists WHERE User_ID = 6 AND Name = 'Liked Recipes';

-- adding recipes to like (totally not reused from feature 2)
INSERT INTO Recipes (Recipe_ID, User_ID, Name, Duration, Difficulty, Cuisine, Instructions, Servings, Image_URL) VALUES
(101, 1, 'Rosemary Focaccia', 120, 'Medium', 'Italian', 'cook good. good cook.', 1, 'very real link'),
(102, 1, 'Tamagoyaki', 15, 'Medium', 'Japanese', 'also cook good. please.', 3, 'slightly real link'),
(103, 2, 'Okonomiyaki', 30, 'Medium', 'Japanese', 'cook good (optional)', 12, 'very fake link'),
(104, 3, 'Fried Rice', 15, 'Easy', 'Chinese', 'a (blank) fried this rice!?!?!?', 1, 'very real link'),
(105, 4, 'Croissants', 300, 'Hard', 'French', 'hon hon hon', 6, 'very real link');

-- liking recipes
INSERT INTO Recipe_Likes (User_ID, Recipe_ID) VALUES
(6, 104),
(6, 105),
(6, 102);

-- viewing liked recipes
SELECT * FROM Cooklist_Recipes WHERE Cooklist_ID = (SELECT Cooklist_ID FROM Cooklists WHERE User_ID = '6' AND Name = 'Liked Recipes');

-- attempting to create a new Liked Recipes Cooklist for Wayne (which gives an error)
-- INSERT INTO Cooklists (User_ID, Name, Description, Is_Public) VALUES (6, 'Liked Recipes', 'All your liked recipes in one place!', TRUE);
