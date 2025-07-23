import mysql.connector
import random
import datetime
from pathlib import Path
import sys
from hydrate_db_helpers import (
    create_dummy_users,
    create_dummy_cooklists,
    create_dummy_cooklist_recipes,
    create_dummy_recipe_likes,
    create_dummy_cooklist_likes,
    create_dummy_user_ingredients,
    # setup_user2_test_data
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

            # try:
            #     cursor.execute(
            #         "INSERT INTO Recipe_Ingredients (Recipe_ID, Ingredient_ID, Quantity, Unit)"
            #         " VALUES (%s, %s, %s, %s)",
            #         (rid,
            #          get_or_create_ingredient(cursor, conn, name),
            #          qty_val,
            #          unit_val)
            #     )
            # except IntegrityError:
            #     pass
            try:
                # Convert qty_val to an integer before inserting
                qty_int = int(float(qty_val)) if qty_val else 1
                
                cursor.execute(
                    "INSERT INTO Recipe_Ingredients (Recipe_ID, Ingredient_ID, Quantity, Unit)"
                    " VALUES (%s, %s, %s, %s)",
                    (rid,
                    get_or_create_ingredient(cursor, conn, name),
                    qty_int,  # Use integer value instead of string
                    unit_val)
                )
            except (IntegrityError, ValueError) as e:
                print(f"Warning: Could not add ingredient '{name}' to recipe {rid}: {e}")
                pass
        conn.commit()

    return recipe_ids


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

    # 1) Users
    ids = create_dummy_users(cursor, conn, n=10)
    admin_id = ids['admin_id']
    user_ids = ids['user_ids']
    # test_chef_id = ids.get('test_chef_id', 2)  # Get TestChef ID, default to 2 if not found

    # 2) CookLists
    cooklist_ids = create_dummy_cooklists(cursor, conn, user_ids, lists_per_user=2)

    # 3) Recipes & Ingredients
    recipe_ids = create_dummy_recipes(cursor, conn, admin_id, num_recipes=20)

    # 4) Associations
    create_dummy_cooklist_recipes(cursor, conn, cooklist_ids, recipe_ids, user_ids)
    create_dummy_recipe_likes(cursor, conn, user_ids, recipe_ids, like_probability=0.3)
    create_dummy_cooklist_likes(cursor, conn, user_ids, cooklist_ids, like_probability=0.2)
    create_dummy_user_ingredients(cursor, conn, user_ids, 15)
    
    # 5) Create comprehensive test data for TestChef (User 2)
    # TestChef user was already created in create_dummy_users with ID=2
    # setup_user2_test_data(cursor, conn, recipe_ids)

    cursor.close()
    conn.close()
    print("Data population complete.")

if __name__ == '__main__':
    main()
