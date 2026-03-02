from app import db
from app.models.product import Product
from app.models.stock_movement import StockMovement
from app.models.category import Category
from datetime import datetime, timedelta

class DashboardService:
    """Service pour les statistiques du tableau de bord"""
    
    @staticmethod
    def get_general_stats():
        """Statistiques générales"""
        total_products = Product.query.count()
        total_categories = Category.query.count()
        
        # Produits en stock bas
        low_stock = Product.query.filter(
            Product.stock_quantity <= Product.min_stock_alert
        ).count()
        
        # Produits en rupture
        out_of_stock = Product.query.filter(
            Product.stock_quantity == 0
        ).count()
        
        # Valeur totale du stock
        products = Product.query.all()
        total_value = sum(p.price * p.stock_quantity for p in products)
        
        return {
            'total_products': total_products,
            'total_categories': total_categories,
            'low_stock': low_stock,
            'out_of_stock': out_of_stock,
            'total_value': total_value
        }
    
    @staticmethod
    def get_recent_movements(limit=10):
        """Derniers mouvements de stock"""
        return StockMovement.query.order_by(
            StockMovement.created_at.desc()
        ).limit(limit).all()
    
    @staticmethod
    def get_movements_by_day(days=7):
        """Mouvements des derniers jours (entrées vs sorties)"""
        result = []
        
        for i in range(days-1, -1, -1):
            day = datetime.now() - timedelta(days=i)
            next_day = day + timedelta(days=1)
            
            # Entrées du jour
            entries = StockMovement.query.filter(
                StockMovement.movement_type.startswith('IN_'),
                StockMovement.created_at >= day,
                StockMovement.created_at < next_day
            ).count()
            
            # Sorties du jour
            exits = StockMovement.query.filter(
                StockMovement.movement_type.startswith('OUT_'),
                StockMovement.created_at >= day,
                StockMovement.created_at < next_day
            ).count()
            
            result.append({
                'date': day.strftime('%d/%m'),
                'entries': entries,
                'exits': exits
            })
        
        return result
    
    @staticmethod
    def get_top_products(limit=5):
        """Produits les plus mouvementés"""
        from sqlalchemy import func
        
        # Compter les mouvements par produit
        top_products = db.session.query(
            Product.id,
            Product.name,
            func.count(StockMovement.id).label('movement_count')
        ).join(
            StockMovement, StockMovement.product_id == Product.id
        ).group_by(
            Product.id, Product.name
        ).order_by(
            func.count(StockMovement.id).desc()
        ).limit(limit).all()
        
        return top_products
    
    @staticmethod
    def get_stock_by_category():
        """Répartition du stock par catégorie"""
        categories = Category.query.all()
        result = []
        
        for cat in categories:
            total = sum(p.stock_quantity for p in cat.products)
            result.append({
                'name': cat.name,
                'total': total
            })
        
        return result