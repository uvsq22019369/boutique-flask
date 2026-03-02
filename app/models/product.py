from app import db

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Prix et stock
    price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, default=0)
    min_stock_alert = db.Column(db.Integer, default=5)
    
    # Références
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    barcode = db.Column(db.String(50), unique=True, nullable=True)
    
    # Traçabilité
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, onupdate=db.func.current_timestamp())
    
    def is_low_stock(self):
        """Vérifie si le stock est bas"""
        return self.stock_quantity <= self.min_stock_alert
    
    def stock_status(self):
        """Retourne le statut du stock"""
        if self.stock_quantity <= 0:
            return 'rupture'
        elif self.stock_quantity <= self.min_stock_alert:
            return 'bas'
        else:
            return 'normal'
    
    def __repr__(self):
        return f'<Product {self.name}>'