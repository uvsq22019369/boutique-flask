from app import db
from app.models.product import Product
from app.models.stock_movement import StockMovement
from app.models.user import User
from datetime import datetime

class StockService:
    """Service pour gérer toute la logique de stock"""
    
    @staticmethod
    def create_movement(product_id, user_id, movement_type, quantity, 
                        reason=None, notes=None):
        """
        Crée un mouvement de stock et met à jour le produit
        
        Args:
            product_id: ID du produit
            user_id: ID de l'utilisateur qui fait le mouvement
            movement_type: Type de mouvement (IN_PURCHASE, OUT_SALE, etc.)
            quantity: Quantité (toujours positive)
            reason: Raison du mouvement (optionnel)
            notes: Notes supplémentaires (optionnel)
        
        Returns:
            (success, message, movement_object)
        """
        try:
            # Récupérer le produit
            product = Product.query.get(product_id)
            if not product:
                return False, "Produit non trouvé", None
            
            # Vérifier l'utilisateur
            user = User.query.get(user_id)
            if not user:
                return False, "Utilisateur non trouvé", None
            
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
            
            # Créer le mouvement (sans order_id pour l'instant)
            movement = StockMovement(
                product_id=product_id,
                user_id=user_id,
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
    def create_entry(product_id, user_id, quantity, reason=None, notes=None):
        """Raccourci pour créer une entrée de stock (achat)"""
        return StockService.create_movement(
            product_id=product_id,
            user_id=user_id,
            movement_type='IN_PURCHASE',
            quantity=quantity,
            reason=reason,
            notes=notes
        )
    
    @staticmethod
    def create_sale(product_id, user_id, quantity, reason=None, notes=None):
        """Raccourci pour créer une sortie de stock (vente)"""
        return StockService.create_movement(
            product_id=product_id,
            user_id=user_id,
            movement_type='OUT_SALE',
            quantity=quantity,
            reason=reason,
            notes=notes
        )
    
    @staticmethod
    def create_damaged(product_id, user_id, quantity, reason=None, notes=None):
        """Raccourci pour créer une sortie de stock (produit endommagé)"""
        return StockService.create_movement(
            product_id=product_id,
            user_id=user_id,
            movement_type='OUT_DAMAGED',
            quantity=quantity,
            reason=reason or "Produit endommagé",
            notes=notes
        )
    
    @staticmethod
    def get_product_stock_history(product_id):
        """Récupère l'historique complet d'un produit"""
        return StockMovement.query.filter_by(
            product_id=product_id
        ).order_by(StockMovement.created_at.desc()).all()
    
    @staticmethod
    def get_movements_by_product(product_id, limit=None):
        """Récupère les mouvements d'un produit avec limite optionnelle"""
        query = StockMovement.query.filter_by(
            product_id=product_id
        ).order_by(StockMovement.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def get_movements_by_user(user_id, limit=None):
        """Récupère les mouvements effectués par un utilisateur"""
        query = StockMovement.query.filter_by(
            user_id=user_id
        ).order_by(StockMovement.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def get_movements_by_date_range(start_date, end_date):
        """Récupère les mouvements entre deux dates"""
        return StockMovement.query.filter(
            StockMovement.created_at >= start_date,
            StockMovement.created_at <= end_date
        ).order_by(StockMovement.created_at.desc()).all()
    
    @staticmethod
    def get_low_stock_products(threshold=None):
        """
        Récupère tous les produits en stock bas
        Si threshold est fourni, utilise ce seuil au lieu de min_stock_alert
        """
        if threshold:
            return Product.query.filter(
                Product.stock_quantity <= threshold
            ).all()
        else:
            return Product.query.filter(
                Product.stock_quantity <= Product.min_stock_alert
            ).all()
    
    @staticmethod
    def get_out_of_stock_products():
        """Récupère tous les produits en rupture de stock"""
        return Product.query.filter(
            Product.stock_quantity == 0
        ).all()
    
    @staticmethod
    def get_stock_value():
        """Calcule la valeur totale du stock"""
        products = Product.query.all()
        total = sum(p.price * p.stock_quantity for p in products)
        return total
    
    @staticmethod
    def get_stock_value_by_category():
        """Calcule la valeur du stock par catégorie"""
        from app.models.category import Category
        
        categories = Category.query.all()
        result = []
        
        for cat in categories:
            value = sum(p.price * p.stock_quantity for p in cat.products)
            result.append({
                'category': cat.name,
                'value': value,
                'count': len(cat.products)
            })
        
        return result
    
    @staticmethod
    def check_stock_alert(product_id):
        """Vérifie si un produit est en stock bas et retourne un booléen"""
        product = Product.query.get(product_id)
        if not product:
            return False
        return product.stock_quantity <= product.min_stock_alert
    
    @staticmethod
    def get_recent_movements(limit=10):
        """Récupère les derniers mouvements"""
        return StockMovement.query.order_by(
            StockMovement.created_at.desc()
        ).limit(limit).all()
    
    @staticmethod
    def get_movements_count_by_type(movement_type, days=30):
        """Compte le nombre de mouvements d'un certain type sur X jours"""
        from datetime import datetime, timedelta
        
        since = datetime.now() - timedelta(days=days)
        
        return StockMovement.query.filter(
            StockMovement.movement_type == movement_type,
            StockMovement.created_at >= since
        ).count()