from app.models.shop import Shop
from app.models.user import User
from app.models.category import Category
from app.models.product import Product
from app.models.client import Client
from app import db

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
        <h1 style="color: green;">✅ Base de données initialisée avec succès !</h1>
        <h2>Identifiants :</h2>
        <ul>
            <li><strong>Super Admin :</strong> superadmin / SuperAdmin123!</li>
            <li><strong>Admin Dakar :</strong> admin_dakar / admin123</li>
            <li><strong>Admin Thiès :</strong> admin_thies / admin123</li>
        </ul>
        <p style="color: red;">⚠️ N'OUBLIEZ PAS DE SUPPRIMER CETTE ROUTE APRÈS UTILISATION !</p>
        <a href="/auth/login">Aller à la page de connexion</a>
        """
    except Exception as e:
        return f"<h1 style='color: red;'>❌ Erreur : {str(e)}</h1>"