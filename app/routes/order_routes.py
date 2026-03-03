from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.product import Product
from app.models.client import Client
from app.models.order import Order
from app.models.order_item import OrderItem
from app.forms.order_forms import AddToCartForm, CheckoutForm
from app.services.invoice_service import InvoiceService
from app.services.stock_service import StockService
from datetime import datetime

order_bp = Blueprint('order', __name__, url_prefix='/commandes')

@order_bp.route('/pos')
@login_required
def pos():
    """Interface caisse (Point of Sale) - Multi-boutiques"""
    form = AddToCartForm()
    
    products = Product.query.filter(
        Product.shop_id == current_user.shop_id,
        Product.stock_quantity > 0
    ).order_by(Product.name).all()
    
    clients = Client.query.filter_by(shop_id=current_user.shop_id).order_by(Client.last_name).all()
    
    cart_key = f'cart_{current_user.shop_id}'
    cart = session.get(cart_key, [])
    
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
    try:
        data = request.get_json()
        product_id = int(data.get('product_id'))
        quantity = int(data.get('quantity', 1))
        
        product = Product.query.filter_by(id=product_id, shop_id=current_user.shop_id).first_or_404()
        
        if product.stock_quantity < quantity:
            return jsonify({'success': False, 'error': 'Stock insuffisant'})
        
        cart_key = f'cart_{current_user.shop_id}'
        cart = session.get(cart_key, [])
        
        found = False
        for item in cart:
            if item['product_id'] == product_id:
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
        
        session[cart_key] = cart
        session.modified = True
        
        total = sum(item['price'] * item['quantity'] for item in cart)
        
        return jsonify({
            'success': True,
            'cart': cart,
            'total': total,
            'cart_count': len(cart)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ⭐ FONCTION CORRIGÉE - RETIRER UN ARTICLE
@order_bp.route('/api/remove-from-cart/<int:product_id>', methods=['POST'])
@login_required
def remove_from_cart(product_id):
    """Retirer un produit du panier"""
    try:
        cart_key = f'cart_{current_user.shop_id}'
        cart = session.get(cart_key, [])
        
        print(f"🔄 Panier avant suppression: {cart}")
        print(f"🆔 Produit à supprimer (reçu): {product_id} (type: {type(product_id)})")
        
        # ⭐ CORRECTION: S'assurer que product_id est un entier
        product_id_int = int(product_id)
        
        # Filtrer pour garder tous les articles SAUF celui avec product_id
        new_cart = []
        removed = False
        
        for item in cart:
            if item['product_id'] == product_id_int:
                removed = True
                print(f"✅ Article trouvé et retiré: {item}")
            else:
                new_cart.append(item)
        
        print(f"📦 Panier après suppression: {new_cart}")
        
        # Vérifier si un article a été retiré
        if not removed:
            # Afficher les IDs du panier pour déboguer
            cart_ids = [item['product_id'] for item in cart]
            print(f"❌ IDs dans le panier: {cart_ids}")
            print(f"❌ ID recherché: {product_id_int}")
            
            return jsonify({
                'success': False, 
                'error': f'Article {product_id} non trouvé dans le panier. IDs: {cart_ids}'
            }), 404
        
        session[cart_key] = new_cart
        session.modified = True
        
        total = sum(item['price'] * item['quantity'] for item in new_cart)
        
        return jsonify({
            'success': True,
            'cart': new_cart,
            'total': total,
            'cart_count': len(new_cart),
            'message': 'Article retiré avec succès'
        })
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 500

@order_bp.route('/api/clear-cart', methods=['POST'])
@login_required
def clear_cart():
    """Vider le panier"""
    try:
        cart_key = f'cart_{current_user.shop_id}'
        session[cart_key] = []
        session.modified = True
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@order_bp.route('/checkout', methods=['POST'])
@login_required
def checkout():
    """Finaliser la commande"""
    cart_key = f'cart_{current_user.shop_id}'
    cart = session.get(cart_key, [])
    
    if not cart:
        flash('Panier vide', 'warning')
        return redirect(url_for('order.pos'))
    
    form = CheckoutForm()
    form.client_id.choices = [(0, 'Client sans compte')] + [
        (c.id, c.full_name) for c in Client.query.filter_by(shop_id=current_user.shop_id).all()
    ]
    
    if form.validate_on_submit():
        # Créer la commande SANS order_number d'abord
        order = Order(
            shop_id=current_user.shop_id,
            user_id=current_user.id,
            client_id=form.client_id.data if form.client_id.data != 0 else None,
            payment_method=form.payment_method.data,
            discount=form.discount.data or 0
        )
        
        # Générer le numéro de commande APRÈS avoir assigné shop_id
        order.order_number = order.generate_order_number()
        
        db.session.add(order)
        db.session.flush()
        
        # Ajouter les items
        for item in cart:
            product = Product.query.filter_by(
                id=item['product_id'], 
                shop_id=current_user.shop_id
            ).first_or_404()
            
            order_item = OrderItem(
                order_id=order.id,
                product_id=item['product_id'],
                product_name=item['name'],
                unit_price=item['price'],
                quantity=item['quantity']
            )
            db.session.add(order_item)
            
            # Mouvement de stock
            success, message, movement = StockService.create_movement(
                product_id=item['product_id'],
                user_id=current_user.id,
                shop_id=current_user.shop_id,
                movement_type='OUT_SALE',
                quantity=item['quantity'],
                reason=f"Vente - Commande {order.order_number}",
                notes=f"Commande #{order.order_number}"
            )
            
            if not success:
                flash(f'Erreur stock: {message}', 'danger')
                db.session.rollback()
                return redirect(url_for('order.pos'))
            
            # Mettre à jour stats client
            if order.client_id:
                client = Client.query.get(order.client_id)
                if client and client.shop_id == current_user.shop_id:
                    client.purchase_count += 1
                    client.total_purchases += (item['price'] * item['quantity'])
                    client.last_purchase_date = datetime.utcnow()
        
        # Calculer les totaux
        order.calculate_totals()
        order.payment_status = 'paid'
        order.status = 'paid'
        
        db.session.commit()
        
        # Vider le panier
        session[cart_key] = []
        session.modified = True
        
        # Générer la facture
        try:
            pdf_path = InvoiceService.generate_invoice(order.id)
        except Exception as e:
            flash(f'Commande créée mais erreur facture: {str(e)}', 'warning')
        
        flash(f'✅ Commande {order.order_number} créée avec succès', 'success')
        return redirect(url_for('order.view_order', order_id=order.id))
    
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'Erreur: {error}', 'danger')
    
    return redirect(url_for('order.pos'))

@order_bp.route('/')
@login_required
def list_orders():
    """Liste des commandes de la boutique"""
    page = request.args.get('page', 1, type=int)
    orders = Order.query.filter_by(shop_id=current_user.shop_id).order_by(
        Order.created_at.desc()
    ).paginate(page=page, per_page=20)
    return render_template('orders/list.html', orders=orders)

@order_bp.route('/<int:order_id>')
@login_required
def view_order(order_id):
    """Voir les détails d'une commande"""
    order = Order.query.filter_by(id=order_id, shop_id=current_user.shop_id).first_or_404()
    return render_template('orders/view.html', order=order)

@order_bp.route('/<int:order_id>/invoice')
@login_required
def download_invoice(order_id):
    """Télécharger la facture PDF"""
    order = Order.query.filter_by(id=order_id, shop_id=current_user.shop_id).first_or_404()
    pdf_path = InvoiceService.generate_invoice(order_id)
    
    from flask import send_file
    return send_file(pdf_path, as_attachment=True, download_name=f"facture_{order.order_number}.pdf")