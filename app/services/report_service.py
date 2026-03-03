from app import db
from app.models.product import Product
from app.models.category import Category
from app.models.stock_movement import StockMovement
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.client import Client
from datetime import datetime, timedelta
import pandas as pd

class ReportService:
    """Service pour générer tous les rapports - Multi-boutiques"""
    
    @staticmethod
    def get_sales_report(shop_id, start_date=None, end_date=None):
        """Rapport des ventes sur une période pour une boutique"""
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Récupérer les commandes de la boutique
        orders = Order.query.filter(
            Order.shop_id == shop_id,
            Order.created_at >= start_date,
            Order.created_at <= end_date,
            Order.status == 'paid'
        ).all()
        
        # Statistiques
        total_orders = len(orders)
        total_revenue = sum(o.total for o in orders)
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        # Ventes par jour
        sales_by_day = {}
        for order in orders:
            day = order.created_at.strftime('%Y-%m-%d')
            if day not in sales_by_day:
                sales_by_day[day] = {'count': 0, 'revenue': 0}
            sales_by_day[day]['count'] += 1
            sales_by_day[day]['revenue'] += order.total
        
        # Top produits
        product_sales = {}
        for order in orders:
            for item in order.items:
                if item.product_name not in product_sales:
                    product_sales[item.product_name] = {
                        'quantity': 0,
                        'revenue': 0
                    }
                product_sales[item.product_name]['quantity'] += item.quantity
                product_sales[item.product_name]['revenue'] += item.subtotal
        
        top_products = sorted(
            product_sales.items(), 
            key=lambda x: x[1]['revenue'], 
            reverse=True
        )[:10]
        
        return {
            'period': {
                'start': start_date,
                'end': end_date,
                'days': (end_date - start_date).days
            },
            'summary': {
                'total_orders': total_orders,
                'total_revenue': total_revenue,
                'avg_order_value': avg_order_value
            },
            'sales_by_day': sales_by_day,
            'top_products': top_products
        }
    
    @staticmethod
    def get_stock_report(shop_id):
        """Rapport complet des stocks pour une boutique"""
        products = Product.query.filter_by(shop_id=shop_id).all()
        
        report = {
            'summary': {
                'total_products': len(products),
                'total_value': sum(p.price * p.stock_quantity for p in products),
                'low_stock_count': sum(1 for p in products if p.is_low_stock()),
                'out_of_stock_count': sum(1 for p in products if p.stock_quantity == 0)
            },
            'by_category': {},
            'products': []
        }
        
        # Par catégorie
        categories = Category.query.filter_by(shop_id=shop_id).all()
        for cat in categories:
            cat_products = [p for p in products if p.category_id == cat.id]
            report['by_category'][cat.name] = {
                'count': len(cat_products),
                'value': sum(p.price * p.stock_quantity for p in cat_products)
            }
        
        # Détail des produits
        for product in products:
            report['products'].append({
                'id': product.id,
                'name': product.name,
                'category': product.category.name,
                'price': product.price,
                'stock': product.stock_quantity,
                'value': product.price * product.stock_quantity,
                'status': product.stock_status(),
                'movements_count': len(product.stock_movements)
            })
        
        return report
    
    @staticmethod
    def get_movements_report(shop_id, days=30):
        """Rapport des mouvements pour une boutique"""
        since = datetime.now() - timedelta(days=days)
        
        movements = StockMovement.query.filter(
            StockMovement.shop_id == shop_id,
            StockMovement.created_at >= since
        ).all()
        
        report = {
            'period_days': days,
            'total_movements': len(movements),
            'by_type': {
                'IN_PURCHASE': 0,
                'IN_RETURN': 0,
                'IN_ADJUSTMENT': 0,
                'OUT_SALE': 0,
                'OUT_DAMAGED': 0,
                'OUT_RETURN': 0,
                'OUT_ADJUSTMENT': 0
            },
            'by_user': {},
            'recent': []
        }
        
        for mov in movements:
            # Par type
            report['by_type'][mov.movement_type] = report['by_type'].get(mov.movement_type, 0) + 1
            
            # Par utilisateur
            username = mov.user.username
            if username not in report['by_user']:
                report['by_user'][username] = 0
            report['by_user'][username] += 1
            
            # Récents
            if len(report['recent']) < 20:
                report['recent'].append({
                    'date': mov.created_at,
                    'product': mov.related_product.name,
                    'type': mov.movement_type,
                    'quantity': mov.quantity,
                    'user': username
                })
        
        return report
    
    @staticmethod
    def get_client_report(shop_id):
        """Rapport des clients pour une boutique"""
        clients = Client.query.filter_by(shop_id=shop_id).all()
        
        report = {
            'total_clients': len(clients),
            'total_revenue': sum(c.total_purchases for c in clients),
            'active_clients': sum(1 for c in clients if c.purchase_count > 0),
            'top_clients': []
        }
        
        # Top clients par achats
        top = sorted(clients, key=lambda c: c.total_purchases, reverse=True)[:10]
        for client in top:
            if client.total_purchases > 0:
                report['top_clients'].append({
                    'id': client.id,
                    'name': client.full_name,
                    'phone': client.phone,
                    'purchases': client.purchase_count,
                    'total': client.total_purchases
                })
        
        return report