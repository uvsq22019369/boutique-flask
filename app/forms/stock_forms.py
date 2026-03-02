from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional

class StockMovementForm(FlaskForm):
    """Formulaire pour les entrées/sorties de stock"""
    
    product_id = SelectField('Produit', coerce=int, validators=[DataRequired()])
    
    movement_type = SelectField('Type de mouvement', choices=[
        ('IN_PURCHASE', '📦 Entrée - Achat fournisseur'),
        ('IN_RETURN', '🔄 Entrée - Retour client'),
        ('IN_ADJUSTMENT', '📊 Entrée - Ajustement inventaire'),
        ('OUT_SALE', '💰 Sortie - Vente'),
        ('OUT_DAMAGED', '⚠️ Sortie - Produit endommagé'),
        ('OUT_RETURN', '📤 Sortie - Retour fournisseur'),
        ('OUT_ADJUSTMENT', '📊 Sortie - Ajustement inventaire')
    ], validators=[DataRequired()])
    
    quantity = IntegerField('Quantité', validators=[
        DataRequired(),
        NumberRange(min=1, message='La quantité doit être supérieure à 0')
    ])
    
    reason = StringField('Raison (optionnel)', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])
    
    submit = SubmitField('Enregistrer le mouvement')