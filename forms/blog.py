from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from flask_wtf.file import FileField, FileAllowed

class PostForm(FlaskForm):
    """Форма создания/редактирования статьи"""
    title = StringField('Заголовок', validators=[DataRequired(), Length(min=3, max=200)])
    content = TextAreaField('Содержание', validators=[DataRequired()])
    category_id = SelectField('Категория', validators=[DataRequired()], coerce=str)
    subcategory_id = SelectField('Подкатегория', validators=[Optional()], coerce=str, choices=[('', 'Нет')])
    tags = StringField('Теги (через запятую)', validators=[Optional()])
    cover_image = FileField('Обложка', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Разрешены только изображения!')
    ])
    is_published = BooleanField('Опубликовать')
    submit = SubmitField('Сохранить')

class CommentForm(FlaskForm):
    """Форма комментария"""
    content = TextAreaField('Комментарий', validators=[DataRequired(), Length(min=1, max=1000)])
    submit = SubmitField('Отправить') 