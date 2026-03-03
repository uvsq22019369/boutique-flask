from app import db
from datetime import datetime

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # ⭐ Multi-boutiques
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'), nullable=False)
    
    # Relation avec les produits
    products = db.relationship('Product', backref='category', lazy=True, 
                               cascade='all, delete-orphan')
    
    # Traçabilité
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Contrainte d'unicité : une catégorie doit être unique dans une boutique
    __table_args__ = (db.UniqueConstraint('name', 'shop_id', name='unique_category_per_shop'),)
    
    def __repr__(self):
        return f'<Category {self.name}>'