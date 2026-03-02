from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

class CategoryForm(FlaskForm):
    name = StringField('Nom de la catégorie', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    description = TextAreaField('Description', validators=[Optional()])
    submit = SubmitField('Enregistrer')

class ProductForm(FlaskForm):
    name = StringField('Nom du produit', validators=[
        DataRequired(),
        Length(min=2, max=200)
    ])
    description = TextAreaField('Description', validators=[Optional()])
    price = FloatField('Prix de vente', validators=[
        DataRequired(),
        NumberRange(min=0, message='Le prix doit être positif')
    ])
    stock_quantity = IntegerField('Quantité en stock', validators=[
        DataRequired(),
        NumberRange(min=0, message='La quantité doit être positive')
    ])
    min_stock_alert = IntegerField('Seuil d\'alerte', validators=[
        DataRequired(),
        NumberRange(min=1, message='Le seuil doit être au moins 1')
    ])
    category_id = SelectField('Catégorie', coerce=int, validators=[DataRequired()])
    barcode = StringField('Code-barres', validators=[Optional()])
    submit = SubmitField('Enregistrer')