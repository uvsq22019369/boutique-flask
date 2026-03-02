from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.product import Product
from app.models.category import Category
from app.forms.product_forms import ProductForm
from app.utils.helpers import role_required

product_bp = Blueprint('product', __name__, url_prefix='/produits')

@product_bp.route('/')
@login_required  # ⭐ Ajouter
@login_required
def list_products():
    """Liste tous les produits"""
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category', type=int)
    
    query = Product.query
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    products = query.order_by(Product.name).paginate(page=page, per_page=20)
    categories = Category.query.all()
    
    return render_template('products/list.html', 
                         products=products, 
                         categories=categories,
                         selected_category=category_id)

@product_bp.route('/ajouter', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'manager')
def add_product():
    """Ajouter un nouveau produit"""
    form = ProductForm()
    
    # Charger les catégories pour le select
    form.category_id.choices = [(c.id, c.name) for c in Category.query.order_by('name').all()]
    
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            stock_quantity=form.stock_quantity.data,
            min_stock_alert=form.min_stock_alert.data,
            category_id=form.category_id.data,
            barcode=form.barcode.data,
            created_by=current_user.id
        )
        db.session.add(product)
        db.session.commit()
        flash('Produit créé avec succès', 'success')
        return redirect(url_for('product.list_products'))
    
    return render_template('products/form.html', form=form, title='Ajouter un produit')

@product_bp.route('/modifier/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'manager')
def edit_product(id):
    """Modifier un produit"""
    product = Product.query.get_or_404(id)
    form = ProductForm(obj=product)
    
    form.category_id.choices = [(c.id, c.name) for c in Category.query.order_by('name').all()]
    
    if form.validate_on_submit():
        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        product.stock_quantity = form.stock_quantity.data
        product.min_stock_alert = form.min_stock_alert.data
        product.category_id = form.category_id.data
        product.barcode = form.barcode.data
        db.session.commit()
        flash('Produit modifié avec succès', 'success')
        return redirect(url_for('product.list_products'))
    
    return render_template('products/form.html', form=form, title='Modifier un produit')

@product_bp.route('/supprimer/<int:id>')
@login_required
@role_required('admin')
def delete_product(id):
    """Supprimer un produit"""
    product = Product.query.get_or_404(id)
    
    # Ici on pourrait vérifier si le produit a des mouvements de stock
    # Mais on fera ça plus tard
    
    db.session.delete(product)
    db.session.commit()
    flash('Produit supprimé avec succès', 'success')
    return redirect(url_for('product.list_products'))

@product_bp.route('/stock-bas')
@login_required
def low_stock():
    """Affiche les produits avec stock bas"""
    products = Product.query.filter(
        Product.stock_quantity <= Product.min_stock_alert
    ).order_by(Product.stock_quantity).all()
    
    return render_template('products/low_stock.html', products=products)