import mysql.connector
from mysql.connector import errorcode, IntegrityError
import pandas as pd
import ast
import re

# ---------- Configuration ----------
DB_CONFIG = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'cookify_db',
    'charset': 'utf8mb4',
    'use_unicode': True,
}

CSV_PATH = 'recipes.csv'  # adjust path to your CSV

# If your Image_Name should map to a URL/path, adjust this function:
def make_image_url(image_name: str) -> str:
    if not image_name or pd.isna(image_name):
        return None
    # example: store under /images/{image_name}.jpg
    return f"/images/{image_name}.jpg"

# Simple heuristic parser for ingredient strings.
# Returns (quantity: str or None, unit: str or None, name: str)
COMMON_UNITS = {
    'cup','cups','tbsp','tbsp.','tablespoon','tablespoons',
    'tsp','tsp.','teaspoon','teaspoons',
    'oz','ounce','ounces','lb','lb.','pound','pounds',
    'clove','cloves','slice','slices','piece','pieces',
    'gram','grams','g','kg','kilogram','kilograms',
    'pinch','pinches','quart','quarts','liter','liters','ml','milliliter','milliliters'
}

def parse_ingredient(ing_str: str):
    """
    Heuristic: split off first token as quantity, 
    check second token against COMMON_UNITS for unit,
    rest as name. If fails, leave quantity/unit None and name = full string.
    """
    s = ing_str.strip()
    if not s:
        return None, None, ''
    parts = s.split(None, 1)
    if len(parts) == 1:
        # no spaces
        return None, None, s
    qty_candidate, rest = parts
    # Basic check: qty_candidate contains digits or fractions?
    # We'll accept as quantity if it contains any digit or fraction char
    if re.search(r'[\d¼½¾⅓⅔–/]', qty_candidate):
        # check unit
        subparts = rest.split(None, 1)
        token = subparts[0].lower().rstrip('.,')
        if token in COMMON_UNITS:
            unit = token
            name = subparts[1].strip() if len(subparts) > 1 else ''
            return qty_candidate, unit, name
        else:
            # no recognized unit: treat rest as name, qty as qty_candidate
            return qty_candidate, None, rest.strip()
    else:
        # first token isn't a quantity: treat full as name
        return None, None, s

# ---------- Main logic ----------
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
    # Cache for ingredient name -> Ingredient_ID
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

    # Ensure the column for ingredients exists
    if 'Cleaned_Ingredients' not in df.columns:
        print("Error: 'Cleaned_Ingredients' column not found in CSV")
        return

    # 3. Iterate rows
    for idx, row in df.iterrows():
        name = row.get('Title')
        instructions = row.get('Instructions')
        image_name = row.get('Image_Name')
        image_url = make_image_url(image_name)

        # Begin transaction for this recipe
        try:
            conn.start_transaction()

            # 3a. Insert into Recipes.
            # We only supply Name, Instructions, Image_URL. The rest (Duration, Difficulty, Cuisine, Servings) default to NULL.
            insert_recipe_sql = """
                INSERT INTO Recipes (Name, Instructions, Image_URL)
                VALUES (%s, %s, %s)
            """
            cursor.execute(insert_recipe_sql, (name, instructions, image_url))
            recipe_id = cursor.lastrowid

            # 3b. Parse Cleaned_Ingredients: assume string representation of Python list
            raw = row['Cleaned_Ingredients']
            ing_list = []
            if pd.isna(raw):
                ing_list = []
            else:
                # Try to parse. If it's e.g. "['a', 'b', ...]" or JSON-like
                try:
                    ing_list = ast.literal_eval(raw)
                    if not isinstance(ing_list, list):
                        raise ValueError
                except Exception:
                    # fallback: if comma-separated string
                    # split on comma, but this is brittle
                    ing_list = [s.strip() for s in str(raw).split(',') if s.strip()]

            # For each ingredient string:
            for ing_str in ing_list:
                qty, unit, ing_name = parse_ingredient(ing_str)
                # Normalize ing_name for lookup: lowercase, strip
                key = ing_name.lower()
                if not key:
                    # skip empty name
                    continue

                # 3b.i. Get or create Ingredient_ID
                ing_id = ingredient_cache.get(key)
                if ing_id is None:
                    # Try inserting
                    try:
                        cursor.execute(
                            "INSERT INTO Ingredients (Name) VALUES (%s)",
                            (ing_name,)
                        )
                        ing_id = cursor.lastrowid
                        ingredient_cache[key] = ing_id
                    except IntegrityError:
                        # Likely another process inserted concurrently, or duplicate
                        cursor.execute(
                            "SELECT Ingredient_ID FROM Ingredients WHERE LOWER(Name)=%s",
                            (key,)
                        )
                        result = cursor.fetchone()
                        if result:
                            ing_id = result[0]
                            ingredient_cache[key] = ing_id
                        else:
                            # Unexpected: skip
                            print(f"Warning: could not insert or find ingredient '{ing_name}'")
                            continue
                    except Exception as e:
                        print(f"Warning: error inserting ingredient '{ing_name}': {e}")
                        continue

                # 3b.ii. Insert into Recipe_Ingredients
                # Use raw qty/unit or NULL if None
                qty_val = qty if qty is not None else None
                unit_val = unit if unit is not None else None
                try:
                    cursor.execute(
                        """
                        INSERT INTO Recipe_Ingredients
                          (Recipe_ID, Ingredient_ID, Quantity, Unit, Is_Optional)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (recipe_id, ing_id, qty_val, unit_val, False)
                    )
                except IntegrityError:
                    # e.g., duplicate primary key (Recipe_ID, Ingredient_ID). Skip.
                    pass
                except Exception as e:
                    print(f"Warning: could not insert recipe_ingredient for recipe {recipe_id}, ing {ing_id}: {e}")

            # Commit this recipe’s inserts
            conn.commit()
            print(f"Inserted recipe '{name}' (ID={recipe_id}) with {len(ing_list)} ingredients")

        except Exception as e:
            conn.rollback()
            print(f"Error on recipe index {idx}, Title={name}: {e}")
            # continue with next row

    # Cleanup
    cursor.close()
    conn.close()
    print("Done.")

if __name__ == "__main__":
    main()
