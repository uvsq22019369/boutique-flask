from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.shop import Shop

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Page d'accueil publique"""
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Redirection vers le dashboard avancé"""
    from flask import redirect, url_for
    return redirect(url_for('dashboard.index'))

@main_bp.route('/shop-info')
@login_required
def shop_info():
    """Afficher les informations de la boutique (optionnel)"""
    if current_user.shop_id:
        shop = Shop.query.get(current_user.shop_id)
        return f"Boutique: {shop.name}"
    return "Super Admin - Toutes les boutiques"