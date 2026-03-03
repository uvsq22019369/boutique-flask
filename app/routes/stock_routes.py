from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.product import Product
from app.models.stock_movement import StockMovement
from app.models.shop import Shop
from app.forms.stock_forms import StockMovementForm
from app.services.stock_service import StockService
from app.utils.helpers import role_required, shop_active_required

stock_bp = Blueprint('stock', __name__, url_prefix='/stock')

@stock_bp.route('/movement/add', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'manager')
@shop_active_required
def add_movement():
    """Ajouter un mouvement de stock (entrée/sortie)"""
    form = StockMovementForm()
    
    # Charger la liste des produits de la boutique courante
    form.product_id.choices = [(p.id, f"{p.name} (Stock: {p.stock_quantity})") 
                               for p in Product.query.join(Shop).filter(
                                   Product.shop_id == current_user.shop_id,
                                   Shop.is_active == True
                               ).order_by('name').all()]
    
    if form.validate_on_submit():
        # Vérifier que le produit appartient bien à la boutique
        product = Product.query.join(Shop).filter(
            Product.id == form.product_id.data,
            Product.shop_id == current_user.shop_id,
            Shop.is_active == True
        ).first()
        
        if not product:
            flash('❌ Produit invalide', 'danger')
            return redirect(url_for('stock.add_movement'))
        
        # Utiliser le service pour créer le mouvement
        success, message, movement = StockService.create_movement(
            product_id=form.product_id.data,
            user_id=current_user.id,
            movement_type=form.movement_type.data,
            quantity=form.quantity.data,
            reason=form.reason.data,
            notes=form.notes.data
        )
        
        if success:
            flash(f'✅ {message}', 'success')
            return redirect(url_for('stock.history'))
        else:
            flash(f'❌ {message}', 'danger')
    
    return render_template('stock/movement.html', form=form)

@stock_bp.route('/history')
@login_required
@shop_active_required
def history():
    """Historique global des mouvements de la boutique"""
    page = request.args.get('page', 1, type=int)
    
    # Filtrer par boutique
    movements = StockMovement.query.join(Shop).filter(
        StockMovement.shop_id == current_user.shop_id,
        Shop.is_active == True
    ).order_by(
        StockMovement.created_at.desc()
    ).paginate(page=page, per_page=50)
    
    return render_template('stock/history.html', movements=movements)

@stock_bp.route('/product/<int:product_id>')
@login_required
@shop_active_required
def product_history(product_id):
    """Historique des mouvements pour un produit spécifique"""
    # Vérifier que le produit appartient à la boutique
    product = Product.query.join(Shop).filter(
        Product.id == product_id,
        Product.shop_id == current_user.shop_id,
        Shop.is_active == True
    ).first_or_404()
    
    movements = StockMovement.query.filter_by(
        product_id=product_id,
        shop_id=current_user.shop_id
    ).order_by(StockMovement.created_at.desc()).all()
    
    return render_template('stock/product_history.html', 
                         product=product, 
                         movements=movements)

@stock_bp.route('/alerts')
@login_required
@shop_active_required
def alerts():
    """Afficher les alertes de stock bas de la boutique"""
    low_stock_products = Product.query.join(Shop).filter(
        Product.shop_id == current_user.shop_id,
        Shop.is_active == True,
        Product.stock_quantity <= Product.min_stock_alert
    ).order_by(Product.stock_quantity).all()
    
    return render_template('stock/alerts.html', products=low_stock_products)

@stock_bp.route('/api/product/<int:product_id>/stock')
@login_required
@shop_active_required
def api_product_stock(product_id):
    """API pour obtenir le stock d'un produit (AJAX)"""
    product = Product.query.join(Shop).filter(
        Product.id == product_id,
        Product.shop_id == current_user.shop_id,
        Shop.is_active == True
    ).first_or_404()
    
    return jsonify({
        'stock': product.stock_quantity,
        'name': product.name,
        'price': product.price
    })