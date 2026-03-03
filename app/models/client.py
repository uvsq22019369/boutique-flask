from app import db
from datetime import datetime

class Client(db.Model):
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Informations personnelles
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=True)
    
    # ⭐ Multi-boutiques
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'), nullable=False)
    
    # Statistiques
    total_purchases = db.Column(db.Float, default=0)  # Montant total des achats
    purchase_count = db.Column(db.Integer, default=0)  # Nombre d'achats
    last_purchase_date = db.Column(db.DateTime, nullable=True)
    
    # Traçabilité
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relations
    orders = db.relationship('Order', backref='related_client', lazy=True, cascade='all, delete-orphan')
    
    # Contrainte d'unicité : un client doit avoir un téléphone unique dans une boutique
    __table_args__ = (db.UniqueConstraint('phone', 'shop_id', name='unique_phone_per_shop'),)
    
    @property
    def full_name(self):
        """Nom complet du client"""
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f'<Client {self.full_name}>'