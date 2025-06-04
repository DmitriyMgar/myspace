from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User
from forms.auth import LoginForm, RegisterForm, ProfileForm, PasswordChangeForm
import os
from werkzeug.utils import secure_filename
from datetime import datetime

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Страница входа"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.validate_login(current_app.db, form.email.data, form.password.data)
        
        if user:
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.index'))
        
        flash('Неверный email или пароль', 'danger')
    
    return render_template('auth/login.html', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Страница регистрации"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegisterForm()
    
    if form.validate_on_submit():
        # Проверяем, существует ли пользователь с таким email
        if User.get_by_email(current_app.db, form.email.data):
            flash('Пользователь с таким email уже существует', 'danger')
            return render_template('auth/register.html', form=form)
        
        # Проверяем, существует ли пользователь с таким именем
        if User.get_by_username(current_app.db, form.username.data):
            flash('Пользователь с таким именем уже существует', 'danger')
            return render_template('auth/register.html', form=form)
        
        # Создаем нового пользователя
        user = User.create_user(
            current_app.db,
            form.username.data,
            form.email.data,
            form.password.data
        )
        
        flash('Регистрация успешна! Теперь вы можете войти', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    """Выход из аккаунта"""
    logout_user()
    flash('Вы успешно вышли из аккаунта', 'info')
    return redirect(url_for('main.index'))

@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Страница профиля пользователя"""
    form = ProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        update_data = {
            'username': form.username.data,
            'email': form.email.data
        }
        
        # Обработка загрузки аватара
        if form.avatar.data:
            filename = secure_filename(form.avatar.data.filename)
            # Добавляем timestamp к имени файла для уникальности
            filename = f"{datetime.utcnow().timestamp()}_{filename}"
            
            # Создаем директорию для аватаров, если она не существует
            avatar_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars')
            if not os.path.exists(avatar_dir):
                os.makedirs(avatar_dir)
            
            # Сохраняем файл
            avatar_path = os.path.join(avatar_dir, filename)
            form.avatar.data.save(avatar_path)
            
            # Обновляем путь к аватару в базе данных
            update_data['profile_image'] = f"uploads/avatars/{filename}"
        
        # Обновляем профиль пользователя
        current_user.update_profile(current_app.db, update_data)
        
        flash('Профиль успешно обновлен', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/profile.html', form=form)

@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Страница изменения пароля"""
    form = PasswordChangeForm()
    
    if form.validate_on_submit():
        # Проверяем текущий пароль
        user = User.validate_login(current_app.db, current_user.email, form.current_password.data)
        
        if not user:
            flash('Текущий пароль неверен', 'danger')
            return render_template('auth/change_password.html', form=form)
        
        # Обновляем пароль
        import bcrypt
        hashed_password = bcrypt.hashpw(form.new_password.data.encode('utf-8'), bcrypt.gensalt())
        
        current_user.update_profile(current_app.db, {'password': hashed_password})
        
        flash('Пароль успешно изменен', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/change_password.html', form=form) 