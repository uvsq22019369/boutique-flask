from app import db
from datetime import datetime

class Shop(db.Model):
    __tablename__ = 'shops'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    address = db.Column(db.Text, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    logo = db.Column(db.String(200), nullable=True)
    
    # ⭐ STATUT DE LA BOUTIQUE (pour abonnement)
    is_active = db.Column(db.Boolean, default=True)
    
    # Configuration
    currency = db.Column(db.String(10), default='FCFA')
    timezone = db.Column(db.String(50), default='Africa/Dakar')
    
    # Statistiques
    total_users = db.Column(db.Integer, default=0)
    total_products = db.Column(db.Integer, default=0)
    total_categories = db.Column(db.Integer, default=0)
    total_clients = db.Column(db.Integer, default=0)
    total_orders = db.Column(db.Integer, default=0)
    
    # Dates
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relations
    users = db.relationship('User', backref='shop_ref', lazy=True, cascade='all, delete-orphan')
    products = db.relationship('Product', backref='shop', lazy=True, cascade='all, delete-orphan')
    categories = db.relationship('Category', backref='shop', lazy=True, cascade='all, delete-orphan')
    clients = db.relationship('Client', backref='shop', lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='shop_ref', lazy=True, cascade='all, delete-orphan')
    stock_movements = db.relationship('StockMovement', backref='shop', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Shop {self.name}>'