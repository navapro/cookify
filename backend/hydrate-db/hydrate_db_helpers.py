import datetime
import random
from mysql.connector import IntegrityError

def create_dummy_users(cursor, conn, n=10):
    """
    Inserts one admin user and n dummy users into Users.
    Returns a dict with admin_id and a list of created user_ids.
    """
    created_ids = {
        'admin_id': None,
        'user_ids': []
    }

    # 1) Create admin user
    try:
        cursor.execute(
            """
            INSERT INTO Users (Name, Email, Password, Date_of_Birth, Cookify_Level, Points, Profile_Image)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                'admin',
                'admin@example.com',
                'adminpassword',  # override in production
                datetime.date(1990, 1, 1),
                100,  # highest level for admin,
                1000,
                "USER_IMAGE_ADMIN"
            )
        )
        conn.commit()
        created_ids['admin_id'] = cursor.lastrowid
        print(f"Created admin user with ID={created_ids['admin_id']}")
    except IntegrityError:
        # If already exists, fetch existing ID
        cursor.execute(
            "SELECT User_ID FROM Users WHERE Email=%s",
            ('admin@example.com',)
        )
        row = cursor.fetchone()
        if row:
            created_ids['admin_id'] = row[0]
            print(f"Admin already exists with ID={created_ids['admin_id']}")
        else:
            print("Warning: could not create or find admin user.")

    # 2) Create n dummy users
    for i in range(1, n+1):
        name = f"User{i}"
        email = f"user{i}@example.com"
        password = f"password{i}"
        year  = random.randint(1950, 2000)
        month = random.randint(1, 12)
        day   = random.randint(1, 28)
        dob   = datetime.date(year, month, day)
        level = random.randint(0, 80)
        points = random.randint(5, 50)
        img = f"USER_IMAGE_{i}"

        try:
            cursor.execute(
                """
                INSERT INTO Users (Name, Email, Password, Date_of_Birth, Cookify_Level, Points, Profile_Image)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (name, email, password, dob, level, points, img)
            )
            conn.commit()
            uid = cursor.lastrowid
            created_ids['user_ids'].append(uid)
            print(f"Inserted dummy user '{name}' with ID={uid}")
        except IntegrityError:
            # fetch existing
            cursor.execute(
                "SELECT User_ID FROM Users WHERE Email=%s",
                (email,)
            )
            row = cursor.fetchone()
            if row:
                uid = row[0]
                created_ids['user_ids'].append(uid)
                print(f"User '{name}' already exists with ID={uid}")
            else:
                print(f"Warning: could not insert or find user '{name}'")

    return created_ids

def create_dummy_user_ingredients(cursor, conn, user_ids,  num_of_sample_ingredients, max_ingredients_per_user=5):
    """
    For each user in user_ids, assign between 1 and max_ingredients_per_user random ingredients.
    Each assignment gets a random Acquired_At timestamp within the last year.
    """
    for u in user_ids:
        # pick how many ingredients this user has
        n = random.randint(1, min(max_ingredients_per_user,  num_of_sample_ingredients))
        picks = random.sample(range(1, num_of_sample_ingredients), n)
        for ing in picks:
            quantity = random.randint(1, 100)
            try:
                cursor.execute(
                    """
                    INSERT INTO User_Ingredients (User_ID, Ingredient_ID, Quantity)
                    VALUES (%s, %s, %s)
                    """,
                    (u, ing, quantity)
                )
            except IntegrityError:
                # skip if already exists
                conn.rollback()
        conn.commit()
    print("Populated User_Ingredients.")

def create_dummy_cooklists(cursor, conn, user_ids, lists_per_user=2):
    """
    For each user in user_ids, create `lists_per_user` CookLists.
    Returns a list of all CookList_IDs.
    """
    cooklist_ids = []
    for u in user_ids:
        for i in range(lists_per_user):
            name = f"{u}'s List {i+1}"
            desc = f"A sample cooklist #{i+1} for user {u}"
            is_public = random.choice([True, False])
            try:
                cursor.execute(
                    """
                    INSERT INTO CookLists
                      (User_ID, Name, Description, Is_Public)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (u, name, desc, is_public)
                )
                conn.commit()
                cooklist_ids.append(cursor.lastrowid)
            except IntegrityError:
                # (unlikely here) skip duplicates
                conn.rollback()
    print(f"Created {len(cooklist_ids)} cooklists.")
    return cooklist_ids

def create_dummy_cooklist_recipes(cursor, conn, cooklist_ids, recipe_ids, max_recipes_per_list=5):
    """
    For each cooklist, add 1–`max_recipes_per_list` random recipes.
    Each entry gets a random Added_At datetime within the last 90 days.
    """
    for cl in cooklist_ids:
        n = random.randint(1, min(max_recipes_per_list, len(recipe_ids)))
        picks = random.sample(recipe_ids, n)
        for r in picks:
            # Generate a random datetime within the last 90 days
            days_ago = random.randint(0, 90)
            seconds_ago = random.randint(0, 86400)
            added_at = datetime.datetime.now() - datetime.timedelta(days=days_ago, seconds=seconds_ago)
            try:
                cursor.execute(
                    "INSERT INTO CookList_Recipes (CookList_ID, Recipe_ID, Added_At) VALUES (%s, %s, %s)",
                    (cl, r, added_at)
                )
            except IntegrityError:
                pass
    conn.commit()
    print("Populated CookList_Recipes.")

def create_dummy_recipe_likes(cursor, conn, user_ids, recipe_ids, like_probability=0.2):
    """
    For each user–recipe pair, like with probability `like_probability`.
    """
    for u in user_ids:
        for r in recipe_ids:
            if random.random() < like_probability:
                try:
                    cursor.execute(
                        "INSERT INTO Recipe_Likes (User_ID, Recipe_ID) VALUES (%s, %s)",
                        (u, r)
                    )
                except IntegrityError:
                    pass
    conn.commit()
    print("Populated Recipe_Likes.")

def create_dummy_cooklist_likes(cursor, conn, user_ids, cooklist_ids, like_probability=0.1):
    """
    For each user–cooklist pair (excluding owner), like with probability `like_probability`.
    """
    # First fetch owner map:
    cursor.execute("SELECT CookList_ID, User_ID FROM CookLists")
    owner_of = {cid: uid for cid, uid in cursor}
    for u in user_ids:
        for cl in cooklist_ids:
            if owner_of.get(cl) == u:
                continue  # users don't like their own lists
            if random.random() < like_probability:
                try:
                    cursor.execute(
                        "INSERT INTO CookList_Likes (User_ID, CookList_ID) VALUES (%s, %s)",
                        (u, cl)
                    )
                except IntegrityError:
                    pass
    conn.commit()
    print("Populated CookList_Likes.")
