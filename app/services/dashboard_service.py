from app import db
from app.models.product import Product
from app.models.stock_movement import StockMovement
from app.models.category import Category
from app.models.order import Order
from datetime import datetime, timedelta

class DashboardService:
    """Service pour les statistiques du tableau de bord - Multi-boutiques"""
    
    @staticmethod
    def get_general_stats(shop_id):
        """Statistiques générales pour une boutique"""
        total_products = Product.query.filter_by(shop_id=shop_id).count()
        total_categories = Category.query.filter_by(shop_id=shop_id).count()
        
        # Produits en stock bas
        low_stock = Product.query.filter(
            Product.shop_id == shop_id,
            Product.stock_quantity <= Product.min_stock_alert
        ).count()
        
        # Produits en rupture
        out_of_stock = Product.query.filter(
            Product.shop_id == shop_id,
            Product.stock_quantity == 0
        ).count()
        
        # Valeur totale du stock
        products = Product.query.filter_by(shop_id=shop_id).all()
        total_value = sum(p.price * p.stock_quantity for p in products)
        
        # Commandes aujourd'hui
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_orders = Order.query.filter(
            Order.shop_id == shop_id,
            Order.created_at >= today_start,
            Order.status == 'paid'
        ).count()
        
        today_revenue = db.session.query(db.func.sum(Order.total)).filter(
            Order.shop_id == shop_id,
            Order.created_at >= today_start,
            Order.status == 'paid'
        ).scalar() or 0
        
        return {
            'total_products': total_products,
            'total_categories': total_categories,
            'low_stock': low_stock,
            'out_of_stock': out_of_stock,
            'total_value': total_value,
            'today_orders': today_orders,
            'today_revenue': today_revenue
        }
    
    @staticmethod
    def get_recent_movements(shop_id, limit=10):
        """Derniers mouvements de stock d'une boutique"""
        return StockMovement.query.filter_by(
            shop_id=shop_id
        ).order_by(
            StockMovement.created_at.desc()
        ).limit(limit).all()
    
    @staticmethod
    def get_movements_by_day(shop_id, days=7):
        """Mouvements des derniers jours (entrées vs sorties)"""
        result = []
        
        for i in range(days-1, -1, -1):
            day = datetime.now() - timedelta(days=i)
            next_day = day + timedelta(days=1)
            
            # Entrées du jour
            entries = StockMovement.query.filter(
                StockMovement.shop_id == shop_id,
                StockMovement.movement_type.startswith('IN_'),
                StockMovement.created_at >= day,
                StockMovement.created_at < next_day
            ).count()
            
            # Sorties du jour
            exits = StockMovement.query.filter(
                StockMovement.shop_id == shop_id,
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
    def get_top_products(shop_id, limit=5):
        """Produits les plus mouvementés d'une boutique"""
        from sqlalchemy import func
        
        top_products = db.session.query(
            Product.id,
            Product.name,
            func.count(StockMovement.id).label('movement_count')
        ).join(
            StockMovement, StockMovement.product_id == Product.id
        ).filter(
            Product.shop_id == shop_id
        ).group_by(
            Product.id, Product.name
        ).order_by(
            func.count(StockMovement.id).desc()
        ).limit(limit).all()
        
        return top_products
    
    @staticmethod
    def get_stock_by_category(shop_id):
        """Répartition du stock par catégorie pour une boutique"""
        categories = Category.query.filter_by(shop_id=shop_id).all()
        result = []
        
        for cat in categories:
            total = sum(p.stock_quantity for p in cat.products)
            value = sum(p.price * p.stock_quantity for p in cat.products)
            result.append({
                'name': cat.name,
                'total': total,
                'value': value
            })
        
        return result
    
    @staticmethod
    def get_sales_today(shop_id):
        """Ventes du jour pour une boutique"""
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        orders = Order.query.filter(
            Order.shop_id == shop_id,
            Order.created_at >= today_start,
            Order.status == 'paid'
        ).all()
        
        total = sum(o.total for o in orders)
        count = len(orders)
        
        return {
            'count': count,
            'total': total
        }