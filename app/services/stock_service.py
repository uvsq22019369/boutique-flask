from app import db
from app.models.product import Product
from app.models.stock_movement import StockMovement
from app.models.user import User
from datetime import datetime

class StockService:
    """Service pour gérer toute la logique de stock - Multi-boutiques"""
    
    @staticmethod
    def create_movement(product_id, user_id, movement_type, quantity, 
                        reason=None, notes=None, shop_id=None):
        """
        Crée un mouvement de stock et met à jour le produit
        Version multi-boutiques avec shop_id
        """
        try:
            # Récupérer le produit (avec vérification shop_id)
            product = Product.query.get(product_id)
            if not product:
                return False, "Produit non trouvé", None
            
            # Vérifier l'utilisateur
            user = User.query.get(user_id)
            if not user:
                return False, "Utilisateur non trouvé", None
            
            # Utiliser le shop_id du produit si non fourni
            if not shop_id:
                shop_id = product.shop_id
            
            # Vérifier que le produit appartient bien à la boutique
            if product.shop_id != shop_id:
                return False, "Produit n'appartient pas à cette boutique", None
            
            # Vérifier que la quantité est positive
            if quantity <= 0:
                return False, "La quantité doit être supérieure à 0", None
            
            # Sauvegarder l'état avant
            stock_before = product.stock_quantity
            
            # Calculer le nouveau stock selon le type
            if movement_type.startswith('IN_'):
                # ENTRÉE de stock
                product.stock_quantity += quantity
                
            elif movement_type.startswith('OUT_'):
                # SORTIE de stock
                if product.stock_quantity < quantity:
                    return False, f"Stock insuffisant. Disponible: {product.stock_quantity}", None
                product.stock_quantity -= quantity
            else:
                return False, "Type de mouvement invalide", None
            
            # Créer le mouvement avec shop_id
            movement = StockMovement(
                product_id=product_id,
                user_id=user_id,
                shop_id=shop_id,  # ⭐ Important
                movement_type=movement_type,
                quantity=quantity,
                stock_before=stock_before,
                stock_after=product.stock_quantity,
                reason=reason,
                notes=notes
            )
            
            db.session.add(movement)
            db.session.commit()
            
            return True, "Mouvement enregistré avec succès", movement
            
        except Exception as e:
            db.session.rollback()
            return False, f"Erreur: {str(e)}", None
    
    @staticmethod
    def create_entry(product_id, user_id, quantity, reason=None, notes=None, shop_id=None):
        """Raccourci pour créer une entrée de stock"""
        return StockService.create_movement(
            product_id=product_id,
            user_id=user_id,
            shop_id=shop_id,
            movement_type='IN_PURCHASE',
            quantity=quantity,
            reason=reason,
            notes=notes
        )
    
    @staticmethod
    def create_sale(product_id, user_id, quantity, reason=None, notes=None, shop_id=None):
        """Raccourci pour créer une sortie de stock (vente)"""
        return StockService.create_movement(
            product_id=product_id,
            user_id=user_id,
            shop_id=shop_id,
            movement_type='OUT_SALE',
            quantity=quantity,
            reason=reason,
            notes=notes
        )
    
    @staticmethod
    def create_damaged(product_id, user_id, quantity, reason=None, notes=None, shop_id=None):
        """Raccourci pour créer une sortie de stock (produit endommagé)"""
        return StockService.create_movement(
            product_id=product_id,
            user_id=user_id,
            shop_id=shop_id,
            movement_type='OUT_DAMAGED',
            quantity=quantity,
            reason=reason or "Produit endommagé",
            notes=notes
        )
    
    @staticmethod
    def get_product_stock_history(product_id, shop_id):
        """Récupère l'historique complet d'un produit"""
        return StockMovement.query.filter_by(
            product_id=product_id,
            shop_id=shop_id
        ).order_by(StockMovement.created_at.desc()).all()
    
    @staticmethod
    def get_movements_by_product(product_id, shop_id, limit=None):
        """Récupère les mouvements d'un produit avec limite"""
        query = StockMovement.query.filter_by(
            product_id=product_id,
            shop_id=shop_id
        ).order_by(StockMovement.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def get_movements_by_user(user_id, shop_id, limit=None):
        """Récupère les mouvements effectués par un utilisateur"""
        query = StockMovement.query.filter_by(
            user_id=user_id,
            shop_id=shop_id
        ).order_by(StockMovement.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def get_movements_by_date_range(start_date, end_date, shop_id):
        """Récupère les mouvements entre deux dates"""
        return StockMovement.query.filter(
            StockMovement.shop_id == shop_id,
            StockMovement.created_at >= start_date,
            StockMovement.created_at <= end_date
        ).order_by(StockMovement.created_at.desc()).all()
    
    @staticmethod
    def get_low_stock_products(shop_id, threshold=None):
        """Récupère tous les produits en stock bas d'une boutique"""
        if threshold:
            return Product.query.filter(
                Product.shop_id == shop_id,
                Product.stock_quantity <= threshold
            ).all()
        else:
            return Product.query.filter(
                Product.shop_id == shop_id,
                Product.stock_quantity <= Product.min_stock_alert
            ).all()
    
    @staticmethod
    def get_out_of_stock_products(shop_id):
        """Récupère tous les produits en rupture d'une boutique"""
        return Product.query.filter(
            Product.shop_id == shop_id,
            Product.stock_quantity == 0
        ).all()
    
    @staticmethod
    def get_stock_value(shop_id):
        """Calcule la valeur totale du stock d'une boutique"""
        products = Product.query.filter_by(shop_id=shop_id).all()
        total = sum(p.price * p.stock_quantity for p in products)
        return total
    
    @staticmethod
    def get_recent_movements(shop_id, limit=10):
        """Récupère les derniers mouvements d'une boutique"""
        return StockMovement.query.filter_by(
            shop_id=shop_id
        ).order_by(
            StockMovement.created_at.desc()
        ).limit(limit).all()
    
    @staticmethod
    def get_movements_count_by_type(shop_id, movement_type, days=30):
        """Compte le nombre de mouvements d'un certain type sur X jours"""
        from datetime import datetime, timedelta
        
        since = datetime.now() - timedelta(days=days)
        
        return StockMovement.query.filter(
            StockMovement.shop_id == shop_id,
            StockMovement.movement_type == movement_type,
            StockMovement.created_at >= since
        ).count()