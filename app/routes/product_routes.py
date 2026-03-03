from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.product import Product
from app.models.category import Category
from app.models.shop import Shop
from app.forms.product_forms import ProductForm
from app.utils.helpers import role_required, shop_active_required

product_bp = Blueprint('product', __name__, url_prefix='/produits')

@product_bp.route('/')
@login_required
@shop_active_required
def list_products():
    """Liste tous les produits de la boutique de l'utilisateur"""
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category', type=int)
    
    # ⭐ Filtrer par boutique ET vérifier que la boutique est active
    query = Product.query.join(Shop).filter(
        Product.shop_id == current_user.shop_id,
        Shop.is_active == True
    )
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    products = query.order_by(Product.name).paginate(page=page, per_page=20)
    
    # Filtrer les catégories par boutique aussi
    categories = Category.query.join(Shop).filter(
        Category.shop_id == current_user.shop_id,
        Shop.is_active == True
    ).all()
    
    return render_template('products/list.html', 
                         products=products, 
                         categories=categories,
                         selected_category=category_id)

@product_bp.route('/ajouter', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'manager')
@shop_active_required
def add_product():
    """Ajouter un nouveau produit"""
    form = ProductForm()
    
    # Charger les catégories de la boutique courante
    form.category_id.choices = [(c.id, c.name) for c in 
                                Category.query.join(Shop).filter(
                                    Category.shop_id == current_user.shop_id,
                                    Shop.is_active == True
                                ).order_by('name').all()]
    
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            stock_quantity=form.stock_quantity.data,
            min_stock_alert=form.min_stock_alert.data,
            category_id=form.category_id.data,
            shop_id=current_user.shop_id,
            created_by=current_user.id
        )
        
        if form.barcode.data and form.barcode.data.strip():
            product.barcode = form.barcode.data
        
        db.session.add(product)
        db.session.commit()
        flash('Produit créé avec succès', 'success')
        return redirect(url_for('product.list_products'))
    
    return render_template('products/form.html', form=form, title='Ajouter un produit')

@product_bp.route('/modifier/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'manager')
@shop_active_required
def edit_product(id):
    """Modifier un produit"""
    # Vérifier que le produit appartient bien à la boutique
    product = Product.query.join(Shop).filter(
        Product.id == id,
        Product.shop_id == current_user.shop_id,
        Shop.is_active == True
    ).first_or_404()
    
    form = ProductForm(obj=product)
    form.category_id.choices = [(c.id, c.name) for c in 
                                Category.query.join(Shop).filter(
                                    Category.shop_id == current_user.shop_id,
                                    Shop.is_active == True
                                ).order_by('name').all()]
    
    if form.validate_on_submit():
        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        product.stock_quantity = form.stock_quantity.data
        product.min_stock_alert = form.min_stock_alert.data
        product.category_id = form.category_id.data
        
        if form.barcode.data and form.barcode.data.strip():
            product.barcode = form.barcode.data
        else:
            product.barcode = None
        
        db.session.commit()
        flash('Produit modifié avec succès', 'success')
        return redirect(url_for('product.list_products'))
    
    return render_template('products/form.html', form=form, title='Modifier un produit')

@product_bp.route('/supprimer/<int:id>')
@login_required
@role_required('admin')
@shop_active_required
def delete_product(id):
    """Supprimer un produit"""
    product = Product.query.join(Shop).filter(
        Product.id == id,
        Product.shop_id == current_user.shop_id,
        Shop.is_active == True
    ).first_or_404()
    
    # Vérifier s'il a des mouvements
    if product.stock_movements:
        flash('Impossible de supprimer : le produit a des mouvements de stock', 'danger')
        return redirect(url_for('product.list_products'))
    
    db.session.delete(product)
    db.session.commit()
    flash('Produit supprimé avec succès', 'success')
    return redirect(url_for('product.list_products'))

@product_bp.route('/stock-bas')
@login_required
@shop_active_required
def low_stock():
    """Affiche les produits avec stock bas de la boutique"""
    products = Product.query.join(Shop).filter(
        Product.shop_id == current_user.shop_id,
        Shop.is_active == True,
        Product.stock_quantity <= Product.min_stock_alert
    ).order_by(Product.stock_quantity).all()
    
    return render_template('products/low_stock.html', products=products)