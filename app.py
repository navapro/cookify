from flask import Flask
from flask_mysqldb import MySQL
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

mysql = MySQL(app)

# add routes later
from routes.recipes import recipes_bp
app.register_blueprint(recipes_bp, url_prefix='/recipes')

if __name__ == "__main__":
    app.run(debug=True)
