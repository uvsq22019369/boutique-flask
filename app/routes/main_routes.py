from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.shop import Shop
from app.models.user import User
from app.models.category import Category
from app.models.product import Product
from app.models.client import Client
from app import db

# ⭐ DÉFINITION DU BLUEPRINT (TRÈS IMPORTANT)
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Page d'accueil publique"""
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Redirection vers le dashboard avancé"""
    return redirect(url_for('dashboard.index'))

@main_bp.route('/shop-info')
@login_required
def shop_info():
    """Afficher les informations de la boutique (optionnel)"""
    if current_user.shop_id:
        shop = Shop.query.get(current_user.shop_id)
        return f"Boutique: {shop.name}"
    return "Super Admin - Toutes les boutiques"

# ⭐ ROUTE TEMPORAIRE POUR INITIALISER LA BASE DE DONNÉES
@main_bp.route('/init-db')
def init_db():
    """Route temporaire pour initialiser la base de données (À SUPPRIMER APRÈS)"""
    try:
        # Créer les tables
        db.create_all()
        
        # 1. Créer le super admin
        if not User.query.filter_by(username='superadmin').first():
            super_admin = User(
                username='superadmin',
                email='superadmin@admin.com',
                role='super_admin',
                is_active=True
            )
            super_admin.password = 'SuperAdmin123!'
            db.session.add(super_admin)
            print("✅ Super admin créé")
        
        # 2. Créer la boutique Dakar
        shop_dakar = Shop.query.filter_by(slug='boutique-dakar').first()
        if not shop_dakar:
            shop_dakar = Shop(
                name='Boutique Dakar Centre',
                slug='boutique-dakar',
                address='Dakar, Sénégal',
                phone='771234567',
                email='contact@dakar.sn',
                is_active=True
            )
            db.session.add(shop_dakar)
            db.session.flush()
            print("✅ Boutique Dakar créée")
        
        # 3. Créer l'admin Dakar
        if not User.query.filter_by(username='admin_dakar').first():
            admin_dakar = User(
                username='admin_dakar',
                email='admin@dakar.sn',
                role='admin',
                shop_id=shop_dakar.id,
                is_active=True
            )
            admin_dakar.password = 'admin123'
            db.session.add(admin_dakar)
            print("✅ Admin Dakar créé")
        
        # 4. Créer la boutique Thiès
        shop_thies = Shop.query.filter_by(slug='boutique-thies').first()
        if not shop_thies:
            shop_thies = Shop(
                name='Boutique Thiès',
                slug='boutique-thies',
                address='Thiès, Sénégal',
                phone='772345678',
                email='contact@thies.sn',
                is_active=True
            )
            db.session.add(shop_thies)
            db.session.flush()
            print("✅ Boutique Thiès créée")
        
        # 5. Créer l'admin Thiès
        if not User.query.filter_by(username='admin_thies').first():
            admin_thies = User(
                username='admin_thies',
                email='admin@thies.sn',
                role='admin',
                shop_id=shop_thies.id,
                is_active=True
            )
            admin_thies.password = 'admin123'
            db.session.add(admin_thies)
            print("✅ Admin Thiès créé")
        
        db.session.commit()
        
        return """
        <h1 style="color: green; text-align: center; margin-top: 50px;">✅ BASE DE DONNÉES INITIALISÉE AVEC SUCCÈS !</h1>
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
            <h2 style="color: #333;">Identifiants :</h2>
            <ul style="list-style: none; padding: 0;">
                <li style="margin: 10px 0; padding: 10px; background: #f0f0f0; border-radius: 5px;">
                    <strong style="color: #007bff;">👑 Super Admin :</strong> superadmin / SuperAdmin123!
                </li>
                <li style="margin: 10px 0; padding: 10px; background: #f0f0f0; border-radius: 5px;">
                    <strong style="color: #28a745;">🏪 Admin Dakar :</strong> admin_dakar / admin123
                </li>
                <li style="margin: 10px 0; padding: 10px; background: #f0f0f0; border-radius: 5px;">
                    <strong style="color: #28a745;">🏪 Admin Thiès :</strong> admin_thies / admin123
                </li>
            </ul>
            <p style="color: red; font-weight: bold; text-align: center;">
                ⚠️ N'OUBLIEZ PAS DE SUPPRIMER CETTE ROUTE APRÈS UTILISATION !
            </p>
            <div style="text-align: center; margin-top: 30px;">
                <a href="/auth/login" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                    Aller à la page de connexion
                </a>
            </div>
        </div>
        """
    except Exception as e:
        return f"""
        <h1 style="color: red; text-align: center; margin-top: 50px;">❌ ERREUR</h1>
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ff4444; border-radius: 10px; background: #ffeeee;">
            <p style="font-size: 18px;"><strong>Message :</strong> {str(e)}</p>
        </div>
        """