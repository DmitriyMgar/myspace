from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

class CategoryForm(FlaskForm):
    """Форма создания/редактирования категории"""
    name = StringField('Название', validators=[DataRequired(), Length(min=1, max=100)])
    description = TextAreaField('Описание', validators=[Optional()])
    parent_id = SelectField('Родительская категория', validators=[Optional()], coerce=str)
    is_private = BooleanField('Приватная категория')
    icon = StringField('Иконка', validators=[Optional(), Length(max=50)], default='folder')
    submit = SubmitField('Сохранить')

class UserAccessForm(FlaskForm):
    """Форма управления доступом пользователя к категориям"""
    categories = SelectMultipleField('Доступные категории', validators=[Optional()], coerce=str)
    submit = SubmitField('Сохранить') 