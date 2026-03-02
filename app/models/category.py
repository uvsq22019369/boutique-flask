from app import db

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    
    # Relation avec les produits (une catégorie a plusieurs produits)
    products = db.relationship('Product', backref='category', lazy=True)
    
    # Traçabilité
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, onupdate=db.func.current_timestamp())
    
    def __repr__(self):
        return f'<Category {self.name}>'