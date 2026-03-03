# seed_multi_tenant.py
from app import create_app, db
from app.models.user import User
from app.models.shop import Shop
from app.models.category import Category
from app.models.product import Product
from app.models.client import Client

app = create_app()

with app.app_context():
    print("🚀 Initialisation des données multi-boutiques...")
    
    # 1. Créer le super admin
    super_admin = User.query.filter_by(username='superadmin').first()
    if not super_admin:
        super_admin = User(
            username='superadmin',
            email='superadmin@admin.com',
            role='super_admin',
            is_active=True
        )
        super_admin.password = 'SuperAdmin123!'
        db.session.add(super_admin)
        db.session.flush()
        print("✅ Super admin créé (superadmin / SuperAdmin123!)")
    else:
        print("✅ Super admin déjà existant")
    
    # 2. Créer une boutique test 1
    shop1 = Shop.query.filter_by(slug='boutique-dakar').first()
    if not shop1:
        shop1 = Shop(
            name='Boutique Dakar Centre',
            slug='boutique-dakar',
            address='15 Rue Félix Faure, Dakar',
            phone='771234567',
            email='contact@boutique-dakar.sn',
            currency='FCFA',
            timezone='Africa/Dakar'
        )
        db.session.add(shop1)
        db.session.flush()
        print(f"✅ Boutique créée: {shop1.name}")
    else:
        print(f"✅ Boutique déjà existante: {shop1.name}")
    
    # 3. Créer une boutique test 2
    shop2 = Shop.query.filter_by(slug='boutique-thies').first()
    if not shop2:
        shop2 = Shop(
            name='Boutique Thiès',
            slug='boutique-thies',
            address='Avenue Lamine Guèye, Thiès',
            phone='772345678',
            email='contact@boutique-thies.sn',
            currency='FCFA',
            timezone='Africa/Dakar'
        )
        db.session.add(shop2)
        db.session.flush()
        print(f"✅ Boutique créée: {shop2.name}")
    else:
        print(f"✅ Boutique déjà existante: {shop2.name}")
    
    # 4. Créer un admin pour la boutique 1
    admin1 = User.query.filter_by(username='admin_dakar').first()
    if not admin1:
        admin1 = User(
            username='admin_dakar',
            email='admin@boutique-dakar.sn',
            role='shop_admin',
            shop_id=shop1.id,
            is_active=True
        )
        admin1.password = 'admin123'
        db.session.add(admin1)
        print(f"✅ Admin créé pour {shop1.name}: admin_dakar / admin123")
    
    # 5. Créer un admin pour la boutique 2
    admin2 = User.query.filter_by(username='admin_thies').first()
    if not admin2:
        admin2 = User(
            username='admin_thies',
            email='admin@boutique-thies.sn',
            role='shop_admin',
            shop_id=shop2.id,
            is_active=True
        )
        admin2.password = 'admin123'
        db.session.add(admin2)
        print(f"✅ Admin créé pour {shop2.name}: admin_thies / admin123")
    
    db.session.commit()
    print("\n" + "="*50)
    print("🎉 INITIALISATION MULTI-BOUTIQUES TERMINÉE !")
    print("="*50)
    print("\nConnexions disponibles :")
    print("  - superadmin / SuperAdmin123! (voit tout)")
    print("  - admin_dakar / admin123 (Boutique Dakar)")
    print("  - admin_thies / admin123 (Boutique Thiès)")