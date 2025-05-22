import mysql.connector
from mysql.connector import Error

# --- Database Configuration ---
# IMPORTANT: Replace with your actual database credentials.
# If you created 'recipe_user' as per README, use those credentials.
# Otherwise, you might use 'root' and your MySQL root password (not recommended for long term).
db_config = {
    "host": "localhost",
    "user": "recipe_user", # or 'root'
    "password": "your_app_password", # or your root password
    "database": "recipe_app_db",
}


def connect_to_database():
    """Establishes a connection to the MySQL database."""
    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
        if conn.is_connected():
            print(
                f"Successfully connected to the database: {db_config['database']}"
            )
            return conn
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None


def fetch_all_recipes(conn):
    """Fetches all recipes from the Recipes table."""
    if not conn or not conn.is_connected():
        print("No active database connection.")
        return []

    cursor = None
    try:
        cursor = conn.cursor()
        query = "SELECT recipe_id, name, cuisine_type, difficulty FROM Recipes;"
        cursor.execute(query)
        records = cursor.fetchall()
        return records
    except Error as e:
        print(f"Error fetching all recipes: {e}")
        return []
    finally:
        if cursor:
            cursor.close()


def fetch_recipes_by_difficulty(conn, difficulty_level):
    """Fetches recipes from the Recipes table by a specific difficulty."""
    if not conn or not conn.is_connected():
        print("No active database connection.")
        return []

    cursor = None
    try:
        cursor = conn.cursor()
        query = """
            SELECT recipe_id, name, cuisine_type, difficulty
            FROM Recipes
            WHERE difficulty = %s;
        """
        cursor.execute(query, (difficulty_level,)) # Note the tuple for params
        records = cursor.fetchall()
        return records
    except Error as e:
        print(f"Error fetching recipes by difficulty '{difficulty_level}': {e}")
        return []
    finally:
        if cursor:
            cursor.close()


def main():
    """Main function to demonstrate database interaction."""
    conn = connect_to_database()

    if conn and conn.is_connected():
        # 1. Select all rows from the table
        print("\n--- All Recipes ---")
        all_recipes = fetch_all_recipes(conn)
        if all_recipes:
            for row in all_recipes:
                # row[0] is recipe_id, row[1] is name, etc.
                print(
                    f"Recipe ID: {row[0]}, Name: {row[1]}, Cuisine: {row[2]}, Difficulty: {row[3]}"
                )
        else:
            print("No recipes found or error occurred.")

        # 2. Select some rows based on a condition
        print("\n--- Easy Recipes ---")
        easy_recipes = fetch_recipes_by_difficulty(conn, "Easy")
        if easy_recipes:
            for row in easy_recipes:
                print(
                    f"Recipe ID: {row[0]}, Name: {row[1]}, Cuisine: {row[2]}, Difficulty: {row[3]}"
                )
        else:
            print("No 'Easy' recipes found or error occurred.")

        # Close the database connection
        try:
            conn.close()
            print("\nDatabase connection closed.")
        except Error as e:
            print(f"Error closing connection: {e}")


if __name__ == "__main__":
    main()
