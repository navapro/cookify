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

# def setup_user2_test_data(cursor, conn, recipe_ids):
#     """
#     Create comprehensive test data for User 2 (TestChef)
#     This function assumes User 2 already exists (created by create_dummy_users)
#     """
#     print("Setting up User 2 (TestChef) with comprehensive test data...")
#     USER_ID = 2
    
#     # User 2 already created in create_dummy_users, so we skip that step
#     try:
#         # Check if "Liked Recipes" cooklist exists
#         cursor.execute("""
#             SELECT CookList_ID FROM CookLists 
#             WHERE User_ID = %s AND Name = 'Liked Recipes'
#         """, (USER_ID,))
        
#         liked_list = cursor.fetchone()
#         if not liked_list:
#             # Create the Liked Recipes cooklist if it doesn't exist
#             cursor.execute("""
#                 INSERT INTO CookLists (User_ID, Name, Description, Is_Public)
#                 VALUES (%s, %s, %s, %s)
#             """, (USER_ID, "Liked Recipes", "All your liked recipes in one place!", True))
#             conn.commit()
            
#             # Get the cooklist ID
#             cursor.execute("""
#                 SELECT CookList_ID FROM CookLists 
#                 WHERE User_ID = %s AND Name = 'Liked Recipes'
#             """, (USER_ID,))
#             liked_list = cursor.fetchone()
        
#         # Add User 2 as an editor of their own Liked Recipes cooklist
#         if liked_list:
#             cursor.execute("""
#                 INSERT IGNORE INTO Cooklist_Editors (CookList_ID, User_ID)
#                 VALUES (%s, %s)
#             """, (liked_list[0], USER_ID))
#             conn.commit()
#             print(f"Ensured User 2 has a 'Liked Recipes' cooklist with ID {liked_list[0]}")
#     except Exception as e:
#         print(f"Error setting up Liked Recipes cooklist for User 2: {e}")
#         conn.rollback()
    
#     # 2. Create specific ingredients for User 2
#     ingredients = [
#         (1, "Chicken", 500),
#         (2, "Onion", 5),
#         (3, "Garlic", 10),
#         (4, "Rice", 1000),
#         (5, "Tomato", 8),
#         (10, "Olive Oil", 250),
#         (15, "Salt", 100),
#         (20, "Pepper", 50)
#     ]
    
#     for ing_id, ing_name, quantity in ingredients:
#         try:
#             # Make sure ingredient exists
#             cursor.execute("""
#                 INSERT INTO Ingredients (Ingredient_ID, Name) 
#                 VALUES (%s, %s)
#                 ON DUPLICATE KEY UPDATE Name = VALUES(Name)
#             """, (ing_id, ing_name))
            
#             # Add to user's ingredients
#             cursor.execute("""
#                 INSERT INTO User_Ingredients (User_ID, Ingredient_ID, Quantity)
#                 VALUES (%s, %s, %s)
#                 ON DUPLICATE KEY UPDATE Quantity = VALUES(Quantity)
#             """, (USER_ID, ing_id, quantity))
#         except Exception as e:
#             print(f"Error adding ingredient {ing_name} to User 2: {e}")
#             conn.rollback()
#     conn.commit()
#     print("Added specific ingredients to User 2")
    
#     # 3. Create specific cooklists for User 2
#     cooklists = [
#         ("Weekly Menu", "My meal plan for this week", True),
#         ("Special Occasions", "Recipes for birthdays and holidays", True),
#         ("Quick Meals", "When I need something fast", False)
#     ]
    
#     cooklist_ids = []
#     for name, desc, is_public in cooklists:
#         try:
#             cursor.execute("""
#                 INSERT INTO CookLists (User_ID, Name, Description, Is_Public)
#                 VALUES (%s, %s, %s, %s)
#             """, (USER_ID, name, desc, is_public))
#             conn.commit()
#             cooklist_ids.append(cursor.lastrowid)
#         except Exception as e:
#             print(f"Error creating cooklist {name} for User 2: {e}")
#             conn.rollback()
#     print(f"Created {len(cooklist_ids)} specific cooklists for User 2")
    
#     # 4. Add specific recipes to User 2's cooklists
#     if len(recipe_ids) >= 10:
#         # Add specific recipes to each cooklist
#         recipe_assignments = [
#             (cooklist_ids[0], recipe_ids[:5]),  # First 5 recipes to Weekly Menu
#             (cooklist_ids[1], recipe_ids[5:8]), # 3 recipes to Special Occasions
#             (cooklist_ids[2], recipe_ids[8:10]) # 2 recipes to Quick Meals
#         ]
        
#         for cl_id, recipes in recipe_assignments:
#             for i, r_id in enumerate(recipes):
#                 # Spread the added_at dates over the last 30 days
#                 days_ago = i * 3  # 0, 3, 6, 9, 12 days ago
#                 added_at = datetime.datetime.now() - datetime.timedelta(days=days_ago)
#                 try:
#                     cursor.execute("""
#                         INSERT INTO CookList_Recipes (CookList_ID, Recipe_ID, Added_At, Added_By)
#                         VALUES (%s, %s, %s, %s)
#                     """, (cl_id, r_id, added_at, USER_ID))
#                 except Exception as e:
#                     print(f"Error adding recipe {r_id} to cooklist {cl_id} for User 2: {e}")
#                     conn.rollback()
#         conn.commit()
#         print("Added specific recipes to User 2's cooklists")
    
#     # 5. Like specific recipes
#     if len(recipe_ids) >= 15:
#         likes = recipe_ids[10:15]  # Like 5 different recipes
#         for r_id in likes:
#             try:
#                 cursor.execute("""
#                     INSERT INTO Recipe_Likes (User_ID, Recipe_ID)
#                     VALUES (%s, %s)
#                 """, (USER_ID, r_id))
#             except Exception as e:
#                 print(f"Error adding recipe like for User 2: {e}")
#                 conn.rollback()
#         conn.commit()
#         print("Added specific recipe likes for User 2")
    
#     # 6. Set up cooklist sharing permissions
#     if len(cooklist_ids) > 0:
#         # Share the "Weekly Menu" cooklist with users 3 and 4 if they exist
#         for shared_user in [3, 4]:
#             try:
#                 cursor.execute("""
#                     INSERT IGNORE INTO Cooklist_Editors (CookList_ID, User_ID)
#                     VALUES (%s, %s)
#                 """, (cooklist_ids[0], shared_user))
#             except Exception as e:
#                 print(f"Error setting up sharing for User 2's cooklist: {e}")
#                 conn.rollback()
#         conn.commit()
#         print("Set up cooklist sharing permissions for User 2")
    
#     print("User 2 test data setup complete!")
