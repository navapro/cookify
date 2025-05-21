
README.txt - Sample MySQL Database Setup
============================================

This document describes how to create and populate a sample MySQL database
named `sample_company_db` with a single table called `employees`.

--------------------------------------------------------------------------------
Prerequisites
--------------------------------------------------------------------------------

1.  **MySQL Server Installed:** You need a running MySQL server instance.
    (e.g., MySQL Community Server, MariaDB).
2.  **MySQL Client:** You need a way to connect to the MySQL server and execute
    SQL commands. This can be:
    *   The `mysql` command-line client.
    *   A GUI tool like MySQL Workbench, DBeaver, phpMyAdmin, etc.
3.  **Permissions:** You need a MySQL user with privileges to create databases
    and tables (e.g., the `root` user or a user with `CREATE DATABASE` and
    `CREATE TABLE` privileges).

--------------------------------------------------------------------------------
Steps to Create and Load the Database
--------------------------------------------------------------------------------

You can execute the following SQL commands using your chosen MySQL client.

**Method 1: Using the `mysql` Command-Line Client**

1.  **Connect to MySQL Server:**
    Open your terminal or command prompt and connect to MySQL. You might be
    prompted for your MySQL user's password.

    ```bash
    mysql -u <your_username> -p
    ```
    Replace `<your_username>` with your MySQL username (e.g., `root`).

2.  **Execute SQL Commands:**
    Once connected, you can copy and paste the SQL commands below directly into
    the `mysql>` prompt.

**Method 2: Using a GUI Tool (e.g., MySQL Workbench, DBeaver)**

1.  **Connect to your MySQL Server** using the tool's connection manager.
2.  **Open a new SQL editor/query window.**
3.  **Copy and paste the SQL commands below** into the editor and execute them.
    Most tools allow you to execute the entire script at once or statement by
    statement.

---
**SQL Commands:**
---

```sql
-- -----------------------------------------------------------------------------
-- Step 1: Create the Database
-- -----------------------------------------------------------------------------
-- It's good practice to check if the database already exists before creating it.
-- The `IF NOT EXISTS` clause prevents an error if it already exists.

CREATE DATABASE IF NOT EXISTS sample_company_db;

-- -----------------------------------------------------------------------------
-- Step 2: Select the Database to Use
-- -----------------------------------------------------------------------------
-- All subsequent commands will be executed in the context of this database.

USE sample_company_db;

-- -----------------------------------------------------------------------------
-- Step 3: Create the 'employees' Table
-- -----------------------------------------------------------------------------
-- This defines the schema for our sample table.

CREATE TABLE IF NOT EXISTS employees (
    employee_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    hire_date DATE,
    department VARCHAR(50),
    salary DECIMAL(10, 2)
);

-- -----------------------------------------------------------------------------
-- Step 4: Insert Sample Data into the 'employees' Table
-- -----------------------------------------------------------------------------
-- This populates the table with a few records.

INSERT INTO employees (first_name, last_name, email, hire_date, department, salary) VALUES
('Alice', 'Smith', 'alice.smith@example.com', '2022-03-15', 'Engineering', 75000.00),
('Bob', 'Johnson', 'bob.johnson@example.com', '2021-07-01', 'Marketing', 68000.00),
('Carol', 'Williams', 'carol.w@example.com', '2023-01-20', 'Sales', 72000.00),
('David', 'Brown', 'david.brown@example.com', '2022-09-10', 'Engineering', 82000.00),
('Eve', 'Davis', 'eve.davis@example.com', '2023-05-05', 'Human Resources', 60000.00);

-- -----------------------------------------------------------------------------
-- Step 5: Verify the Data (Optional but Recommended)
-- -----------------------------------------------------------------------------
-- This command will display all records from the 'employees' table.

SELECT * FROM employees;

-- You can also check the table structure:
-- DESCRIBE employees;
