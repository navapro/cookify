from flask import Flask
from config import Config
from extensions import db
from flask_cors import CORS
from flask_jwt_extended import JWTManager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)

    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:8080", "http://localhost:5173", "http://127.0.0.1:8080", "http://127.0.0.1:5173", "http://localhost:8081"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Import and register blueprints
    from routes.users import users_bp
    from routes.recipes import recipes_bp
    from routes.cooklists import cooklists_bp
    from routes.shopping_lists import shopping_lists_bp
    from routes.user_ingredients import user_ingredients_bp
    
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(recipes_bp, url_prefix='/api/recipes')
    app.register_blueprint(cooklists_bp, url_prefix='/api/cooklists')
    app.register_blueprint(shopping_lists_bp, url_prefix='/api/shopping-lists')
    app.register_blueprint(user_ingredients_bp, url_prefix='/api/users')
    
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5001) 