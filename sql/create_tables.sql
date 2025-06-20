-- User profile table creation
CREATE TABLE Users (
  User_ID INT AUTO_INCREMENT PRIMARY KEY,
  Name VARCHAR(50) NOT NULL,
  Email VARCHAR(100) NOT NULL UNIQUE,
  Password VARCHAR(255) NOT NULL,
  Date_of_Birth DATE,
  Profile_Image VARCHAR(255),
  Points INT DEFAULT 0,
  Cookify_Level VARCHAR(50) DEFAULT '🐀 Street Rat',
  Created_At DATETIME DEFAULT CURRENT_TIMESTAMP,
  Updated_At DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Related tables for user activities
CREATE TABLE User_Activities (
  Activity_ID INT AUTO_INCREMENT PRIMARY KEY,
  User_ID INT NOT NULL,
  Activity_Type ENUM('recipe_created', 'recipe_liked', 'recipe_cooked', 'cooklist_created', 'cooklist_shared', 'recipe_rated', 'recipe_commented'),
  Points_Earned INT DEFAULT 0,
  Activity_Date DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (User_ID) REFERENCES Users(User_ID) ON DELETE CASCADE
); 