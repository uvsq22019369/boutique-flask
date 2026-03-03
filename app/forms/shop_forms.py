from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Optional

class ShopForm(FlaskForm):
    name = StringField('Nom de la boutique', validators=[
        DataRequired(), Length(min=2, max=100)
    ])
    slug = StringField('Identifiant unique (slug)', validators=[
        DataRequired(), Length(min=2, max=50)
    ])
    address = TextAreaField('Adresse', validators=[Optional()])
    phone = StringField('Téléphone', validators=[Optional(), Length(max=20)])
    email = StringField('Email', validators=[Optional(), Email()])
    
    # Admin de la boutique
    admin_email = StringField('Email de l\'admin', validators=[
        DataRequired(), Email()
    ])
    admin_password = StringField('Mot de passe admin', validators=[
        DataRequired(), Length(min=6)
    ])
    
    submit = SubmitField('Créer la boutique')