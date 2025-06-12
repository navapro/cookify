from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

# Import and register blueprints
from routes.users import users_bp
from routes.recipes import recipes_bp
from routes.cooklists import cooklists_bp

app.register_blueprint(users_bp, url_prefix='/api/users')
app.register_blueprint(recipes_bp, url_prefix='/api/recipes')
app.register_blueprint(cooklists_bp, url_prefix='/api/cooklists')

if __name__ == "__main__":
    app.run(debug=True)
