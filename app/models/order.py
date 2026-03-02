from app import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True, nullable=False)
    
    # Relations
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Montants
    subtotal = db.Column(db.Float, default=0)  # Total HT
    tax = db.Column(db.Float, default=0)       # Taxes
    discount = db.Column(db.Float, default=0)  # Réduction
    total = db.Column(db.Float, default=0)     # Total TTC
    
    # Statuts
    status = db.Column(db.String(20), default='pending')  # pending, paid, cancelled
    payment_method = db.Column(db.String(20), nullable=True)  # cash, wave, orange_money, mtn_money
    payment_status = db.Column(db.String(20), default='unpaid')  # unpaid, paid
    
    # Traçabilité
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relations
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    client = db.relationship('Client', backref='orders', lazy=True)
    user = db.relationship('User', backref='orders', lazy=True)  # ⭐ Relation avec l'utilisateur
    
    def generate_order_number(self):
        """
        Génère un numéro de commande unique au format:
        CMD-AAAAMM-XXXX (ex: CMD-202603-0001)
        """
        last_order = Order.query.order_by(Order.id.desc()).first()
        if last_order:
            last_num = int(last_order.order_number.split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1
        
        # Formater avec 4 chiffres (0001, 0002, etc.)
        return f"CMD-{datetime.now().strftime('%Y%m')}-{new_num:04d}"
    
    def calculate_totals(self):
        """Calcule les totaux de la commande à partir des items"""
        self.subtotal = sum(item.subtotal for item in self.items)
        self.total = self.subtotal + self.tax - self.discount
        return self.total
    
    @property
    def item_count(self):
        """Nombre total d'articles dans la commande"""
        return sum(item.quantity for item in self.items)
    
    @property
    def is_paid(self):
        """Vérifie si la commande est payée"""
        return self.payment_status == 'paid'
    
    @property
    def is_cancelled(self):
        """Vérifie si la commande est annulée"""
        return self.status == 'cancelled'
    
    def mark_as_paid(self):
        """Marque la commande comme payée"""
        self.payment_status = 'paid'
        self.status = 'paid'
    
    def mark_as_cancelled(self):
        """Annule la commande"""
        self.status = 'cancelled'
        self.payment_status = 'unpaid'
    
    def __repr__(self):
        return f'<Order {self.order_number}>'