from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, FloatField, HiddenField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional

class AddToCartForm(FlaskForm):
    """Formulaire pour ajouter au panier"""
    product_id = HiddenField('ID Produit', validators=[DataRequired()])
    quantity = IntegerField('Quantité', validators=[
        DataRequired(),
        NumberRange(min=1, message='La quantité doit être supérieure à 0')
    ])
    submit = SubmitField('Ajouter au panier')

class CheckoutForm(FlaskForm):
    """Formulaire de validation de commande"""
    client_id = SelectField('Client', coerce=int, validators=[Optional()])
    payment_method = SelectField('Mode de paiement', choices=[
        ('cash', 'Espèces'),
        ('wave', 'Wave'),
        ('orange_money', 'Orange Money'),
        ('mtn_money', 'MTN Money')
    ], validators=[DataRequired()])
    discount = FloatField('Remise', default=0, validators=[
        Optional(),
        NumberRange(min=0, message='La remise doit être positive')
    ])
    submit = SubmitField('Finaliser la commande')