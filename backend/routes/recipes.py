# recipes.py
from flask import Blueprint, jsonify, request
from extensions import db
from sqlalchemy import text

recipes_bp = Blueprint('recipes', __name__)

# SQL statements with named params
ADD_RECIPE_SQL = """
INSERT INTO Recipes
    (Name, Duration, Difficulty, Cuisine, Instructions, Image_URL, User_ID)
VALUES
    (:name, :duration, :difficulty, :cuisine, :instructions, :image_url);
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

@recipes_bp.route('/', methods=['GET'])
def get_all_recipes():
    try:
        limit = request.args.get('limit', default=12, type=int)
        offset = request.args.get('offset', default=0, type=int)
        params = {"limit": limit, "offset": offset}
        result = db.session.execute(text(GET_RECIPES_JOINED_SQL), params)
        recipes = []
        for row in result:
            recipes.append({
                "id": row[0],
                "name": row[1],
                "duration": row[2],
                "difficulty": row[3],
                "cuisine": row[4],
                "instructions": row[5],
                "ingredients": row[6].split(',') if row[6] else []
            })
        return jsonify(recipes), 200
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
def add_recipe():
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
