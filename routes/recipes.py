from flask import Blueprint, jsonify, request, current_app
from flask_mysqldb import MySQL

recipes_bp = Blueprint('recipes', __name__)

@recipes_bp.route('/', methods=['GET'])
def get_all_recipes():
    mysql: MySQL = current_app.extensions['mysql']
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name FROM recipes")
    data = cur.fetchall()
    cur.close()
    return jsonify(data)
