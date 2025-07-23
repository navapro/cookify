import datetime
import random
from mysql.connector import IntegrityError

def create_dummy_users(cursor, conn, n=10):
    """
    Inserts one admin user and n dummy users into Users.
    Returns a dict with admin_id and a list of created user_ids.
    Also creates a hardcoded User 2 (TestChef) for consistent testing.
    """
    created_ids = {
        'admin_id': None,
        'user_ids': [],
        'test_chef_id': None
    }

    # 1) Create admin user
    try:
        cursor.execute(
            """
            INSERT INTO Users (User_ID, Name, Email, Password, Date_of_Birth, Cookify_Level, Points, Profile_Image)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                Name = VALUES(Name),
                Email = VALUES(Email),
                Password = VALUES(Password),
                Date_of_Birth = VALUES(Date_of_Birth),
                Cookify_Level = VALUES(Cookify_Level),
                Points = VALUES(Points),
                Profile_Image = VALUES(Profile_Image)
            """,
            (
                1,  # Explicit User_ID = 1
                'admin',
                'admin@example.com',
                'adminpassword',  # override in production
                datetime.date(1990, 1, 1),
                'Michelin Star Chef',  # highest level for admin,
                100000,
                "USER_IMAGE_ADMIN"
            )
        )
        conn.commit()
        created_ids['admin_id'] = 1
        print(f"Created/updated admin user with ID=1")
    except Exception as e:
        print(f"Error setting up admin user: {e}")
        # If error, fetch existing ID
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
    
    # 2) Create hardcoded User 2 (TestChef) for consistent testing
    try:
        cursor.execute(
            """
            INSERT INTO Users (User_ID, Name, Email, Password, Date_of_Birth, Cookify_Level, Points, Profile_Image)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                Name = VALUES(Name),
                Email = VALUES(Email),
                Password = VALUES(Password),
                Date_of_Birth = VALUES(Date_of_Birth),
                Cookify_Level = VALUES(Cookify_Level),
                Points = VALUES(Points),
                Profile_Image = VALUES(Profile_Image)
            """,
            (
                2,  # Explicit User_ID = 2
                "TestChef", 
                "testchef@example.com", 
                "test123", 
                datetime.date(1990, 1, 1),
                "Chef",
                150,
                "chef"
            )
        )
        conn.commit()
        created_ids['test_chef_id'] = 2
        created_ids['user_ids'].append(2)  # Add TestChef to the user_ids list
        print(f"Created/updated TestChef user with ID=2")
    except Exception as e:
        print(f"Error setting up TestChef user: {e}")
        # If error, fetch existing ID
        cursor.execute(
            "SELECT User_ID FROM Users WHERE Email=%s",
            ('testchef@example.com',)
        )
        row = cursor.fetchone()
        if row:
            created_ids['test_chef_id'] = row[0]
            if row[0] not in created_ids['user_ids']:
                created_ids['user_ids'].append(row[0])
            print(f"TestChef already exists with ID={created_ids['test_chef_id']}")

    # 3) Create n additional dummy users
    for i in range(1, n+1):
        # Start user IDs from 3 to avoid conflicting with admin (1) and TestChef (2)
        user_id = i + 2
        name = f"User{i}"
        email = f"user{i}@example.com"
        password = f"password{i}"
        year  = random.randint(1950, 2000)
        month = random.randint(1, 12)
        day   = random.randint(1, 28)
        dob   = datetime.date(year, month, day)
        points = random.randint(5, 50)
        level = 'Street Rat'  # Default for low points
        if points >= 10:
            level = 'Dishwasher'
        if points >= 25: 
            level = 'Prep Cook'  
        img = f"USER_IMAGE_{i}"

        try:
            cursor.execute(
                """
                INSERT INTO Users (User_ID, Name, Email, Password, Date_of_Birth, Cookify_Level, Points, Profile_Image)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    Name = VALUES(Name),
                    Email = VALUES(Email),
                    Password = VALUES(Password),
                    Date_of_Birth = VALUES(Date_of_Birth),
                    Cookify_Level = VALUES(Cookify_Level),
                    Points = VALUES(Points),
                    Profile_Image = VALUES(Profile_Image)
                """,
                (user_id, name, email, password, dob, level, points, img)
            )
            conn.commit()
            created_ids['user_ids'].append(user_id)
            print(f"Inserted/updated dummy user '{name}' with ID={user_id}")
        except Exception as e:
            print(f"Error setting up user {name}: {e}")
            # Try to fetch existing ID
            cursor.execute(
                "SELECT User_ID FROM Users WHERE Email=%s",
                (email,)
            )
            row = cursor.fetchone()
            if row:
                uid = row[0]
                if uid not in created_ids['user_ids']:
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

def create_dummy_cooklist_recipes(cursor, conn, cooklist_ids, recipe_ids, user_ids, max_recipes_per_list=5):
    """
    For each cooklist, add 1–`max_recipes_per_list` random recipes.
    Each entry gets a random Added_At datetime within the last 90 days.
    """
    # Find cooklist owners for permissions
    cursor.execute("SELECT CookList_ID, User_ID FROM CookLists")
    owners = {cid: uid for cid, uid in cursor}
    
    # Add owners as editors for their cooklists
    # for cl_id, user_id in owners.items():
    #     try:
    #         cursor.execute(
    #             "INSERT IGNORE INTO Cooklist_Editors (CookList_ID, User_ID) VALUES (%s, %s)",
    #             (cl_id, user_id)
    #         )
    #     except Exception as e:
    #         print(f"Error adding owner as editor: {e}")
    # conn.commit()
    
    for cl in cooklist_ids:
        n = random.randint(1, min(max_recipes_per_list, len(recipe_ids)))
        picks = random.sample(recipe_ids, n)
        for r in picks:
            # Generate a random datetime within the last 90 days
            days_ago = random.randint(0, 90)
            seconds_ago = random.randint(0, 86400)
            added_at = datetime.datetime.now() - datetime.timedelta(days=days_ago, seconds=seconds_ago)
            
            # Use the cooklist owner as the Added_By user
            added_by = owners.get(cl, user_ids[0])
            
            try:
                cursor.execute(
                    "INSERT INTO CookList_Recipes (CookList_ID, Recipe_ID, Added_At, Added_By) VALUES (%s, %s, %s, %s)",
                    (cl, r, added_at, added_by)
                )
            except IntegrityError:
                pass
    conn.commit()
    print("Populated CookList_Recipes.")

def create_dummy_recipe_likes(cursor, conn, user_ids, recipe_ids, like_probability=0.2):
    """
    For each user–recipe pair, like with probability `like_probability`.
    """
    success_count = 0
    error_count = 0
    
    # First make sure each user has a Liked Recipes cooklist
    print("Setting up Liked Recipes cooklists...")
    cooklist_map = {}  # Store user_id -> cooklist_id mapping
    
    for u in user_ids:
        try:
            # Create Liked Recipes cooklist if it doesn't exist
            cursor.execute(
                "SELECT COUNT(*) FROM CookLists WHERE User_ID = %s AND Name = 'Liked Recipes'",
                (u,)
            )
            count = cursor.fetchone()[0]
            
            if count == 0:
                cursor.execute(
                    "INSERT INTO CookLists (User_ID, Name, Description, Is_Public) VALUES (%s, %s, %s, %s)",
                    (u, 'Liked Recipes', 'All your liked recipes in one place!', True)
                )
                conn.commit()
                
            # Get the cooklist ID
            cursor.execute(
                "SELECT CookList_ID FROM CookLists WHERE User_ID = %s AND Name = 'Liked Recipes'",
                (u,)
            )
            result = cursor.fetchone()
            
            if result:
                cooklist_id = result[0]
                cooklist_map[u] = cooklist_id
                
                # Make sure user is an editor
                cursor.execute(
                    "SELECT COUNT(*) FROM Cooklist_Editors WHERE CookList_ID = %s AND User_ID = %s",
                    (cooklist_id, u)
                )
                if cursor.fetchone()[0] == 0:
                    cursor.execute(
                        "INSERT INTO Cooklist_Editors (CookList_ID, User_ID) VALUES (%s, %s)",
                        (cooklist_id, u)
                    )
                    conn.commit()
            else:
                print(f"Warning: Failed to find 'Liked Recipes' cooklist for user {u}")
        except Exception as e:
            print(f"Error creating Liked Recipes cooklist for user {u}: {e}")
            conn.rollback()
    
    # Add likes for each user
    print("Adding recipe likes...")
    for u in user_ids:
        # Get the user's Liked Recipes cooklist ID
        cooklist_id = cooklist_map.get(u)
        
        # Skip if no cooklist found
        if not cooklist_id:
            continue
        
        # For each recipe they might like
        for r in recipe_ids:
            if random.random() < like_probability:
                try:
                    # Skip if already liked
                    cursor.execute(
                        "SELECT COUNT(*) FROM Recipe_Likes WHERE User_ID = %s AND Recipe_ID = %s",
                        (u, r)
                    )
                    if cursor.fetchone()[0] > 0:
                        continue
                    
                    # Insert the like directly
                    cursor.execute(
                        "INSERT INTO Recipe_Likes (User_ID, Recipe_ID) VALUES (%s, %s)",
                        (u, r)
                    )
                    
                    # Manually insert into cooklist recipes
                    cursor.execute(
                        "INSERT IGNORE INTO CookList_Recipes (CookList_ID, Recipe_ID, Added_At, Added_By) VALUES (%s, %s, CURRENT_TIMESTAMP, %s)",
                        (cooklist_id, r, u)
                    )
                    
                    conn.commit()
                    success_count += 1
                    
                except Exception as e:
                    error_count += 1
                    print(f"Error adding like for user {u}, recipe {r}: {str(e)}")
                    conn.rollback()
    
    print(f"Populated Recipe_Likes. Success: {success_count}, Errors: {error_count}")

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
