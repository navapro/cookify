from flask import Blueprint, jsonify, request
from extensions import db
from sqlalchemy import text

recipes_bp = Blueprint('recipes', __name__)

@recipes_bp.route('/', methods=['GET'])
def get_all_recipes():
    try:
        limit = int(request.args.get('limit', 10))
        offset = int(request.args.get('offset', 0))

        query = text(f"""
            WITH RecipeData AS (
                SELECT r.Recipe_ID, r.Name, r.Duration, r.Difficulty, r.Cuisine,
                       i.Name AS Ingredient
                FROM Recipes r
                LEFT JOIN Recipe_Ingredients ri ON r.Recipe_ID = ri.Recipe_ID
                LEFT JOIN Ingredients i ON ri.Ingredient_ID = i.Ingredient_ID
            )
            SELECT rd.Recipe_ID, rd.Name, rd.Duration, rd.Difficulty, rd.Cuisine,
                   GROUP_CONCAT(rd.Ingredient) AS Ingredients
            FROM RecipeData rd
            GROUP BY rd.Recipe_ID
            ORDER BY rd.Recipe_ID
            LIMIT :limit OFFSET :offset
        """)

        result = db.session.execute(query, {"limit": limit, "offset": offset})

        recipes = []
        for row in result:
            recipes.append({
                "id": row[0],
                "name": row[1],
                "duration": row[2],
                "difficulty": row[3],
                "cuisine": row[4],
                "ingredients": row[5].split(',') if row[5] else []
            })
        return jsonify(recipes)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@recipes_bp.route('/<int:recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    try:
        result = db.session.execute(
            text("""
                SELECT r.Recipe_ID, r.Name, r.Duration, r.Difficulty, r.Cuisine, r.Instructions,
                       GROUP_CONCAT(i.Name) as Ingredients
                FROM Recipes r
                LEFT JOIN Recipe_Ingredients ri ON r.Recipe_ID = ri.Recipe_ID
                LEFT JOIN Ingredients i ON ri.Ingredient_ID = i.Ingredient_ID
                WHERE r.Recipe_ID = :id
                GROUP BY r.Recipe_ID
            """),
            {"id": recipe_id}
        )
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
            })
        return jsonify({"error": "Recipe not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
