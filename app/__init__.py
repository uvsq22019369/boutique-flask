from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_session import Session
from config import config
from datetime import datetime
import os

# Initialisation des extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
bcrypt = Bcrypt()
sess = Session()

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Configuration
    app.config.from_object(config[config_name])
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'cle-secrete-tres-longue-pour-projet-boutique'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    
    # Initialisation des extensions avec l'app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    sess.init_app(app)
    
    # Configuration de Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page'
    
    # ⭐ IMPORTANT: User loader pour Flask-Login
    from app.models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Ajouter des variables globales aux templates
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}
    
    # Enregistrement des blueprints
    from app.routes.main_routes import main_bp
    from app.routes.auth_routes import auth_bp
    from app.routes.category_routes import category_bp
    from app.routes.product_routes import product_bp
    from app.routes.stock_routes import stock_bp
    from app.routes.client_routes import client_bp
    from app.routes.order_routes import order_bp
    from app.routes.dashboard_routes import dashboard_bp
    from app.routes.report_routes import report_bp
    from app.routes.shop_routes import shop_bp
    
    
    app.register_blueprint(shop_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(category_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(stock_bp)
    app.register_blueprint(client_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(report_bp, url_prefix='/rapports')
    
    # Import des modèles
    from app.models import user, shop, category, product, stock_movement, client, order, order_item
    
    # Création des tables si elles n'existent pas
    with app.app_context():
        db.create_all()
        print("✅ Base de données vérifiée/créée")
    
    return app