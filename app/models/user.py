from app import db, bcrypt
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    
    # Rôles étendus pour multi-boutiques
    role = db.Column(db.String(20), nullable=False, default='shop_cashier')
    # super_admin, shop_admin, shop_manager, shop_cashier
    
    # Lien vers la boutique (NULL pour super_admin)
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'), nullable=True)
    
    # Relation avec la boutique
    shop = db.relationship('Shop', backref='shop_users', lazy=True)
    
    # Statut
    is_active = db.Column(db.Boolean, default=True)
    
    # Horodatage
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    @property
    def password(self):
        raise AttributeError('password n\'est pas un attribut lisible')
    
    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def verify_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    # Méthodes de vérification des rôles
    def is_super_admin(self):
        return self.role == 'super_admin'
    
    def is_shop_admin(self):
        return self.role == 'shop_admin'
    
    def is_manager(self):
        return self.role in ['shop_admin', 'shop_manager']
    
    def has_shop(self):
        return self.shop_id is not None
    
    def can_access_shop(self, shop_id):
        """Vérifie si l'utilisateur peut accéder à une boutique"""
        if self.is_super_admin():
            return True
        return self.shop_id == shop_id
    
    def get_filtered_query(self, model):
        """Retourne une requête filtrée par boutique"""
        if self.is_super_admin():
            return model.query
        return model.query.filter_by(shop_id=self.shop_id)
    
    def __repr__(self):
        return f'<User {self.username} ({self.role})>'