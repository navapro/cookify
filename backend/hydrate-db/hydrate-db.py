import mysql.connector
from mysql.connector import errorcode, IntegrityError
import pandas as pd
import ast
import re
import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from config import Config

# ADMIN user constant
ADMIN_USER_ID = 1

config = Config()

DB_CONFIG = {
    'host': config.MYSQL_HOST,
    'user': config.MYSQL_USER,
    'password': config.MYSQL_PASSWORD,
    'database': config.MYSQL_DB,
    'charset': 'utf8mb4',
    'use_unicode': True,
}

CSV_PATH = 'recipes.csv'

def make_image_url(image_name: str) -> str:
    if not image_name or pd.isna(image_name):
        return None
    return f"/images/{image_name}.jpg"

COMMON_UNITS = {
    'cup','cups','tbsp','tbsp.','tablespoon','tablespoons',
    'tsp','tsp.','teaspoon','teaspoons',
    'oz','ounce','ounces','lb','lb.','pound','pounds',
    'clove','cloves','slice','slices','piece','pieces',
    'gram','grams','g','kg','kilogram','kilograms',
    'pinch','pinches','quart','quarts','liter','liters','ml','milliliter','milliliters'
}

def parse_ingredient(ing_str: str):
    s = ing_str.strip()
    if not s:
        return None, None, ''
    parts = s.split(None, 1)
    if len(parts) == 1:
        return None, None, s
    qty_candidate, rest = parts
    if re.search(r'[\d¼½¾⅓⅔–/]', qty_candidate):
        subparts = rest.split(None, 1)
        token = subparts[0].lower().rstrip('.,')
        if token in COMMON_UNITS:
            unit = token
            name = subparts[1].strip() if len(subparts) > 1 else ''
            return qty_candidate, unit, name
        else:
            return qty_candidate, None, rest.strip()
    else:
        return None, None, s

def main():
    # 1. Connect to MySQL
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Error: Invalid credentials")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Error: Database does not exist")
        else:
            print(err)
        return

    cursor = conn.cursor(buffered=True)
    ingredient_cache = {}

    # Pre-load existing Ingredients into cache
    try:
        cursor.execute("SELECT Ingredient_ID, Name FROM Ingredients")
        for iid, name in cursor:
            ingredient_cache[name.lower()] = iid
    except Exception as e:
        print("Warning: could not preload Ingredients:", e)

    # 2. Load CSV into DataFrame
    df = pd.read_csv(CSV_PATH)
    if 'Cleaned_Ingredients' not in df.columns:
        print("Error: 'Cleaned_Ingredients' column not found in CSV")
        return

    # 3. Iterate rows
    for idx, row in df.iterrows():
        name = row.get('Title')
        instructions = row.get('Instructions')
        image_name = row.get('Image_Name')
        image_url = make_image_url(image_name)
        top_5_cuisines = ["American", "Chinese", "Greek", "Indian", "Italian"]
        difficulty_levels = ["Easy", "Intermediate", "Hard"]
        difficulty  = random.choice(difficulty_levels)
        cuisine     = random.choice(top_5_cuisines)
        duration    = random.randrange(10, 241, 10)

        try:
            conn.start_transaction()

            # 3a. Insert into Recipes with ADMIN user
            insert_recipe_sql = """
                INSERT INTO Recipes
                  (User_ID, Name, Duration, Difficulty, Cuisine, Instructions, Image_URL)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(
                insert_recipe_sql,
                (ADMIN_USER_ID, name, duration, difficulty, cuisine, instructions, image_url)
            )
            recipe_id = cursor.lastrowid

            # 3b. Parse Cleaned_Ingredients
            raw = row['Cleaned_Ingredients']
            if pd.isna(raw):
                ing_list = []
            else:
                try:
                    ing_list = ast.literal_eval(raw)
                    if not isinstance(ing_list, list):
                        raise ValueError
                except Exception:
                    ing_list = [s.strip() for s in str(raw).split(',') if s.strip()]

            for ing_str in ing_list:
                qty, unit, ing_name = parse_ingredient(ing_str)
                key = ing_name.lower()
                if not key:
                    continue

                # 3b.i. Get or create Ingredient_ID
                ing_id = ingredient_cache.get(key)
                if ing_id is None:
                    try:
                        cursor.execute(
                            "INSERT INTO Ingredients (Name) VALUES (%s)",
                            (ing_name,)
                        )
                        ing_id = cursor.lastrowid
                        ingredient_cache[key] = ing_id
                    except IntegrityError:
                        cursor.execute(
                            "SELECT Ingredient_ID FROM Ingredients WHERE LOWER(Name)=%s",
                            (key,)
                        )
                        res = cursor.fetchone()
                        if res:
                            ing_id = res[0]
                            ingredient_cache[key] = ing_id
                        else:
                            print(f"Warning: could not insert or find ingredient '{ing_name}'")
                            continue
                    except Exception as e:
                        print(f"Warning: error inserting ingredient '{ing_name}': {e}")
                        continue

                # 3b.ii. Insert into Recipe_Ingredients with defaults
                qty_val  = qty  if qty  is not None else '1'
                unit_val = unit if unit is not None else 'count'
                try:
                    cursor.execute(
                        """
                        INSERT INTO Recipe_Ingredients
                          (Recipe_ID, Ingredient_ID, Quantity, Unit)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (recipe_id, ing_id, qty_val, unit_val)
                    )
                except IntegrityError:
                    pass
                except Exception as e:
                    print(f"Warning: could not insert recipe_ingredient for recipe {recipe_id}, ing {ing_id}: {e}")

            conn.commit()

        except Exception as e:
            conn.rollback()
            print(f"Error on recipe index {idx}, Title={name}: {e}")

    cursor.close()
    conn.close()
    print("Done.")

def clean_database():
    """
    Connects to MySQL and drops all tables in cookify_db in the proper order.
    Use with caution: this deletes all data and table definitions.
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Error: Invalid credentials")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Error: Database does not exist")
        else:
            print("Connection error:", err)
        return

    cursor = conn.cursor()
    try:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        tables = [
            "Recipe_Ingredients",
            "CookList_Recipes",
            "Recipe_Likes",
            "CookList_Likes",
            "User_Activities",
            "CookLists",
            "Ingredients",
            "Recipes",
            "Users",
        ]
        for tbl in tables:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS `{tbl}`;")
                print(f"Dropped table {tbl}")
            except mysql.connector.Error as e:
                print(f"Warning: could not drop {tbl}: {e}")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        conn.commit()
        print("Database cleaned: all Cookify tables dropped.")
    except Exception as e:
        conn.rollback()
        print("Error during cleaning:", e)
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
