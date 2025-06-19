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