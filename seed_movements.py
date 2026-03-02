# seed_movements.py
from app import create_app, db
from app.models.product import Product
from app.models.stock_movement import StockMovement
from app.models.user import User
from datetime import datetime, timedelta
import random

app = create_app()

with app.app_context():
    # Récupérer l'admin et les produits
    admin = User.query.filter_by(username='admin').first()
    products = Product.query.all()
    
    if admin and products:
        # Créer des mouvements pour les 7 derniers jours
        for i in range(20):
            product = random.choice(products)
            days_ago = random.randint(0, 7)
            movement_date = datetime.now() - timedelta(days=days_ago)
            
            # Alterner entrées et sorties
            if random.choice([True, False]):
                movement_type = 'IN_PURCHASE'
                quantity = random.randint(5, 20)
            else:
                movement_type = 'OUT_SALE'
                quantity = random.randint(1, 5)
            
            # Stock avant (simulé)
            stock_before = product.stock_quantity
            stock_after = stock_before + quantity if movement_type.startswith('IN') else stock_before - quantity
            
            movement = StockMovement(
                product_id=product.id,
                user_id=admin.id,
                movement_type=movement_type,
                quantity=quantity,
                stock_before=stock_before,
                stock_after=stock_after,
                reason="Données de test",
                created_at=movement_date
            )
            db.session.add(movement)
        
        db.session.commit()
        print(f"✅ {20} mouvements de test créés !")