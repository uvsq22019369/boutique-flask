from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.client import Client
from app.models.shop import Shop
from app.forms.client_forms import ClientForm
from app.utils.helpers import role_required, shop_active_required

client_bp = Blueprint('client', __name__, url_prefix='/clients')

@client_bp.route('/')
@login_required
@shop_active_required
def list_clients():
    """Liste tous les clients de la boutique"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Client.query.join(Shop).filter(
        Client.shop_id == current_user.shop_id,
        Shop.is_active == True
    )
    
    if search:
        query = query.filter(
            db.or_(
                Client.first_name.contains(search),
                Client.last_name.contains(search),
                Client.phone.contains(search),
                Client.email.contains(search)
            )
        )
    
    clients = query.order_by(Client.last_name).paginate(page=page, per_page=20)
    
    return render_template('clients/list.html', clients=clients, search=search)

@client_bp.route('/ajouter', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'manager')
@shop_active_required
def add_client():
    """Ajouter un nouveau client"""
    form = ClientForm()
    
    if form.validate_on_submit():
        client = Client(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            phone=form.phone.data,
            address=form.address.data,
            shop_id=current_user.shop_id,
            created_by=current_user.id
        )
        
        db.session.add(client)
        db.session.commit()
        
        flash(f'Client {client.full_name} ajouté avec succès', 'success')
        return redirect(url_for('client.list_clients'))
    
    return render_template('clients/form.html', form=form, title='Ajouter un client')

@client_bp.route('/modifier/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'manager')
@shop_active_required
def edit_client(id):
    """Modifier un client"""
    client = Client.query.join(Shop).filter(
        Client.id == id,
        Client.shop_id == current_user.shop_id,
        Shop.is_active == True
    ).first_or_404()
    
    form = ClientForm(obj=client)
    
    if form.validate_on_submit():
        client.first_name = form.first_name.data
        client.last_name = form.last_name.data
        client.email = form.email.data
        client.phone = form.phone.data
        client.address = form.address.data
        
        db.session.commit()
        
        flash(f'Client {client.full_name} modifié avec succès', 'success')
        return redirect(url_for('client.list_clients'))
    
    return render_template('clients/form.html', form=form, title='Modifier un client')

@client_bp.route('/supprimer/<int:id>')
@login_required
@role_required('admin')
@shop_active_required
def delete_client(id):
    """Supprimer un client"""
    client = Client.query.join(Shop).filter(
        Client.id == id,
        Client.shop_id == current_user.shop_id,
        Shop.is_active == True
    ).first_or_404()
    
    # Vérifier si le client a des commandes
    if client.orders:
        flash('Impossible de supprimer : le client a des commandes', 'danger')
        return redirect(url_for('client.list_clients'))
    
    db.session.delete(client)
    db.session.commit()
    
    flash(f'Client {client.full_name} supprimé', 'success')
    return redirect(url_for('client.list_clients'))

@client_bp.route('/<int:id>')
@login_required
@shop_active_required
def view_client(id):
    """Voir les détails d'un client"""
    client = Client.query.join(Shop).filter(
        Client.id == id,
        Client.shop_id == current_user.shop_id,
        Shop.is_active == True
    ).first_or_404()
    
    # Récupérer les commandes du client
    orders = client.orders
    
    return render_template('clients/view.html', client=client, orders=orders)