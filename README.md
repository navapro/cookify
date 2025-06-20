# Cookify 🍳

A full-stack web application for recipe management with user profiles, cooklists, and a gamified leveling system.

## Set Up
Ensure you have the following installed on your system:
*   [Node.js](https://nodejs.org/) (which includes npm)
*   [Python 3](https://www.python.org/)
*   [MySQL Server](https://dev.mysql.com/downloads/mysql/)

### Setup 
This application requires a MySQL database named `cookify`. Follow these steps to create and configure it.

**1. Log into MySQL**

First, open your terminal and log into the MySQL command-line client as the root user.

```bash
mysql -u root -p
```
You will be prompted to enter the password you set for the MySQL root user during its installation.

**2. Create the Database**

Inside the MySQL monitor, run the following SQL command to create the database. The `IF NOT EXISTS` clause prevents errors if you run it more than once.

```sql
CREATE DATABASE IF NOT EXISTS cookify;
```
**3. Configure Environment Variables**

In the `backend` directory, create a file named `.env`. This file stores the credentials your Flask application will use to connect to the database. Update MYSQL_PASSWORD accordingly.

```dotenv
# filepath: backend/.env
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DB=cookify
```

Your database is now set up and ready for the application.

### Launch the Application
Option 1: In one terminal, launch the react app:
```bash
cd frontend
npm install
npm run dev
```
In one terminal, launch the flask app:
```bash
cd backend
# Optional: Create and activate a Python virtual environment
python3 -m venv venv
source venv/bin/activate  # or on Windows, use: venv\Scripts\activate
# Install required Python packages
pip install -r requirements.txt
# Run the Flask application
python wsgi.py
```

Option 2:
```bash
./launch_app
```
This script starts both the frontend (React) and backend (Flask) servers.

The backend will be running at `http://localhost:5001`.

The frontend will be running at `http://localhost:5173`.

## Milestone 1 Features: C2 + C3
Option 1:

cd into the sql folder if you haven't already. Then run this bash script in a terminal that support linux/unix commands:
```bash
cd sql
./reset-and-test.sh
```

Option 2:

**C2: Populate the Database**

From your regular terminal (not the MySQL monitor), navigate to the project's root directory. Run the following command to execute the master schema file. This will create all the necessary tables and insert the sample data.

```bash
mysql -u root -p cookify < create_tables.sql
```
(If this doesn't work, cd into sql folder and run: mysql -u root -p cookify < create_and_update_recipes.sql)

You will be prompted to enter the password for the root user.

**C3: Run test-sample.sql Script**

This script resets the database, creates tables, and runs test queries for user profile creation.

If it fails, you can manually run the sql script:
```bash
mysql -u root -p cookify < test-sample.sql
```

## Technologies Used

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **React Router** - Navigation
- **Lucide React** - Icons
- **Shadcn/ui** - Component library

### Backend
- **Flask** - Python web framework
- **SQLAlchemy** - Database ORM
- **MySQL** - Database
- **JWT** - Authentication
- **Werkzeug** - Password hashing

### Database
- **MySQL 8.0** - DBSM

### Development Tools
- **Git** - Version control
- **Shell Scripts** - Database management and app launching 
