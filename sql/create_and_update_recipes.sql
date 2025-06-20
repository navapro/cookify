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