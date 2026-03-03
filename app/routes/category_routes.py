from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.category import Category
from app.models.shop import Shop
from app.forms.product_forms import CategoryForm
from app.utils.helpers import role_required, shop_active_required

category_bp = Blueprint('category', __name__, url_prefix='/categories')

@category_bp.route('/')
@login_required
@shop_active_required
def list_categories():
    """Liste toutes les catégories de la boutique"""
    categories = Category.query.join(Shop).filter(
        Category.shop_id == current_user.shop_id,
        Shop.is_active == True
    ).order_by(Category.name).all()
    return render_template('categories/list.html', categories=categories)

@category_bp.route('/ajouter', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'manager')
@shop_active_required
def add_category():
    """Ajouter une nouvelle catégorie"""
    form = CategoryForm()
    
    if form.validate_on_submit():
        category = Category(
            name=form.name.data,
            description=form.description.data,
            shop_id=current_user.shop_id
        )
        db.session.add(category)
        db.session.commit()
        flash('Catégorie créée avec succès', 'success')
        return redirect(url_for('category.list_categories'))
    
    return render_template('categories/form.html', form=form, title='Ajouter une catégorie')

@category_bp.route('/modifier/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'manager')
@shop_active_required
def edit_category(id):
    """Modifier une catégorie"""
    category = Category.query.join(Shop).filter(
        Category.id == id,
        Category.shop_id == current_user.shop_id,
        Shop.is_active == True
    ).first_or_404()
    
    form = CategoryForm(obj=category)
    
    if form.validate_on_submit():
        category.name = form.name.data
        category.description = form.description.data
        db.session.commit()
        flash('Catégorie modifiée avec succès', 'success')
        return redirect(url_for('category.list_categories'))
    
    return render_template('categories/form.html', form=form, title='Modifier une catégorie')

@category_bp.route('/supprimer/<int:id>')
@login_required
@role_required('admin')
@shop_active_required
def delete_category(id):
    """Supprimer une catégorie"""
    category = Category.query.join(Shop).filter(
        Category.id == id,
        Category.shop_id == current_user.shop_id,
        Shop.is_active == True
    ).first_or_404()
    
    # Vérifier si la catégorie contient des produits
    if category.products:
        flash('Impossible de supprimer : la catégorie contient des produits', 'danger')
        return redirect(url_for('category.list_categories'))
    
    db.session.delete(category)
    db.session.commit()
    flash('Catégorie supprimée avec succès', 'success')
    return redirect(url_for('category.list_categories'))