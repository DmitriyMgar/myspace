from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from flask_wtf.file import FileField, FileAllowed

class LoginForm(FlaskForm):
    """Форма входа"""
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

class RegisterForm(FlaskForm):
    """Форма регистрации"""
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=3, max=20)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[
        DataRequired(),
        Length(min=8, message='Пароль должен содержать не менее 8 символов')
    ])
    password_confirm = PasswordField('Подтверждение пароля', validators=[
        DataRequired(),
        EqualTo('password', message='Пароли должны совпадать')
    ])
    submit = SubmitField('Зарегистрироваться')

class ProfileForm(FlaskForm):
    """Форма редактирования профиля"""
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=3, max=20)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    avatar = FileField('Аватар', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Разрешены только изображения!')
    ])
    submit = SubmitField('Сохранить')

class PasswordChangeForm(FlaskForm):
    """Форма изменения пароля"""
    current_password = PasswordField('Текущий пароль', validators=[DataRequired()])
    new_password = PasswordField('Новый пароль', validators=[
        DataRequired(),
        Length(min=8, message='Пароль должен содержать не менее 8 символов')
    ])
    new_password_confirm = PasswordField('Подтверждение нового пароля', validators=[
        DataRequired(),
        EqualTo('new_password', message='Пароли должны совпадать')
    ])
    submit = SubmitField('Изменить пароль') 