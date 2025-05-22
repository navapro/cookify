
Recipe Curation Platform - "Hello World" Database Setup & Application
=======================================================================
This document describes how to create a sample MySQL database and run a simple
Python application to interact with it. This serves as a basic test to ensure
your development environment is correctly configured for the project.

Our project is a personalized platform that curates recipes the way Spotify
curates music. This toy example will use a single table called 'Recipes'.

--------------------------------------------------------------------------------
I. Prerequisites
--------------------------------------------------------------------------------

1.  **MySQL Server:** Ensure you have MySQL Server installed and running.
    You can download it from: https://dev.mysql.com/downloads/mysql/
    During installation, take note of your root password or create a dedicated
    user for this project.

2.  **Python 3:** Ensure Python 3 (preferably 3.7+) is installed.
    You can download it from: https://www.python.org/downloads/

3.  **MySQL Connector for Python:** This library allows Python to communicate
    with MySQL. Install it using pip:
    pip install mysql-connector-python

--------------------------------------------------------------------------------
II. Database Setup (Using MySQL Command Line or a GUI like MySQL Workbench)
--------------------------------------------------------------------------------

1.  **Connect to MySQL Server:**
    Open your MySQL command-line client or GUI tool.
    If using the command line, you might connect as root (replace 'your_root_password'
    with your actual root password):
    mysql -u root -p

2.  **Create the Database:**
    Execute the following SQL command:
    CREATE DATABASE recipe_app_db;

3.  **Create a Dedicated User (Recommended):**
    It's good practice to create a specific user for your application rather
    than using the root user. Replace 'your_app_password' with a strong password.

    CREATE USER 'recipe_user'@'localhost' IDENTIFIED BY 'your_app_password';
    GRANT ALL PRIVILEGES ON recipe_app_db.* TO 'recipe_user'@'localhost';
    FLUSH PRIVILEGES;

    If you skip this step, you'll need to use your root credentials in the
    Python script, which is not recommended for production.

4.  **Select the Database:**
    USE recipe_app_db;

5.  **Create the Sample Table (`Recipes`):**
    Execute the following SQL command:

    CREATE TABLE Recipes (
        recipe_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        prep_time_minutes INT,
        cuisine_type VARCHAR(100),
        difficulty VARCHAR(50)
    );

6.  **Insert Sample Data into the `Recipes` Table:**
    Execute the following SQL commands:

    INSERT INTO Recipes (name, description, prep_time_minutes, cuisine_type, difficulty) VALUES
    ('Spaghetti Carbonara', 'A classic Italian pasta dish made with eggs, cheese, pancetta, and pepper.', 30, 'Italian', 'Easy'),
    ('Chicken Stir-Fry', 'Quick and healthy chicken and vegetable stir-fry.', 25, 'Asian', 'Medium'),
    ('Chocolate Chip Cookies', 'The best homemade soft and chewy chocolate chip cookies.', 45, 'Dessert', 'Easy'),
    ('Beef Tacos', 'Flavorful ground beef tacos with your favorite toppings.', 20, 'Mexican', 'Easy'),
    ('Vegetable Curry', 'Aromatic and creamy vegetable curry with coconut milk.', 40, 'Indian', 'Medium');

7.  **Verify Data Insertion (Optional):**
    SELECT * FROM Recipes;

    You should see the 5 rows you just inserted.

8.  **Exit MySQL client (if using command line):**
    EXIT;

--------------------------------------------------------------------------------
III. Python Application Setup & Execution
--------------------------------------------------------------------------------

1.  **Save the Python Code:**
    Save the Python script provided (e.g., `app.py`) in a directory on your
    machine or school server.

2.  **Configure Database Credentials in `app.py`:**
    Open `app.py` in a text editor.
    Locate the `db_config` dictionary:
    db_config = {
        'host': 'localhost',
        'user': 'recipe_user',        # Or 'root' if you skipped user creation
        'password': 'your_app_password', # Or your root password
        'database': 'recipe_app_db'
    }
    Update the 'user' and 'password' fields to match the credentials you set up
    in Step II.3 (or your root credentials if you didn't create a new user).

3.  **Run the Python Application:**
    Open a terminal or command prompt, navigate to the directory where you
    saved `app.py`, and run:
    python app.py

--------------------------------------------------------------------------------
IV. Expected Output
--------------------------------------------------------------------------------

The Python script will attempt to connect to the database, select all recipes,
and then select only 'Easy' difficulty recipes. The output should look
something like this:

    Successfully connected to the database: recipe_app_db
    --- All Recipes ---
    Recipe ID: 1, Name: Spaghetti Carbonara, Cuisine: Italian, Difficulty: Easy
    Recipe ID: 2, Name: Chicken Stir-Fry, Cuisine: Asian, Difficulty: Medium
    Recipe ID: 3, Name: Chocolate Chip Cookies, Cuisine: Dessert, Difficulty: Easy
    Recipe ID: 4, Name: Beef Tacos, Cuisine: Mexican, Difficulty: Easy
    Recipe ID: 5, Name: Vegetable Curry, Cuisine: Indian, Difficulty: Medium

    --- Easy Recipes ---
    Recipe ID: 1, Name: Spaghetti Carbonara, Cuisine: Italian, Difficulty: Easy
    Recipe ID: 3, Name: Chocolate Chip Cookies, Cuisine: Dessert, Difficulty: Easy
    Recipe ID: 4, Name: Beef Tacos, Cuisine: Mexican, Difficulty: Easy

    Database connection closed.

If you see an error, double-check your MySQL server status, database/table
creation steps, user credentials, and Python script configuration.
The error message should provide clues as to what went wrong.
================================================================================
