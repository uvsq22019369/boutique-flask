# seed_data.py
from app import create_app, db
from app.models.user import User
from app.models.category import Category
from app.models.product import Product

app = create_app()

with app.app_context():
    # Créer des catégories
    categories = [
        Category(name='Électronique', description='Téléphones, ordinateurs, accessoires'),
        Category(name='Alimentation', description='Produits alimentaires, boissons'),
        Category(name='Vêtements', description='Habits, chaussures, accessoires'),
        Category(name='Maison', description='Meubles, décoration, électroménager')
    ]
    
    for cat in categories:
        existing = Category.query.filter_by(name=cat.name).first()
        if not existing:
            db.session.add(cat)
            print(f"✅ Catégorie ajoutée : {cat.name}")
    
    db.session.commit()
    
    # Récupérer l'admin
    admin = User.query.filter_by(username='admin').first()
    
    if admin:
        # Créer des produits de test
        cat_electronique = Category.query.filter_by(name='Électronique').first()
        cat_alimentation = Category.query.filter_by(name='Alimentation').first()
        
        produits = [
            Product(
                name='Smartphone Galaxy A12',
                description='Smartphone Android 6.5 pouces, 64GB',
                price=150000,
                stock_quantity=15,
                min_stock_alert=5,
                category=cat_electronique,
                created_by=admin.id
            ),
            Product(
                name='Ordinateur Portable HP',
                description='Intel Core i5, 8GB RAM, 512GB SSD',
                price=450000,
                stock_quantity=8,
                min_stock_alert=3,
                category=cat_electronique,
                created_by=admin.id
            ),
            Product(
                name='Sac de riz 25kg',
                description='Riz parfumé',
                price=18000,
                stock_quantity=45,
                min_stock_alert=10,
                category=cat_alimentation,
                created_by=admin.id
            ),
            Product(
                name='Huile d\'olive 1L',
                description='Huile d\'olive extra vierge',
                price=5000,
                stock_quantity=3,  # Stock bas pour test
                min_stock_alert=5,
                category=cat_alimentation,
                created_by=admin.id
            )
        ]
        
        for prod in produits:
            existing = Product.query.filter_by(name=prod.name).first()
            if not existing:
                db.session.add(prod)
                print(f"✅ Produit ajouté : {prod.name}")
        
        db.session.commit()
    
    print("🎉 Données de test ajoutées avec succès !")