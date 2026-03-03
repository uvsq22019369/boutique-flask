from app import db
from datetime import datetime

class StockMovement(db.Model):
    __tablename__ = 'stock_movements'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Références
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Multi-boutiques
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'), nullable=False)
    
    # Optionnel : lié à une commande
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=True)
    
    # Type de mouvement
    movement_type = db.Column(db.String(20), nullable=False)
    # IN_PURCHASE, IN_RETURN, IN_ADJUSTMENT
    # OUT_SALE, OUT_DAMAGED, OUT_RETURN, OUT_ADJUSTMENT
    
    # Quantité (toujours positive)
    quantity = db.Column(db.Integer, nullable=False)
    
    # État du stock AVANT et APRÈS
    stock_before = db.Column(db.Integer, nullable=False)
    stock_after = db.Column(db.Integer, nullable=False)
    
    # Informations supplémentaires
    reason = db.Column(db.String(200), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    # Horodatage
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations - CORRIGÉ : backref='stock_movements' pour correspondre à Product
    product = db.relationship('Product', backref='stock_movements')
    user = db.relationship('User', backref='stock_movements')
    order = db.relationship('Order', backref='stock_movements')
    
    def __repr__(self):
        return f'<StockMovement {self.movement_type} {self.quantity} - Prod {self.product_id}>'