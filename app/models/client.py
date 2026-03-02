from app import db
from datetime import datetime

class Client(db.Model):
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Informations personnelles
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=True)
    
    # Statistiques
    total_purchases = db.Column(db.Float, default=0)  # Montant total des achats
    purchase_count = db.Column(db.Integer, default=0)  # Nombre d'achats
    last_purchase_date = db.Column(db.DateTime, nullable=True)
    
    # Traçabilité
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relations (à décommenter quand Order sera créé)
    # orders = db.relationship('Order', backref='client', lazy=True)
    
    @property
    def full_name(self):
        """Nom complet du client"""
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f'<Client {self.full_name}>'