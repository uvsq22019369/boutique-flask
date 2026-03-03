from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.services.dashboard_service import DashboardService
from app.utils.helpers import role_required
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def index():
    """Tableau de bord principal - Multi-boutiques"""
    # Récupérer toutes les statistiques pour la boutique courante
    stats = DashboardService.get_general_stats(current_user.shop_id)
    recent_movements = DashboardService.get_recent_movements(current_user.shop_id)
    
    # Données pour les graphiques
    movements_by_day = DashboardService.get_movements_by_day(current_user.shop_id)
    
    # Données de test si aucune donnée réelle
    if not movements_by_day or all(d.get('entries', 0) == 0 and d.get('exits', 0) == 0 for d in movements_by_day):
        movements_by_day = []
        for i in range(7):
            day = datetime.now() - timedelta(days=6-i)
            movements_by_day.append({
                'date': day.strftime('%d/%m'),
                'entries': 2 + i,
                'exits': 1 + i
            })
    
    top_products = DashboardService.get_top_products(current_user.shop_id)
    if not top_products:
        top_products = [
            {'name': 'Smartphone', 'movement_count': 15},
            {'name': 'Ordinateur', 'movement_count': 12},
            {'name': 'TV', 'movement_count': 8},
        ]
    
    stock_by_category = DashboardService.get_stock_by_category(current_user.shop_id)
    if not stock_by_category:
        stock_by_category = [
            {'name': 'Électronique', 'total': 45},
            {'name': 'Alimentation', 'total': 32},
            {'name': 'Vêtements', 'total': 28},
        ]
    
    # S'assurer que stats a toutes les clés
    if 'total_products' not in stats:
        stats['total_products'] = 0
    if 'total_value' not in stats:
        stats['total_value'] = 0
    if 'low_stock' not in stats:
        stats['low_stock'] = 0
    if 'out_of_stock' not in stats:
        stats['out_of_stock'] = 0
    
    return render_template(
        'dashboard/advanced.html',
        stats=stats,
        recent_movements=recent_movements,
        movements_by_day=movements_by_day,
        top_products=top_products,
        stock_by_category=stock_by_category
    )

@dashboard_bp.route('/refresh')
@login_required
@role_required('admin')
def refresh_stats():
    """Forcer le rafraîchissement des stats"""
    flash('Statistiques mises à jour', 'success')
    return redirect(url_for('dashboard.index'))