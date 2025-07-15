from flask import Blueprint, jsonify, request
from extensions import db
from sqlalchemy import text

cooklists_bp = Blueprint('cooklists', __name__)

@cooklists_bp.route('/', methods=['GET'])
def get_all_cooklists():
    try:
        result = db.session.execute(text("""
            SELECT cl.CookList_ID, cl.Name, cl.Description, u.Name as User_Name,
                   GROUP_CONCAT(r.Name) as Recipes
            FROM CookLists cl
            JOIN Users u ON cl.User_ID = u.User_ID
            LEFT JOIN CookList_Recipes cr ON cl.CookList_ID = cr.CookList_ID
            LEFT JOIN Recipes r ON cr.Recipe_ID = r.Recipe_ID
            GROUP BY cl.CookList_ID
        """))
        cooklists = []
        for row in result:
            cooklists.append({
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "user": row[3],
                "recipes": row[4].split(',') if row[4] else []
            })
        return jsonify(cooklists)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@cooklists_bp.route('/<int:cooklist_id>', methods=['GET'])
def get_cooklist(cooklist_id):
    try:
        # Get cooklist details
        cooklist_result = db.session.execute(
            text("""
                SELECT cl.CookList_ID, cl.Name, cl.Description, u.Name as User_Name
                FROM CookLists cl
                JOIN Users u ON cl.User_ID = u.User_ID
                WHERE cl.CookList_ID = :id
            """),
            {"id": cooklist_id}
        )
        cooklist = cooklist_result.fetchone()
        
        if not cooklist:
            return jsonify({"error": "CookList not found"}), 404
        
        # Get recipes in this cooklist
        recipes_result = db.session.execute(
            text("""
                SELECT r.Recipe_ID, r.Name, r.Duration, r.Difficulty, r.Cuisine, 
                       r.Instructions, r.Image_URL,
                       GROUP_CONCAT(i.Name) as Ingredients
                FROM Recipes r
                JOIN CookList_Recipes cr ON r.Recipe_ID = cr.Recipe_ID
                LEFT JOIN Recipe_Ingredients ri ON r.Recipe_ID = ri.Recipe_ID
                LEFT JOIN Ingredients i ON ri.Ingredient_ID = i.Ingredient_ID
                WHERE cr.CookList_ID = :id
                GROUP BY r.Recipe_ID
            """),
            {"id": cooklist_id}
        )
        
        recipes = []
        for row in recipes_result:
            recipes.append({
                "id": row[0],
                "title": row[1],
                "duration": row[2],
                "difficulty": row[3],
                "cuisine": row[4],
                "instructions": row[5].split('\n') if row[5] else [],
                "image": row[6] or "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?auto=format&fit=crop&w=500&h=300",
                "ingredients": row[7].split(',') if row[7] else [],
                "isMyRecipe": True
            })
        
        return jsonify({
            "id": cooklist[0],
            "name": cooklist[1],
            "description": cooklist[2],
            "user": cooklist[3],
            "recipeCount": len(recipes),
            "recipes": recipes
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@cooklists_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_cooklists(user_id):
    try:
        result = db.session.execute(
            text("""
                SELECT cl.CookList_ID, cl.Name, cl.Description, u.Name as User_Name,
                       COUNT(cr.Recipe_ID) as Recipe_Count,
                       GROUP_CONCAT(r.Name) as Recipes
                FROM CookLists cl
                JOIN Users u ON cl.User_ID = u.User_ID
                LEFT JOIN CookList_Recipes cr ON cl.CookList_ID = cr.CookList_ID
                LEFT JOIN Recipes r ON cr.Recipe_ID = r.Recipe_ID
                WHERE cl.User_ID = :user_id
                GROUP BY cl.CookList_ID
                ORDER BY cl.CookList_ID DESC
            """),
            {"user_id": user_id}
        )
        cooklists = []
        for row in result:
            cooklists.append({
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "user": row[3],
                "recipeCount": row[4],
                "recipes": row[5].split(',') if row[5] else []
            })
        return jsonify(cooklists)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@cooklists_bp.route('/', methods=['POST'])
def create_cooklist():
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description', '')
        user_id = data.get('user_id')
        
        if not name or not user_id:
            return jsonify({"error": "Name and user_id are required"}), 400
        
        # Insert new cooklist
        result = db.session.execute(
            text("""
                INSERT INTO CookLists (User_ID, Name, Description, Is_Public, Created_At, Updated_At)
                VALUES (:user_id, :name, :description, 0, NOW(), NOW())
            """),
            {"user_id": user_id, "name": name, "description": description}
        )
        db.session.commit()
        
        # Get the created cooklist ID
        cooklist_id = result.lastrowid
        
        return jsonify({
            "id": cooklist_id,
            "name": name,
            "description": description,
            "message": "Cooklist created successfully"
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@cooklists_bp.route('/<int:cooklist_id>/recipes', methods=['POST'])
def add_recipe_to_cooklist(cooklist_id):
    try:
        data = request.get_json()
        recipe_id = data.get('recipe_id')
        
        if not recipe_id:
            return jsonify({"error": "recipe_id is required"}), 400
        
        # Check if recipe is already in the cooklist
        existing = db.session.execute(
            text("""
                SELECT * FROM CookList_Recipes 
                WHERE CookList_ID = :cooklist_id AND Recipe_ID = :recipe_id
            """),
            {"cooklist_id": cooklist_id, "recipe_id": recipe_id}
        ).fetchone()
        
        if existing:
            return jsonify({"error": "Recipe already exists in this cooklist"}), 400
        
        # Add recipe to cooklist
        db.session.execute(
            text("""
                INSERT INTO CookList_Recipes (CookList_ID, Recipe_ID)
                VALUES (:cooklist_id, :recipe_id)
            """),
            {"cooklist_id": cooklist_id, "recipe_id": recipe_id}
        )
        db.session.commit()
        
        return jsonify({"message": "Recipe added to cooklist successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
@cooklists_bp.route('/<int:cooklist_id>/recipes', methods=['GET'])
def get_cooklist_recipes_sorted(cooklist_id):
    """
    Get recipes in a cooklist, ordered by date added (asc/desc) or by name.
    Query param: sort = 'date_asc' | 'date_desc' | 'name_asc'
    """
    sort = request.args.get('sort', 'date_desc')
    if sort == 'date_asc':
        order_clause = "clr.Added_At ASC"
    elif sort == 'name_asc':
        order_clause = "r.Name ASC"
    elif sort == 'name_desc':
        order_clause = "r.Name DESC"
    else:
        order_clause = "clr.Added_At DESC"

    try:
        recipes_result = db.session.execute(
            text(f"""
                SELECT r.Recipe_ID, r.Name, r.Cuisine, r.Difficulty, r.Instructions, clr.Added_At AS Added_To_List_At
                FROM CookList_Recipes clr
                JOIN Recipes r ON clr.Recipe_ID = r.Recipe_ID
                WHERE clr.CookList_ID = :id
                ORDER BY {order_clause}
            """),
            {"id": cooklist_id}
        )
        recipes = []
        for row in recipes_result:
            recipe_id = row[0]
            
            # Get detailed ingredients for this recipe
            ingredients_result = db.session.execute(
                text("""
                    SELECT ri.Ingredient_ID, i.Name, ri.Quantity, ri.Unit, i.Category
                    FROM Recipe_Ingredients ri
                    JOIN Ingredients i ON ri.Ingredient_ID = i.Ingredient_ID
                    WHERE ri.Recipe_ID = :recipe_id
                """),
                {"recipe_id": recipe_id}
            )
            
            ingredients = []
            for ing_row in ingredients_result:
                ingredients.append({
                    "ingredient_id": ing_row[0],
                    "name": ing_row[1],
                    "quantity": ing_row[2],
                    "unit": ing_row[3],
                    "category": ing_row[4]
                })
            
            recipes.append({
                "id": recipe_id,
                "name": row[1],
                "cuisine": row[2],
                "difficulty": row[3],
                "instructions": row[4].split('\n') if row[4] else [],
                "added_at": row[5].isoformat() if row[5] else None,
                "ingredients": ingredients,
            })
        return jsonify(recipes)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
