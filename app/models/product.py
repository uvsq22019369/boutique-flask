from app import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Prix et stock
    price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, default=0)
    min_stock_alert = db.Column(db.Integer, default=5)
    
    # Multi-boutiques
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    
    # Références
    barcode = db.Column(db.String(50), unique=True, nullable=True)
    
    # Traçabilité
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relations - CORRIGÉ : backref='stock_movements' au lieu de 'movements'
    movements = db.relationship('StockMovement', backref='related_product', lazy=True, 
                               cascade='all, delete-orphan')
    
    # Contrainte d'unicité : un produit doit avoir un nom unique dans une boutique
    __table_args__ = (db.UniqueConstraint('name', 'shop_id', name='unique_product_per_shop'),)
    
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