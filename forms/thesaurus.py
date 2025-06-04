from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

class TermForm(FlaskForm):
    """Форма создания/редактирования термина"""
    term = StringField('Термин', validators=[DataRequired(), Length(min=1, max=100)])
    definition = TextAreaField('Определение', validators=[DataRequired()])
    category = SelectField('Категория', validators=[DataRequired()])
    new_category = StringField('Новая категория', validators=[Optional(), Length(min=1, max=50)])
    related_terms = SelectMultipleField('Связанные термины', validators=[Optional()], coerce=str)
    submit = SubmitField('Сохранить') 