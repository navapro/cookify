from flask import Blueprint, jsonify, request
from extensions import db
from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash

users_bp = Blueprint('users', __name__)

@users_bp.route('/', methods=['GET'])
def get_all_users():
    try:
        result = db.session.execute(text("SELECT User_ID, Name, Email, Cookify_Level FROM Users"))
        users = [{"id": row[0], "name": row[1], "email": row[2], "level": row[3]} for row in result]
        return jsonify({"users": users})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        result = db.session.execute(
            text("SELECT User_ID, Name, Email, Cookify_Level FROM Users WHERE User_ID = :id"),
            {"id": user_id}
        )
        user = result.fetchone()
        if user:
            return jsonify({
                "id": user[0],
                "name": user[1],
                "email": user[2],
                "level": user[3]
            })
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_bp.route('/', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No input data provided"}), 400

        name = data.get('name')
        email = data.get('email')
        password = data.get('password') # Get password from request
        cookify_level = data.get('cookify_level', 1) # Default to 1 if not provided

        if not name or not email or not password: # Password is now required
            return jsonify({"error": "Name, email, and password are required"}), 400

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Check if email already exists
        email_check = db.session.execute(
            text("SELECT User_ID FROM Users WHERE Email = :email"),
            {"email": email}
        ).fetchone()

        if email_check:
            return jsonify({"error": "Email already exists"}), 409 # Conflict

        # Insert new user into the database, including the hashed password
        result = db.session.execute(
            text("INSERT INTO Users (Name, Email, Password, Cookify_Level) VALUES (:name, :email, :password, :cookify_level)"),
            {"name": name, "email": email, "password": hashed_password, "cookify_level": cookify_level}
        )
        db.session.commit()

        new_user_id = result.lastrowid
        return jsonify({"message": "User created successfully", "id": new_user_id}), 201 # Created
    except Exception as e:
        db.session.rollback() # Rollback in case of error
        return jsonify({"error": str(e)}), 500

@users_bp.route('/login', methods=['POST'])
def login_user():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No input data provided"}), 400

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        # Fetch user from database by email
        result = db.session.execute(
            text("SELECT User_ID, Name, Email, Password FROM Users WHERE Email = :email"),
            {"email": email}
        )
        user = result.fetchone()

        if not user:
            return jsonify({"error": "Invalid credentials"}), 401 # Unauthorized

        hashed_password_from_db = user[3] # Assuming Password is the 4th column (index 3)

        if check_password_hash(hashed_password_from_db, password):
            # Login successful, return user info (excluding password hash)
            return jsonify({"message": "Login successful", "user": {"id": user[0], "name": user[1], "email": user[2]}}), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401 # Unauthorized

    except Exception as e:
        return jsonify({"error": str(e)}), 500 