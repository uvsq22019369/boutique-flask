from app import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True, nullable=False)
    
    # Multi-boutiques
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'), nullable=False)
    
    # Relations
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Montants
    subtotal = db.Column(db.Float, default=0)
    tax = db.Column(db.Float, default=0)
    discount = db.Column(db.Float, default=0)
    total = db.Column(db.Float, default=0)
    
    # Statuts
    status = db.Column(db.String(20), default='pending')
    payment_method = db.Column(db.String(20), nullable=True)
    payment_status = db.Column(db.String(20), default='unpaid')
    
    # Traçabilité
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relations
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    client = db.relationship('Client', backref='client_orders', lazy=True)
    user = db.relationship('User', backref='orders', lazy=True)
    shop = db.relationship('Shop', backref='shop_orders', lazy=True)
    
    def generate_order_number(self):
        """
        Génère un numéro de commande unique au format:
        CMD-{shop_id}-{AAAAMM}-{XXXX}
        """
        # ⭐ Compter les commandes existantes pour cette boutique
        last_order = Order.query.filter_by(shop_id=self.shop_id).order_by(Order.id.desc()).first()
        if last_order:
            # Extraire le dernier numéro
            try:
                last_num = int(last_order.order_number.split('-')[-1])
                new_num = last_num + 1
            except (ValueError, IndexError):
                new_num = 1
        else:
            new_num = 1
        
        # Formater avec 4 chiffres (0001, 0002, etc.)
        return f"CMD-{self.shop_id}-{datetime.now().strftime('%Y%m')}-{new_num:04d}"
    
    def calculate_totals(self):
        """Calcule les totaux de la commande"""
        self.subtotal = sum(item.subtotal for item in self.items)
        self.total = self.subtotal + self.tax - self.discount
        return self.total
    
    @property
    def item_count(self):
        return sum(item.quantity for item in self.items)
    
    @property
    def is_paid(self):
        return self.payment_status == 'paid'
    
    @property
    def is_cancelled(self):
        return self.status == 'cancelled'
    
    def mark_as_paid(self):
        self.payment_status = 'paid'
        self.status = 'paid'
    
    def mark_as_cancelled(self):
        self.status = 'cancelled'
        self.payment_status = 'unpaid'
    
    def __repr__(self):
        return f'<Order {self.order_number}>'