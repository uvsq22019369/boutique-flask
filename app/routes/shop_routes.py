from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.shop import Shop
from app.models.user import User
from app.forms.shop_forms import ShopForm
from app.utils.helpers import super_admin_required

shop_bp = Blueprint('shop', __name__, url_prefix='/boutiques')

@shop_bp.route('/')
@login_required
@super_admin_required
def list_shops():
    shops = Shop.query.all()
    return render_template('shops/list.html', shops=shops)

@shop_bp.route('/ajouter', methods=['GET', 'POST'])
@login_required
@super_admin_required
def add_shop():
    form = ShopForm()
    
    if form.validate_on_submit():
        # Vérifier si le slug existe déjà
        if Shop.query.filter_by(slug=form.slug.data).first():
            flash('Ce slug est déjà utilisé', 'danger')
            return render_template('shops/form.html', form=form)
        
        # Créer la boutique
        shop = Shop(
            name=form.name.data,
            slug=form.slug.data,
            address=form.address.data,
            phone=form.phone.data,
            email=form.email.data,
            is_active=True  # ⭐ Active par défaut
        )
        db.session.add(shop)
        db.session.flush()
        
        # Créer l'admin de la boutique
        username = f"admin_{form.slug.data}"
        admin = User(
            username=username,
            email=form.admin_email.data,
            role='shop_admin',
            shop_id=shop.id,
            is_active=True
        )
        admin.password = form.admin_password.data
        db.session.add(admin)
        
        db.session.commit()
        flash(f'✅ Boutique {shop.name} créée avec succès', 'success')
        flash(f'Admin: {username} / {form.admin_password.data}', 'info')
        return redirect(url_for('shop.list_shops'))
    
    return render_template('shops/form.html', form=form, title='Ajouter une boutique')

# ⭐ NOUVEAU : Activer/Désactiver une boutique
@shop_bp.route('/toggle/<int:id>')
@login_required
@super_admin_required
def toggle_shop(id):
    """Activer ou désactiver une boutique (gestion abonnement)"""
    shop = Shop.query.get_or_404(id)
    
    # Inverser le statut
    shop.is_active = not shop.is_active
    
    # Si on désactive, on désactive aussi tous les utilisateurs de la boutique
    if not shop.is_active:
        for user in shop.users:
            user.is_active = False
        flash(f'Tous les utilisateurs de {shop.name} ont été désactivés', 'warning')
    else:
        # Si on active, on réactive les utilisateurs
        for user in shop.users:
            user.is_active = True
        flash(f'Tous les utilisateurs de {shop.name} ont été réactivés', 'success')
    
    db.session.commit()
    
    status = "activée" if shop.is_active else "désactivée"
    flash(f'✅ Boutique {shop.name} {status} avec succès', 'success')
    return redirect(url_for('shop.list_shops'))

@shop_bp.route('/supprimer/<int:id>')
@login_required
@super_admin_required
def delete_shop(id):
    shop = Shop.query.get_or_404(id)
    
    # Vérifier s'il y a des données
    if shop.products or shop.clients or shop.orders:
        flash('Impossible de supprimer : la boutique contient des données', 'danger')
        return redirect(url_for('shop.list_shops'))
    
    db.session.delete(shop)
    db.session.commit()
    flash(f'Boutique {shop.name} supprimée', 'success')
    return redirect(url_for('shop.list_shops'))