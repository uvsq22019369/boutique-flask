from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Optional
from app.models.client import Client

class ClientForm(FlaskForm):
    """Formulaire pour ajouter/modifier un client"""
    
    first_name = StringField('Prénom', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    
    last_name = StringField('Nom', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    
    email = StringField('Email', validators=[
        Optional(),
        Email()
    ])
    
    phone = StringField('Téléphone', validators=[
        DataRequired(),
        Length(min=8, max=20)
    ])
    
    address = TextAreaField('Adresse', validators=[Optional()])
    
    submit = SubmitField('Enregistrer')