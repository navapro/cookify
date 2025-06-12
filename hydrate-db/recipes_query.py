import mysql.connector

connection = mysql.connector.connect(**DB_CONFIG)
cursor = connection.cursor()
DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "password",
    "database": "cookify",
    "charset": "utf8mb4",
    "use_unicode": True,
}

# RAW SQL QUERIES:
ADD_RECIPE_SQL = """
INSERT INTO Recipes
    (Name, Duration, Difficulty, Cuisine,
     Instructions, Recipe_Link, Image_URL)
VALUES
    (%s, %s, %s, %s, %s, %s, %s);
"""

UPDATE_RECIPE_SQL = """
UPDATE Recipes
SET
    Name         = %s,
    Duration     = %s,
    Difficulty   = %s,
    Cuisine      = %s,
    Instructions = %s,
    Recipe_Link  = %s,
    Image_URL    = %s
WHERE
    Recipe_ID    = %s;
"""

GET_RECIPE_SQL = "SELECT * FROM Recipes WHERE Recipe_ID = %s;"

LIST_RECIPES_SQL = "SELECT * FROM Recipes ORDER BY Name ASC;"

PAGED_RECIPES_SQL = """
SELECT *
FROM Recipes
ORDER BY Name ASC
LIMIT %s OFFSET %s;
"""

# Helper functions.
def add_recipe(cursor, values):
    cursor.execute(ADD_RECIPE_SQL, values)
    return cursor.lastrowid

def update_recipe(cursor, values):
    cursor.execute(UPDATE_RECIPE_SQL, values)

def get_recipe(cursor, recipe_id):
    cursor.execute(GET_RECIPE_SQL, (recipe_id,))
    return cursor.fetchone()

def list_recipes(cursor, limit=None, offset=0):
    if limit is None:
        cursor.execute(LIST_RECIPES_SQL)
    else:
        cursor.execute(PAGED_RECIPES_SQL, (limit, offset))
    return cursor.fetchall()
