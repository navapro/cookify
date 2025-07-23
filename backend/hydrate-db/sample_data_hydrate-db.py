import mysql.connector
import random
from pathlib import Path
import sys
from hydrate_db_helpers import (
    create_dummy_users,
    create_dummy_cooklists,
    create_dummy_cooklist_recipes,
    create_dummy_recipe_likes,
    create_dummy_cooklist_likes,
    create_dummy_user_ingredients
)

# If you also want to parse ingredient strings, re-import parse_ingredient
from hydrate_db_helpers import IntegrityError  # for exception handling
sys.path.append(str(Path(__file__).parent.parent))
from config import Config


def create_dummy_recipes(cursor, conn, admin_id, num_recipes=20):
    """
    Create dummy recipes using the admin_id as the author.  
    Returns a list of created Recipe_IDs.
    """
    sample_titles = [
        "Spicy Tomato Soup",
        "Herb Roasted Chicken",
        "Vegan Buddha Bowl",
        "Classic Pancakes",
        "Garlic Butter Shrimp",
        "Chocolate Chip Cookies",
        "Quinoa Salad",
        "Beef Stir Fry",
        "Lemon Drizzle Cake",
        "Mango Smoothie",
        "Avocado Toast",
        "Pumpkin Spice Latte",
        "Grilled Cheese Sandwich",
        "Mediterranean Pasta",
        "Teriyaki Salmon",
        "BBQ Pulled Pork",
        "Greek Yogurt Parfait",
        "Spinach Frittata",
        "Cauliflower Tacos",
        "Berry Chia Pudding"
    ]

    # sample ingredients pool
    sample_ingredients = [
        "1 cup flour",
        "2 tbsp olive oil",
        "3 cloves garlic",
        "fresh basil",
        "salt",
        "pepper",
        "200g chicken breast",
        "1 tbsp soy sauce",
        "2 tsp sugar",
        "100ml milk",
        "1 egg",
        "handful spinach",
        "1 avocado",
        "100g shrimp",
        "150g quinoa",
    ]

    recipe_ids = []
    for i, title in enumerate(sample_titles[:num_recipes]):
        duration = random.randrange(10, 120, 10)
        difficulty = random.choice(["Easy", "Intermediate", "Hard"])
        cuisine = random.choice(["American", "Italian", "Asian", "Mexican", "Mediterranean"])
        instructions = f"Step-by-step instructions for {title}."

        # Generate image URL from title
        slug = title.lower().replace(' ', '-')
        image_url = f"/images/{slug}.jpg"

        # Insert recipe
        cursor.execute(
            """
            INSERT INTO Recipes
              (Name, Duration, Difficulty, Cuisine, Instructions, Image_URL, User_ID)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (title, duration, difficulty, cuisine, instructions, image_url, admin_id)
        )
        conn.commit()
        rid = cursor.lastrowid
        recipe_ids.append(rid)
        print(f"Inserted recipe '{title}' with ID={rid} and Image_URL={image_url}")

        # Attach 3-6 random ingredients
        ingredients_list = random.sample(sample_ingredients, random.randint(3, 6))
        for ing_str in ingredients_list:
            parts = ing_str.split(None, 2)
            if len(parts) == 3 and parts[1].isalpha():
                qty, unit, name = parts
            elif len(parts) == 2:
                if parts[0].replace('.', '', 1).isdigit():
                    qty = parts[0]
                    unit = None
                    name = parts[1]
                else:
                    qty = None
                    unit = None
                    name = ing_str
            else:
                qty = None
                unit = None
                name = ing_str

            unit_val = unit if unit else "count"
            qty_val = qty if qty else '1'

            try:
                # Convert qty_val to integer before inserting
                numeric_qty = parse_quantity(qty_val)
                
                cursor.execute(
                    "INSERT INTO Recipe_Ingredients (Recipe_ID, Ingredient_ID, Quantity, Unit)"
                    " VALUES (%s, %s, %s, %s)",
                    (rid,
                     get_or_create_ingredient(cursor, conn, name),
                     numeric_qty,  # Use the parsed numeric value instead of qty_val directly
                     unit_val)
                )
            except Exception as e:
                print(f"Warning: Could not add ingredient '{name}' to recipe {rid}, qty='{qty_val}': {e}")
                # Try again with default quantity of 1 as fallback
                try:
                    cursor.execute(
                        "INSERT INTO Recipe_Ingredients (Recipe_ID, Ingredient_ID, Quantity, Unit)"
                        " VALUES (%s, %s, %s, %s)",
                        (rid,
                         get_or_create_ingredient(cursor, conn, name),
                         1,  # Default to 1 as fallback
                         unit_val)
                    )
                    print(f"  - Fallback succeeded: Used quantity=1 for ingredient '{name}'")
                except Exception as e2:
                    print(f"  - Fallback failed: {e2}")
                    pass
        conn.commit()

    return recipe_ids


def parse_quantity(qty_str):
    """Parse a quantity string that might include units like '200g' and extract just the number.
    Also handles special fraction characters like ¼, ½, ¾."""
    if not qty_str:
        return 1
    
    # Convert common fraction characters to their decimal equivalents
    fraction_map = {
        '¼': 0.25,
        '½': 0.5,
        '¾': 0.75,
        '⅓': 0.33,
        '⅔': 0.67,
        '⅛': 0.125,
        '⅜': 0.375,
        '⅝': 0.625,
        '⅞': 0.875
    }
    
    qty_str = str(qty_str).strip()
    
    # Check if the quantity is a special fraction character
    if qty_str in fraction_map:
        return fraction_map[qty_str]
    
    # Handle mixed numbers like "1¼" (1.25)
    import re
    mixed_number = re.match(r'^(\d+)([¼½¾⅓⅔⅛⅜⅝⅞])$', qty_str)
    if mixed_number:
        whole = int(mixed_number.group(1))
        fraction = fraction_map.get(mixed_number.group(2), 0)
        return int(whole + fraction)
        
    # Extract just the numeric part from strings like '200g', '1.5kg', etc.
    numeric_part = re.match(r'^([\d.]+)', qty_str)
    if numeric_part:
        try:
            return int(float(numeric_part.group(1)))
        except (ValueError, TypeError):
            pass
            
    return 1  # Default to 1 if parsing fails


def get_or_create_ingredient(cursor, conn, ing_name: str):
    """
    Fetches Ingredient_ID for ing_name (case-insensitive), or creates it.
    """
    key = ing_name.lower()
    cursor.execute(
        "SELECT Ingredient_ID FROM Ingredients WHERE LOWER(Name) = %s",
        (key,)
    )
    row = cursor.fetchone()
    if row:
        return row[0]

    cursor.execute(
        "INSERT INTO Ingredients (Name) VALUES (%s)",
        (ing_name,)
    )
    conn.commit()
    return cursor.lastrowid


def main():
    config = Config()
    DB_CONFIG = {
        'host': config.MYSQL_HOST,
        'user': config.MYSQL_USER,
        'password': config.MYSQL_PASSWORD,
        'database': config.MYSQL_DB,
        'charset': 'utf8mb4',
        'use_unicode': True,
        "port": config.MYSQL_PORT
    }
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(buffered=True)

    # Disable triggers before creating users
    print("Temporarily disabling triggers...")
    cursor.execute("SET @TRIGGER_DISABLED = 1;")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

    # 1) Users
    ids = create_dummy_users(cursor, conn, n=10)
    admin_id = ids['admin_id']
    user_ids = ids['user_ids']

    # 2) CookLists
    cooklist_ids = create_dummy_cooklists(cursor, conn, user_ids, lists_per_user=2)

    # 3) Recipes & Ingredients
    recipe_ids = create_dummy_recipes(cursor, conn, admin_id, num_recipes=20)
    
    # Re-enable triggers for subsequent operations
    print("Re-enabling triggers...")
    cursor.execute("SET @TRIGGER_DISABLED = NULL;")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

    # 4) Associations
    create_dummy_cooklist_recipes(cursor, conn, cooklist_ids, recipe_ids)
    create_dummy_recipe_likes(cursor, conn, user_ids, recipe_ids, like_probability=0.3)
    create_dummy_cooklist_likes(cursor, conn, user_ids, cooklist_ids, like_probability=0.2)
    create_dummy_user_ingredients(cursor, conn, user_ids, 15)

    cursor.close()
    conn.close()
    print("Data population complete.")

if __name__ == '__main__':
    main()
