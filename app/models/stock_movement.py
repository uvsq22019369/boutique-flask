from app import db

class StockMovement(db.Model):
    __tablename__ = 'stock_movements'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Références (QUOI)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    # QUI a fait le mouvement
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Optionnel : lié à une commande
    # ⚠️ COMMENTÉ TEMPORAIREMENT - on l'activera quand la table orders existera
    #order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=True)
    
    # Type de mouvement
    movement_type = db.Column(db.String(20), nullable=False)
    
    # Quantité (toujours positive, le type indique + ou -)
    quantity = db.Column(db.Integer, nullable=False)
    
    # État du stock AVANT et APRÈS (instantané)
    stock_before = db.Column(db.Integer, nullable=False)
    stock_after = db.Column(db.Integer, nullable=False)
    
    # Informations supplémentaires
    reason = db.Column(db.String(200))
    notes = db.Column(db.Text)
    
    # Horodatage
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Relations
    product = db.relationship('Product', backref='movements')
    user = db.relationship('User', backref='stock_movements')
    
    def __repr__(self):
        return f'<StockMovement {self.movement_type} {self.quantity} - Prod {self.product_id}>'
    
