from app import db

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Relations
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    # Détails de la vente (copie des infos produit au moment de la vente)
    product_name = db.Column(db.String(200), nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    discount = db.Column(db.Float, default=0)  # Réduction ligne
    
    @property
    def subtotal(self):
        """Total pour cette ligne"""
        return (self.unit_price * self.quantity) - self.discount
    
    def __repr__(self):
        return f'<OrderItem {self.product_name} x{self.quantity}>'