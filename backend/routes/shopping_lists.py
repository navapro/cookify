from flask import Blueprint, jsonify, request
from extensions import db
from sqlalchemy import text
from flask_jwt_extended import jwt_required, get_jwt_identity

shopping_lists_bp = Blueprint('shopping_lists', __name__)

@shopping_lists_bp.route('/', methods=['GET'])
@jwt_required()
def get_user_shopping_lists():
    """Get all shopping lists for the current user"""
    try:
        user_id = get_jwt_identity()
        result = db.session.execute(text("""
            SELECT sl.Shopping_List_ID, sl.Name, sl.CookList_ID, cl.Name as CookList_Name,
                   sl.Created_At, sl.Updated_At,
                   COUNT(sli.Ingredient_ID) as Total_Items,
                   COUNT(CASE WHEN sli.Is_Purchased = 1 THEN 1 END) as Purchased_Items
            FROM Shopping_Lists sl
            LEFT JOIN CookLists cl ON sl.CookList_ID = cl.CookList_ID
            LEFT JOIN Shopping_List_Items sli ON sl.Shopping_List_ID = sli.Shopping_List_ID
            WHERE sl.User_ID = :user_id
            GROUP BY sl.Shopping_List_ID
            ORDER BY sl.Created_At DESC
        """), {"user_id": user_id})
        
        shopping_lists = []
        for row in result:
            shopping_lists.append({
                "id": row[0],
                "name": row[1],
                "cooklist_id": row[2],
                "cooklist_name": row[3],
                "created_at": row[4].isoformat() if row[4] else None,
                "updated_at": row[5].isoformat() if row[5] else None,
                "total_items": row[6],
                "purchased_items": row[7]
            })
        
        return jsonify(shopping_lists), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@shopping_lists_bp.route('/<int:shopping_list_id>', methods=['GET'])
@jwt_required()
def get_shopping_list(shopping_list_id):
    """Get a specific shopping list with items"""
    try:
        user_id = get_jwt_identity()
        
        # First verify the shopping list belongs to the user
        list_result = db.session.execute(text("""
            SELECT sl.Shopping_List_ID, sl.Name, sl.CookList_ID, cl.Name as CookList_Name
            FROM Shopping_Lists sl
            LEFT JOIN CookLists cl ON sl.CookList_ID = cl.CookList_ID
            WHERE sl.Shopping_List_ID = :list_id AND sl.User_ID = :user_id
        """), {"list_id": shopping_list_id, "user_id": user_id})
        
        shopping_list = list_result.fetchone()
        if not shopping_list:
            return jsonify({"error": "Shopping list not found"}), 404
        
        # Get shopping list items
        items_result = db.session.execute(text("""
            SELECT sli.Ingredient_ID, i.Name, sli.Quantity, sli.Is_Purchased, 
                   i.Category, i.Price, sli.Added_At
            FROM Shopping_List_Items sli
            JOIN Ingredients i ON sli.Ingredient_ID = i.Ingredient_ID
            WHERE sli.Shopping_List_ID = :list_id
            ORDER BY i.Category, i.Name
        """), {"list_id": shopping_list_id})
        
        items = []
        for row in items_result:
            items.append({
                "ingredient_id": row[0],
                "name": row[1],
                "quantity": row[2],
                "is_purchased": bool(row[3]),
                "category": row[4],
                "price": float(row[5]) if row[5] else None,
                "added_at": row[6].isoformat() if row[6] else None
            })
        
        return jsonify({
            "id": shopping_list[0],
            "name": shopping_list[1],
            "cooklist_id": shopping_list[2],
            "cooklist_name": shopping_list[3],
            "items": items
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@shopping_lists_bp.route('/', methods=['POST'])
@jwt_required()
def create_shopping_list():
    """Create a new shopping list"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        name = data.get('name', 'Shopping List')
        cooklist_id = data.get('cooklist_id')
        
        # Validate cooklist belongs to user if provided
        if cooklist_id:
            cooklist_check = db.session.execute(text("""
                SELECT CookList_ID FROM CookLists 
                WHERE CookList_ID = :cooklist_id AND User_ID = :user_id
            """), {"cooklist_id": cooklist_id, "user_id": user_id})
            
            if not cooklist_check.fetchone():
                return jsonify({"error": "CookList not found or not accessible"}), 404
        
        # Create shopping list
        result = db.session.execute(text("""
            INSERT INTO Shopping_Lists (User_ID, Name, CookList_ID)
            VALUES (:user_id, :name, :cooklist_id)
        """), {"user_id": user_id, "name": name, "cooklist_id": cooklist_id})
        
        shopping_list_id = result.lastrowid
        
        # If linked to a cooklist, automatically populate with ingredients
        if cooklist_id:
            db.session.execute(text("""
                INSERT INTO Shopping_List_Items (Shopping_List_ID, Ingredient_ID, Quantity)
                SELECT :shopping_list_id, ri.Ingredient_ID, ri.Quantity
                FROM CookList_Recipes cr
                JOIN Recipe_Ingredients ri ON cr.Recipe_ID = ri.Recipe_ID
                WHERE cr.CookList_ID = :cooklist_id
                GROUP BY ri.Ingredient_ID
            """), {"shopping_list_id": shopping_list_id, "cooklist_id": cooklist_id})
        
        db.session.commit()
        
        return jsonify({
            "message": "Shopping list created successfully",
            "shopping_list_id": shopping_list_id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@shopping_lists_bp.route('/<int:shopping_list_id>/items', methods=['POST'])
@jwt_required()
def add_item_to_shopping_list(shopping_list_id):
    """Add an item to a shopping list"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        ingredient_id = data.get('ingredient_id')
        quantity = data.get('quantity', '1')
        
        if not ingredient_id:
            return jsonify({"error": "ingredient_id is required"}), 400
        
        # Verify shopping list belongs to user
        list_check = db.session.execute(text("""
            SELECT Shopping_List_ID FROM Shopping_Lists 
            WHERE Shopping_List_ID = :list_id AND User_ID = :user_id
        """), {"list_id": shopping_list_id, "user_id": user_id})
        
        if not list_check.fetchone():
            return jsonify({"error": "Shopping list not found"}), 404
        
        # Add or update item
        db.session.execute(text("""
            INSERT INTO Shopping_List_Items (Shopping_List_ID, Ingredient_ID, Quantity)
            VALUES (:list_id, :ingredient_id, :quantity)
            ON DUPLICATE KEY UPDATE
            Quantity = :quantity, Added_At = CURRENT_TIMESTAMP
        """), {
            "list_id": shopping_list_id,
            "ingredient_id": ingredient_id,
            "quantity": quantity
        })
        
        db.session.commit()
        
        return jsonify({"message": "Item added to shopping list"}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@shopping_lists_bp.route('/<int:shopping_list_id>/items/<int:ingredient_id>', methods=['PUT'])
@jwt_required()
def update_shopping_list_item(shopping_list_id, ingredient_id):
    """Update an item in a shopping list (mark as purchased/unpurchased)"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        # Verify shopping list belongs to user
        list_check = db.session.execute(text("""
            SELECT Shopping_List_ID FROM Shopping_Lists 
            WHERE Shopping_List_ID = :list_id AND User_ID = :user_id
        """), {"list_id": shopping_list_id, "user_id": user_id})
        
        if not list_check.fetchone():
            return jsonify({"error": "Shopping list not found"}), 404
        
        # Update item
        is_purchased = data.get('is_purchased', False)
        quantity = data.get('quantity')
        
        update_fields = ["Is_Purchased = :is_purchased"]
        params = {
            "list_id": shopping_list_id,
            "ingredient_id": ingredient_id,
            "is_purchased": is_purchased
        }
        
        if quantity is not None:
            update_fields.append("Quantity = :quantity")
            params["quantity"] = quantity
        
        result = db.session.execute(text(f"""
            UPDATE Shopping_List_Items 
            SET {', '.join(update_fields)}
            WHERE Shopping_List_ID = :list_id AND Ingredient_ID = :ingredient_id
        """), params)
        
        if result.rowcount == 0:
            return jsonify({"error": "Item not found in shopping list"}), 404
        
        db.session.commit()
        
        return jsonify({"message": "Item updated"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@shopping_lists_bp.route('/<int:shopping_list_id>/items/<int:ingredient_id>', methods=['DELETE'])
@jwt_required()
def remove_item_from_shopping_list(shopping_list_id, ingredient_id):
    """Remove an item from a shopping list"""
    try:
        user_id = get_jwt_identity()
        
        # Verify shopping list belongs to user
        list_check = db.session.execute(text("""
            SELECT Shopping_List_ID FROM Shopping_Lists 
            WHERE Shopping_List_ID = :list_id AND User_ID = :user_id
        """), {"list_id": shopping_list_id, "user_id": user_id})
        
        if not list_check.fetchone():
            return jsonify({"error": "Shopping list not found"}), 404
        
        # Remove item
        result = db.session.execute(text("""
            DELETE FROM Shopping_List_Items 
            WHERE Shopping_List_ID = :list_id AND Ingredient_ID = :ingredient_id
        """), {"list_id": shopping_list_id, "ingredient_id": ingredient_id})
        
        if result.rowcount == 0:
            return jsonify({"error": "Item not found in shopping list"}), 404
        
        db.session.commit()
        
        return jsonify({"message": "Item removed from shopping list"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@shopping_lists_bp.route('/<int:shopping_list_id>', methods=['DELETE'])
@jwt_required()
def delete_shopping_list(shopping_list_id):
    """Delete a shopping list"""
    try:
        user_id = get_jwt_identity()
        
        # Verify and delete shopping list
        result = db.session.execute(text("""
            DELETE FROM Shopping_Lists 
            WHERE Shopping_List_ID = :list_id AND User_ID = :user_id
        """), {"list_id": shopping_list_id, "user_id": user_id})
        
        if result.rowcount == 0:
            return jsonify({"error": "Shopping list not found"}), 404
        
        db.session.commit()
        
        return jsonify({"message": "Shopping list deleted"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500