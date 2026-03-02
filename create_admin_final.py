# create_admin_final.py
from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    # Supprimer les anciens utilisateurs s'ils existent
    User.query.delete()
    
    # Créer l'admin
    admin = User(
        username='admin',
        email='admin@boutique.com',
        role='admin',
        is_active=True
    )
    admin.password = 'admin123'  # Le setter utilise bcrypt
    
    # Créer un utilisateur test
    test = User(
        username='test',
        email='test@test.com',
        role='cashier',
        is_active=True
    )
    test.password = 'test123'
    
    # Ajouter à la base
    db.session.add(admin)
    db.session.add(test)
    db.session.commit()
    
    print("✅ Utilisateurs créés avec succès !")
    print("   Admin: admin / admin123")
    print("   Test: test / test123")
    
    # Vérification
    print("\n🔍 Vérification des hashages:")
    admin_check = admin.verify_password('admin123')
    test_check = test.verify_password('test123')
    print(f"   Admin vérification: {'✅ OK' if admin_check else '❌ Échec'}")
    print(f"   Test vérification: {'✅ OK' if test_check else '❌ Échec'}")