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
            FROM CookList cl
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
        result = db.session.execute(
            text("""
                SELECT cl.CookList_ID, cl.Name, cl.Description, u.Name as User_Name,
                       GROUP_CONCAT(r.Name) as Recipes
                FROM CookList cl
                JOIN Users u ON cl.User_ID = u.User_ID
                LEFT JOIN CookList_Recipes cr ON cl.CookList_ID = cr.CookList_ID
                LEFT JOIN Recipes r ON cr.Recipe_ID = r.Recipe_ID
                WHERE cl.CookList_ID = :id
                GROUP BY cl.CookList_ID
            """),
            {"id": cooklist_id}
        )
        cooklist = result.fetchone()
        if cooklist:
            return jsonify({
                "id": cooklist[0],
                "name": cooklist[1],
                "description": cooklist[2],
                "user": cooklist[3],
                "recipes": cooklist[4].split(',') if cooklist[4] else []
            })
        return jsonify({"error": "CookList not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500 