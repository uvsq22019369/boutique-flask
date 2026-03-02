from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import config

# Initialisation des extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Configuration
    app.config.from_object(config[config_name])
    
    # Initialisation des extensions avec l'app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Configuration de Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page'
    
    # ===================================================
    # 👇 C'EST ICI QU'ON ENREGISTRE LES BLUEPRINTS
    # ===================================================
    
    # 1. D'abord on importe les blueprints
    from app.routes.main_routes import main_bp
    from app.routes.category_routes import category_bp
    from app.routes.product_routes import product_bp
    
    # 2. Ensuite on les enregistre
    app.register_blueprint(main_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(product_bp)
    
    # Plus tard on ajoutera ceux-ci :
    # from app.routes.auth_routes import auth_bp
    # app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # ===================================================
    
    # Import des modèles (important pour Flask-Migrate)
    from app.models import user, category, product
    
    return app