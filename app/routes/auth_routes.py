from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt
from app.models.user import User
from app.forms.auth_forms import LoginForm, RegistrationForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

""" @auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    #Page de connexion
    # Si l'utilisateur est déjà connecté, rediriger vers dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        # Chercher l'utilisateur
        user = User.query.filter_by(username=form.username.data).first()
        
        # Vérifier le mot de passe
        if user and user.verify_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Connexion réussie !', 'success')
            
            # Rediriger vers la page demandée ou dashboard
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard.index'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect', 'danger')
    
    return render_template('auth/login.html', form=form) """

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Page d'inscription"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        # Créer le nouvel utilisateur (rôle par défaut: caissier)
        user = User(
            username=form.username.data,
            email=form.email.data,
            role='cashier'  # Par défaut, pas admin
        )
        user.password = form.password.data  # Le setter va hasher
        
        db.session.add(user)
        db.session.commit()
        
        flash('Compte créé avec succès ! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """Déconnexion"""
    logout_user()
    flash('Vous avez été déconnecté', 'info')
    return redirect(url_for('main.index'))