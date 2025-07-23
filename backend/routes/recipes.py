# recipes.py
from flask import Blueprint, jsonify, request
from extensions import db
from sqlalchemy import text
from flask_jwt_extended import jwt_required, get_jwt_identity

recipes_bp = Blueprint('recipes', __name__)

# SQL statements with named params
ADD_RECIPE_SQL = """
INSERT INTO Recipes
    (Name, Duration, Difficulty, Cuisine, Instructions, Image_URL, User_ID)
VALUES
    (:name, :duration, :difficulty, :cuisine, :instructions, :image_url, :user_id);
"""

UPDATE_RECIPE_SQL = """
UPDATE Recipes
SET
    Name         = :name,
    Duration     = :duration,
    Difficulty   = :difficulty,
    Cuisine      = :cuisine,
    Instructions = :instructions,
    Image_URL    = :image_url
WHERE
    Recipe_ID    = :recipe_id;
"""

GET_RECIPES_JOINED_SQL = """
WITH RecipeData AS (
    SELECT r.Recipe_ID, r.Name, r.Duration, r.Difficulty, r.Cuisine,
           r.Instructions,
           i.Name AS Ingredient
    FROM Recipes r
    LEFT JOIN Recipe_Ingredients ri ON r.Recipe_ID = ri.Recipe_ID
    LEFT JOIN Ingredients i ON ri.Ingredient_ID = i.Ingredient_ID
)
SELECT
    rd.Recipe_ID, rd.Name, rd.Duration, rd.Difficulty, rd.Cuisine,
    rd.Instructions,
    GROUP_CONCAT(rd.Ingredient) AS Ingredients
FROM RecipeData rd
GROUP BY rd.Recipe_ID
ORDER BY rd.Name ASC
LIMIT :limit OFFSET :offset;
"""

GET_RECIPE_JOINED_SQL = """
SELECT r.Recipe_ID, r.Name, r.Duration, r.Difficulty, r.Cuisine, r.Instructions,
       GROUP_CONCAT(i.Name) AS Ingredients
FROM Recipes r
LEFT JOIN Recipe_Ingredients ri ON r.Recipe_ID = ri.Recipe_ID
LEFT JOIN Ingredients i ON ri.Ingredient_ID = i.Ingredient_ID
WHERE r.Recipe_ID = :id
GROUP BY r.Recipe_ID;
"""

GET_USER_RECIPES_SQL = """
SELECT r.Recipe_ID, r.Name, r.Duration, r.Difficulty, r.Cuisine, r.Instructions, r.Image_URL,
       GROUP_CONCAT(i.Name) AS Ingredients
FROM Recipes r
LEFT JOIN Recipe_Ingredients ri ON r.Recipe_ID = ri.Recipe_ID
LEFT JOIN Ingredients i ON ri.Ingredient_ID = i.Ingredient_ID
WHERE r.User_ID = :user_id
GROUP BY r.Recipe_ID
ORDER BY r.Recipe_ID DESC;
"""

@recipes_bp.route('/', methods=['GET'])
def get_all_recipes():
    try:
        limit = request.args.get('limit', default=12, type=int)
        offset = request.args.get('offset', default=0, type=int)
        
        # Get total count for pagination
        count_result = db.session.execute(text("SELECT COUNT(*) FROM Recipes"))
        total_recipes = count_result.scalar()
        
        params = {"limit": limit, "offset": offset}
        result = db.session.execute(text(GET_RECIPES_JOINED_SQL), params)
        recipes = []
        for row in result:
            # Format image URL properly
            image_url = row[7] if row[7] else "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?auto=format&fit=crop&w=500&h=300"
            
            recipes.append({
                "id": row[0],
                "name": row[1],
                "duration": row[2],
                "difficulty": row[3],
                "cuisine": row[4],
                "instructions": row[5],
                "ingredients": row[6].split(',') if row[6] else [],
                "image_url": image_url
            })
        
        return jsonify({
            "recipes": recipes,
            "total": total_recipes
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@recipes_bp.route('/<int:recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    try:
        result = db.session.execute(text(GET_RECIPE_JOINED_SQL), {"id": recipe_id})
        recipe = result.fetchone()
        if recipe:
            return jsonify({
                "id": recipe[0],
                "name": recipe[1],
                "duration": recipe[2],
                "difficulty": recipe[3],
                "cuisine": recipe[4],
                "instructions": recipe[5],
                "ingredients": recipe[6].split(',') if recipe[6] else []
            }), 200
        else:
            return jsonify({"error": "Recipe not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@recipes_bp.route('/', methods=['POST'])
@jwt_required()
def add_recipe():
    # Get the current user from JWT token
    current_user_id = int(get_jwt_identity())
    
    data = request.get_json() or {}
    required = ['name', 'duration', 'difficulty', 'cuisine', 'instructions']
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    params = {
        "name": data["name"],
        "duration": data["duration"],
        "difficulty": data["difficulty"],
        "cuisine": data["cuisine"],
        "instructions": data["instructions"],
        "image_url": data.get("image_url"),
        "user_id": current_user_id,
    }
    try:
        result = db.session.execute(text(ADD_RECIPE_SQL), params)
        new_id = getattr(result, 'lastrowid', None)
        db.session.commit()
        return jsonify({"message": "Recipe created", "recipe_id": new_id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@recipes_bp.route('/<int:recipe_id>', methods=['PUT'])
def update_recipe(recipe_id):
    data = request.get_json() or {}
    required = ['name', 'duration', 'difficulty', 'cuisine', 'instructions']
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields for update: {', '.join(missing)}"}), 400

    params = {
        "recipe_id": recipe_id,
        "name": data["name"],
        "duration": data["duration"],
        "difficulty": data["difficulty"],
        "cuisine": data["cuisine"],
        "instructions": data["instructions"],
        "image_url": data.get("image_url"),
    }
    try:
        result = db.session.execute(text(UPDATE_RECIPE_SQL), params)
        if result.rowcount == 0:
            db.session.rollback()
            return jsonify({"error": "Recipe not found"}), 404
        db.session.commit()
        return jsonify({"message": "Recipe updated", "recipe_id": recipe_id}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@recipes_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_recipes(user_id):
    try:
        result = db.session.execute(text(GET_USER_RECIPES_SQL), {"user_id": user_id})
        recipes = []
        for row in result:
            recipes.append({
                "id": row[0],
                "title": row[1],  # Using 'title' to match frontend Recipe interface
                "duration": row[2],
                "difficulty": row[3],
                "cuisine": row[4],
                "instructions": row[5].split('\n') if row[5] else [],
                "image": row[6] or "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?auto=format&fit=crop&w=500&h=300",
                "ingredients": row[7].split(',') if row[7] else [],
                "isMyRecipe": True
            })
        return jsonify(recipes), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@recipes_bp.route('/<int:recipe_id>/like', methods=['POST'])
@jwt_required()
def like_recipe(recipe_id):
    try:
        current_user_id = int(get_jwt_identity())
        
        # Check if recipe exists
        recipe_check = db.session.execute(
            text("SELECT Recipe_ID FROM Recipes WHERE Recipe_ID = :recipe_id"),
            {"recipe_id": recipe_id}
        ).fetchone()
        
        if not recipe_check:
            return jsonify({"error": "Recipe not found"}), 404
        
        # Check if user has already liked this recipe
        existing_like = db.session.execute(
            text("SELECT * FROM Recipe_Likes WHERE User_ID = :user_id AND Recipe_ID = :recipe_id"),
            {"user_id": current_user_id, "recipe_id": recipe_id}
        ).fetchone()
        
        if existing_like:
            return jsonify({"error": "Recipe already liked"}), 400
        
        # Insert the like
        db.session.execute(
            text("INSERT INTO Recipe_Likes (User_ID, Recipe_ID) VALUES (:user_id, :recipe_id)"),
            {"user_id": current_user_id, "recipe_id": recipe_id}
        )
        
        # Add to Liked Recipes cooklist (create if it doesn't exist)
        liked_cooklist = db.session.execute(
            text("SELECT CookList_ID FROM CookLists WHERE User_ID = :user_id AND Name = 'Liked Recipes'"),
            {"user_id": current_user_id}
        ).fetchone()
        
        if not liked_cooklist:
            # Create the Liked Recipes cooklist
            db.session.execute(
                text("INSERT INTO CookLists (User_ID, Name, Description, Is_Public) VALUES (:user_id, 'Liked Recipes', 'Automatically created cooklist for liked recipes', 0)"),
                {"user_id": current_user_id}
            )
            liked_cooklist = db.session.execute(
                text("SELECT CookList_ID FROM CookLists WHERE User_ID = :user_id AND Name = 'Liked Recipes'"),
                {"user_id": current_user_id}
            ).fetchone()
        
        # Add recipe to Liked Recipes cooklist (if not already there)
        existing_in_cooklist = db.session.execute(
            text("SELECT * FROM CookList_Recipes WHERE CookList_ID = :cooklist_id AND Recipe_ID = :recipe_id"),
            {"cooklist_id": liked_cooklist[0], "recipe_id": recipe_id}
        ).fetchone()
        
        if not existing_in_cooklist:
            db.session.execute(
                text("INSERT INTO CookList_Recipes (CookList_ID, Recipe_ID) VALUES (:cooklist_id, :recipe_id)"),
                {"cooklist_id": liked_cooklist[0], "recipe_id": recipe_id}
            )
        
        db.session.commit()
        
        return jsonify({"message": "Recipe liked successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@recipes_bp.route('/<int:recipe_id>/unlike', methods=['DELETE'])
@jwt_required()
def unlike_recipe(recipe_id):
    try:
        current_user_id = int(get_jwt_identity())
        
        # Check if user has liked this recipe
        existing_like = db.session.execute(
            text("SELECT * FROM Recipe_Likes WHERE User_ID = :user_id AND Recipe_ID = :recipe_id"),
            {"user_id": current_user_id, "recipe_id": recipe_id}
        ).fetchone()
        
        if not existing_like:
            return jsonify({"error": "Recipe not liked"}), 400
        
        # Remove the like
        db.session.execute(
            text("DELETE FROM Recipe_Likes WHERE User_ID = :user_id AND Recipe_ID = :recipe_id"),
            {"user_id": current_user_id, "recipe_id": recipe_id}
        )
        
        # Also remove from Liked Recipes cooklist
        db.session.execute(
            text("""
                DELETE FROM CookList_Recipes 
                WHERE CookList_ID = (
                    SELECT CookList_ID FROM CookLists 
                    WHERE User_ID = :user_id AND Name = 'Liked Recipes'
                ) AND Recipe_ID = :recipe_id
            """),
            {"user_id": current_user_id, "recipe_id": recipe_id}
        )
        
        db.session.commit()
        
        return jsonify({"message": "Recipe unliked successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@recipes_bp.route('/<int:recipe_id>/liked', methods=['GET'])
@jwt_required()
def check_recipe_liked(recipe_id):
    try:
        current_user_id = int(get_jwt_identity())
        
        # Check if user has liked this recipe
        existing_like = db.session.execute(
            text("SELECT * FROM Recipe_Likes WHERE User_ID = :user_id AND Recipe_ID = :recipe_id"),
            {"user_id": current_user_id, "recipe_id": recipe_id}
        ).fetchone()
        
        return jsonify({"isLiked": existing_like is not None}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
