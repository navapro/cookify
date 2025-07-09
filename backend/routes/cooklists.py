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
            recipes.append({
                "id": row[0],
                "name": row[1],
                "cuisine": row[2],
                "difficulty": row[3],
                "instructions": row[4].split('\n') if row[4] else [],
                "added_at": row[5].isoformat() if row[5] else None,
            })
        return jsonify(recipes)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
