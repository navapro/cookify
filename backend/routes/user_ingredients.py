from flask import Blueprint, jsonify, request
from extensions import db
from sqlalchemy import text
from flask_jwt_extended import jwt_required, get_jwt_identity

user_ingredients_bp = Blueprint('user_ingredients', __name__)

@user_ingredients_bp.route('/<int:user_id>/ingredients', methods=['GET'])
@jwt_required()
def get_user_ingredients(user_id):
    current_user_id = int(get_jwt_identity())
    if current_user_id != user_id:
        return jsonify({"error": "Unauthorized access"}), 403

    try:
        result = db.session.execute(
            text("""
                SELECT ui.User_ID, ui.Ingredient_ID, i.Name, ui.Quantity
                FROM User_Ingredients ui
                JOIN Ingredients i ON ui.Ingredient_ID = i.Ingredient_ID
                WHERE ui.User_ID = :user_id
                ORDER BY i.Name
            """),
            {"user_id": current_user_id}
        )
        
        ingredients = []
        for row in result:
            ingredients.append({
                "user_id": row[0],
                "ingredient_id": row[1],
                "name": row[2],
                "quantity": row[3],
                "category": "",  # Empty default value
                "season": "",    # Empty default value
                "price": None    # Null default value
            })
        
        return jsonify({"ingredients": ingredients})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_ingredients_bp.route('/<int:user_id>/ingredients', methods=['POST'])
@jwt_required()
def add_user_ingredient(user_id):
    current_user_id = int(get_jwt_identity())
    if current_user_id != user_id:
        return jsonify({"error": "Unauthorized access"}), 403

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No input data provided"}), 400

        ingredient_name = data.get('name', '').strip()
        quantity = data.get('quantity', '').strip()
        category = data.get('category', '').strip()
        
        if not ingredient_name or not quantity:
            return jsonify({"error": "Ingredient name and quantity are required"}), 400

        # First check if ingredient exists in the database
        existing_ingredient = db.session.execute(
            text("SELECT Ingredient_ID FROM Ingredients WHERE Name = :name"),
            {"name": ingredient_name}
        ).fetchone()

        if existing_ingredient:
            ingredient_id = existing_ingredient[0]
        else:
            # Create new ingredient if it doesn't exist
            result = db.session.execute(
                text("INSERT INTO Ingredients (Name, Category) VALUES (:name, :category)"),
                {"name": ingredient_name, "category": category or 'Other'}
            )
            db.session.commit()
            ingredient_id = result.lastrowid

        # Check if user already has this ingredient
        user_has_ingredient = db.session.execute(
            text("SELECT User_ID FROM User_Ingredients WHERE User_ID = :user_id AND Ingredient_ID = :ingredient_id"),
            {"user_id": current_user_id, "ingredient_id": ingredient_id}
        ).fetchone()

        if user_has_ingredient:
            # Update quantity if user already has it
            db.session.execute(
                text("UPDATE User_Ingredients SET Quantity = :quantity WHERE User_ID = :user_id AND Ingredient_ID = :ingredient_id"),
                {"user_id": current_user_id, "ingredient_id": ingredient_id, "quantity": quantity}
            )
        else:
            # Add new user ingredient
            db.session.execute(
                text("INSERT INTO User_Ingredients (User_ID, Ingredient_ID, Quantity) VALUES (:user_id, :ingredient_id, :quantity)"),
                {"user_id": current_user_id, "ingredient_id": ingredient_id, "quantity": quantity}
            )
        
        db.session.commit()

        return jsonify({
            "message": "Ingredient added to pantry successfully",
            "ingredient": {
                "ingredient_id": ingredient_id,
                "name": ingredient_name,
                "quantity": quantity,
                "category": category or 'Other'
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@user_ingredients_bp.route('/<int:user_id>/ingredients/<int:ingredient_id>', methods=['PUT'])
@jwt_required()
def update_user_ingredient(user_id, ingredient_id):
    current_user_id = int(get_jwt_identity())
    if current_user_id != user_id:
        return jsonify({"error": "Unauthorized access"}), 403

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No input data provided"}), 400

        quantity = data.get('quantity')
        if not quantity:
            return jsonify({"error": "Quantity is required"}), 400

        # Check if user has this ingredient
        existing_check = db.session.execute(
            text("SELECT User_ID FROM User_Ingredients WHERE User_ID = :user_id AND Ingredient_ID = :ingredient_id"),
            {"user_id": current_user_id, "ingredient_id": ingredient_id}
        ).fetchone()

        if not existing_check:
            return jsonify({"error": "User does not have this ingredient in pantry"}), 404

        # Update the quantity
        db.session.execute(
            text("UPDATE User_Ingredients SET Quantity = :quantity WHERE User_ID = :user_id AND Ingredient_ID = :ingredient_id"),
            {"user_id": current_user_id, "ingredient_id": ingredient_id, "quantity": quantity}
        )
        db.session.commit()

        return jsonify({"message": "Ingredient quantity updated successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@user_ingredients_bp.route('/<int:user_id>/ingredients/<int:ingredient_id>', methods=['DELETE'])
@jwt_required()
def remove_user_ingredient(user_id, ingredient_id):
    current_user_id = int(get_jwt_identity())
    if current_user_id != user_id:
        return jsonify({"error": "Unauthorized access"}), 403

    try:
        # Check if user has this ingredient
        existing_check = db.session.execute(
            text("SELECT User_ID FROM User_Ingredients WHERE User_ID = :user_id AND Ingredient_ID = :ingredient_id"),
            {"user_id": current_user_id, "ingredient_id": ingredient_id}
        ).fetchone()

        if not existing_check:
            return jsonify({"error": "User does not have this ingredient in pantry"}), 404

        # Remove the ingredient from user's pantry
        db.session.execute(
            text("DELETE FROM User_Ingredients WHERE User_ID = :user_id AND Ingredient_ID = :ingredient_id"),
            {"user_id": current_user_id, "ingredient_id": ingredient_id}
        )
        db.session.commit()

        return jsonify({"message": "Ingredient removed from pantry successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@user_ingredients_bp.route('/<int:user_id>/ingredients/categories', methods=['GET'])
@jwt_required()
def get_user_ingredients_by_category(user_id):
    current_user_id = int(get_jwt_identity())
    if current_user_id != user_id:
        return jsonify({"error": "Unauthorized access"}), 403

    try:
        result = db.session.execute(
            text("""
                SELECT i.Category, COUNT(*) as count,
                       GROUP_CONCAT(i.Name ORDER BY i.Name SEPARATOR ', ') as ingredients
                FROM User_Ingredients ui
                JOIN Ingredients i ON ui.Ingredient_ID = i.Ingredient_ID
                WHERE ui.User_ID = :user_id
                GROUP BY i.Category
                ORDER BY i.Category
            """),
            {"user_id": current_user_id}
        )
        
        categories = []
        for row in result:
            categories.append({
                "category": row[0],
                "count": row[1],
                "ingredients": row[2].split(', ') if row[2] else []
            })
        
        return jsonify({"categories": categories})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_ingredients_bp.route('/<int:user_id>/ingredients/search', methods=['GET'])
@jwt_required()
def search_user_ingredients(user_id):
    current_user_id = int(get_jwt_identity())
    if current_user_id != user_id:
        return jsonify({"error": "Unauthorized access"}), 403

    try:
        search_term = request.args.get('q', '').strip()
        category = request.args.get('category', '').strip()
        
        if not search_term and not category:
            return jsonify({"error": "Search term or category is required"}), 400

        query = """
            SELECT ui.User_ID, ui.Ingredient_ID, i.Name, ui.Quantity, 
                   i.Category, i.Season, i.Price
            FROM User_Ingredients ui
            JOIN Ingredients i ON ui.Ingredient_ID = i.Ingredient_ID
            WHERE ui.User_ID = :user_id
        """
        params = {"user_id": current_user_id}

        if search_term:
            query += " AND i.Name LIKE :search_term"
            params["search_term"] = f"%{search_term}%"
        
        if category:
            query += " AND i.Category = :category"
            params["category"] = category

        query += " ORDER BY i.Name"

        result = db.session.execute(text(query), params)
        
        ingredients = []
        for row in result:
            ingredients.append({
                "user_id": row[0],
                "ingredient_id": row[1],
                "name": row[2],
                "quantity": row[3],
                "category": row[4],
                "season": row[5],
                "price": float(row[6]) if row[6] else None,
                "added_at": None,
                "updated_at": None
            })
        
        return jsonify({"ingredients": ingredients, "search_term": search_term, "category": category})
    except Exception as e:
        return jsonify({"error": str(e)}), 500