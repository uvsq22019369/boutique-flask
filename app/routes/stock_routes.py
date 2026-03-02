from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.product import Product
from app.models.stock_movement import StockMovement
from app.forms.stock_forms import StockMovementForm
from app.services.stock_service import StockService
from app.utils.helpers import role_required

stock_bp = Blueprint('stock', __name__, url_prefix='/stock')

@stock_bp.route('/movement/add', methods=['GET', 'POST'])
@login_required  # ⭐ Ajouter
@login_required
@role_required('admin', 'manager')
def add_movement():
    """Ajouter un mouvement de stock (entrée/sortie)"""
    form = StockMovementForm()
    
    # Charger la liste des produits pour le select
    form.product_id.choices = [(p.id, f"{p.name} (Stock: {p.stock_quantity})") 
                               for p in Product.query.order_by('name').all()]
    
    if form.validate_on_submit():
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
def history():
    """Historique global des mouvements"""
    page = request.args.get('page', 1, type=int)
    
    movements = StockMovement.query.order_by(
        StockMovement.created_at.desc()
    ).paginate(page=page, per_page=50)
    
    return render_template('stock/history.html', movements=movements)

@stock_bp.route('/product/<int:product_id>')
@login_required
def product_history(product_id):
    """Historique des mouvements pour un produit spécifique"""
    product = Product.query.get_or_404(product_id)
    
    movements = StockMovement.query.filter_by(
        product_id=product_id
    ).order_by(StockMovement.created_at.desc()).all()
    
    return render_template('stock/product_history.html', 
                         product=product, 
                         movements=movements)

@stock_bp.route('/alerts')
@login_required
def alerts():
    """Afficher les alertes de stock bas"""
    low_stock_products = Product.query.filter(
        Product.stock_quantity <= Product.min_stock_alert
    ).order_by(Product.stock_quantity).all()
    
    return render_template('stock/alerts.html', products=low_stock_products)