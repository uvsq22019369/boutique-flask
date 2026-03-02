from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.product import Product
from app.models.client import Client
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.stock_movement import StockMovement
from app.forms.order_forms import AddToCartForm, CheckoutForm
from app.services.invoice_service import InvoiceService
from app.services.stock_service import StockService
from datetime import datetime
import json

order_bp = Blueprint('order', __name__, url_prefix='/commandes')

# Panier en session
@order_bp.route('/pos')
@login_required
def pos():
    """Interface caisse (Point of Sale)"""
    form = AddToCartForm()
    products = Product.query.filter(Product.stock_quantity > 0).order_by(Product.name).all()
    clients = Client.query.order_by(Client.last_name).all()
    
    # Récupérer le panier de la session
    cart = session.get('cart', [])
    
    # Calculer le total
    total = sum(item['price'] * item['quantity'] for item in cart)
    
    return render_template('pos/index.html', 
                         products=products, 
                         clients=clients,
                         cart=cart, 
                         total=total,
                         form=form)

@order_bp.route('/api/add-to-cart', methods=['POST'])
@login_required
def add_to_cart():
    """API pour ajouter un produit au panier (AJAX)"""
    product_id = request.json.get('product_id')
    quantity = int(request.json.get('quantity', 1))
    
    product = Product.query.get_or_404(product_id)
    
    # Vérifier le stock
    if product.stock_quantity < quantity:
        return jsonify({'success': False, 'error': 'Stock insuffisant'})
    
    # Récupérer le panier
    cart = session.get('cart', [])
    
    # Vérifier si le produit est déjà dans le panier
    found = False
    for item in cart:
        if item['product_id'] == product_id:
            # Vérifier le stock pour la nouvelle quantité
            if product.stock_quantity < item['quantity'] + quantity:
                return jsonify({'success': False, 'error': 'Stock insuffisant'})
            item['quantity'] += quantity
            found = True
            break
    
    if not found:
        cart.append({
            'product_id': product_id,
            'name': product.name,
            'price': product.price,
            'quantity': quantity
        })
    
    session['cart'] = cart
    session.modified = True
    
    # Calculer le nouveau total
    total = sum(item['price'] * item['quantity'] for item in cart)
    
    return jsonify({
        'success': True,
        'cart': cart,
        'total': total,
        'cart_count': len(cart)
    })

@order_bp.route('/api/remove-from-cart/<int:product_id>', methods=['POST'])
@login_required
def remove_from_cart(product_id):
    """Retirer un produit du panier"""
    cart = session.get('cart', [])
    cart = [item for item in cart if item['product_id'] != product_id]
    session['cart'] = cart
    session.modified = True
    
    total = sum(item['price'] * item['quantity'] for item in cart)
    
    return jsonify({
        'success': True,
        'cart': cart,
        'total': total,
        'cart_count': len(cart)
    })

@order_bp.route('/api/clear-cart', methods=['POST'])
@login_required
def clear_cart():
    """Vider le panier"""
    session['cart'] = []
    session.modified = True
    return jsonify({'success': True})

# ⭐ FONCTION CHECKOUT CORRIGÉE (SANS order_id)
@order_bp.route('/checkout', methods=['POST'])
@login_required
def checkout():
    """Finaliser la commande"""
    cart = session.get('cart', [])
    
    if not cart:
        flash('Panier vide', 'warning')
        return redirect(url_for('order.pos'))
    
    form = CheckoutForm()
    form.client_id.choices = [(0, 'Client sans compte')] + [(c.id, c.full_name) for c in Client.query.all()]
    
    if form.validate_on_submit():
        # Créer la commande
        order = Order(
            order_number=Order().generate_order_number(),
            user_id=current_user.id,
            client_id=form.client_id.data if form.client_id.data != 0 else None,
            payment_method=form.payment_method.data,
            discount=form.discount.data or 0
        )
        db.session.add(order)
        db.session.flush()  # Pour obtenir l'ID de la commande
        
        # Ajouter les items et mettre à jour le stock
        for item in cart:
            product = Product.query.get(item['product_id'])
            
            # Créer l'item de commande
            order_item = OrderItem(
                order_id=order.id,
                product_id=item['product_id'],
                product_name=item['name'],
                unit_price=item['price'],
                quantity=item['quantity']
            )
            db.session.add(order_item)
            
            # ⭐ CRÉER LE MOUVEMENT DE STOCK (SANS order_id)
            success, message, movement = StockService.create_movement(
                product_id=item['product_id'],
                user_id=current_user.id,
                movement_type='OUT_SALE',
                quantity=item['quantity'],
                reason=f"Vente - Commande {order.order_number}",
                notes=f"Commande #{order.order_number}"  # On met l'info dans notes
            )
            
            if not success:
                flash(f'Erreur stock: {message}', 'danger')
                db.session.rollback()
                return redirect(url_for('order.pos'))
            
            # Mettre à jour les stats du client si client existant
            if order.client_id:
                client = Client.query.get(order.client_id)
                client.purchase_count += 1
                client.total_purchases += (item['price'] * item['quantity'])
                client.last_purchase_date = datetime.utcnow()
        
        # Calculer les totaux
        order.calculate_totals()
        
        # Marquer comme payé
        order.payment_status = 'paid'
        order.status = 'paid'
        
        db.session.commit()
        
        # Vider le panier
        session['cart'] = []
        session.modified = True
        
        # Générer la facture
        try:
            pdf_path = InvoiceService.generate_invoice(order.id)
        except Exception as e:
            flash(f'Commande créée mais erreur facture: {str(e)}', 'warning')
        
        flash(f'✅ Commande {order.order_number} créée avec succès', 'success')
        return redirect(url_for('order.view_order', order_id=order.id))
    
    # Si erreur de formulaire
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'Erreur: {error}', 'danger')
    
    return redirect(url_for('order.pos'))

@order_bp.route('/')
@login_required
def list_orders():
    """Liste des commandes"""
    page = request.args.get('page', 1, type=int)
    orders = Order.query.order_by(Order.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('orders/list.html', orders=orders)

@order_bp.route('/<int:order_id>')
@login_required
def view_order(order_id):
    """Voir les détails d'une commande"""
    order = Order.query.get_or_404(order_id)
    return render_template('orders/view.html', order=order)

@order_bp.route('/<int:order_id>/invoice')
@login_required
def download_invoice(order_id):
    """Télécharger la facture PDF"""
    order = Order.query.get_or_404(order_id)
    pdf_path = InvoiceService.generate_invoice(order_id)
    
    from flask import send_file
    return send_file(pdf_path, as_attachment=True, download_name=f"facture_{order.order_number}.pdf")