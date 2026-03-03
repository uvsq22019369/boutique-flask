from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def role_required(*roles):
    """Décorateur pour restreindre l'accès selon le rôle"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Vous devez être connecté', 'warning')
                return redirect(url_for('auth.login'))
            
            allowed_roles = []
            for role in roles:
                if role == 'admin':
                    allowed_roles.extend(['admin', 'shop_admin', 'super_admin'])
                elif role == 'manager':
                    allowed_roles.extend(['manager', 'shop_manager'])
                else:
                    allowed_roles.append(role)
            
            if current_user.role not in allowed_roles:
                flash('Accès non autorisé', 'danger')
                return redirect(url_for('main.dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def super_admin_required(f):
    """Décorateur pour restreindre l'accès aux super admins uniquement"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Vous devez être connecté', 'warning')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_super_admin():
            flash('Accès réservé au super administrateur', 'danger')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function

# ⭐ NOUVEAU : Vérifier que la boutique est active
def shop_active_required(f):
    """Vérifie que la boutique de l'utilisateur est active"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Veuillez vous connecter', 'warning')
            return redirect(url_for('auth.login'))
        
        if current_user.is_super_admin():
            return f(*args, **kwargs)
        
        if not current_user.has_shop():
            flash('Vous n\'êtes pas associé à une boutique', 'danger')
            return redirect(url_for('main.index'))
        
        # Vérifier si la boutique est active
        if not current_user.shop.is_active:
            flash('Votre boutique est désactivée. Veuillez contacter l\'administrateur.', 'danger')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function