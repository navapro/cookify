import mysql.connector
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from config import Config
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

connection = mysql.connector.connect(**DB_CONFIG)
cursor = connection.cursor()

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
