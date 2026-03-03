import os
from app import create_app, db
from app.models.user import User
from app.models.shop import Shop

# Utiliser la config de production sur Render
config_name = 'production' if os.environ.get('RENDER') else 'development'
app = create_app(config_name)

# ⭐ INITIALISATION AUTOMATIQUE DE LA BASE DE DONNÉES EN PRODUCTION
if config_name == 'production':
    with app.app_context():
        # Créer les tables si elles n'existent pas
        db.create_all()
        
        # Créer le super admin s'il n'existe pas
        if not User.query.filter_by(username='superadmin').first():
            print("🚀 Création du super admin...")
            super_admin = User(
                username='superadmin',
                email='superadmin@admin.com',
                role='super_admin',
                is_active=True
            )
            super_admin.password = 'SuperAdmin123!'
            db.session.add(super_admin)
            print("✅ Super admin créé")
        
        # Créer la boutique Dakar si elle n'existe pas
        if not Shop.query.filter_by(slug='boutique-dakar').first():
            print("🚀 Création de la boutique Dakar...")
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
            
            # Créer l'admin Dakar
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
        
        # Créer la boutique Thiès si elle n'existe pas
        if not Shop.query.filter_by(slug='boutique-thies').first():
            print("🚀 Création de la boutique Thiès...")
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
            
            # Créer l'admin Thiès
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
        print("🎉 Base de données initialisée avec succès !")

if __name__ == '__main__':
    app.run()