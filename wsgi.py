from flask import Flask
from config import Config
from extensions import db
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)

    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:8080", "http://localhost:5173", "http://127.0.0.1:8080", "http://127.0.0.1:5173"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Import and register blueprints
    from routes.users import users_bp
    from routes.recipes import recipes_bp
    from routes.cooklists import cooklists_bp
    
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(recipes_bp, url_prefix='/api/recipes')
    app.register_blueprint(cooklists_bp, url_prefix='/api/cooklists')
    
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5001) 