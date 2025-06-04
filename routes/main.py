from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
from flask_login import current_user
from models.post import Post
from models.category import Category

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Главная страница блога"""
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['POSTS_PER_PAGE']
    
    # Получаем опубликованные статьи
    filter_criteria = {'is_published': True}
    
    # Если пользователь не авторизован, исключаем приватные категории
    if not current_user.is_authenticated or not current_user.is_admin:
        # Получаем ID всех приватных категорий
        private_categories = [cat.id for cat in Category.get_all(current_app.db, include_private=True) 
                             if cat.is_private]
        
        # Если пользователь авторизован, но не админ, проверяем доступ к приватным категориям
        if current_user.is_authenticated:
            allowed_private_categories = current_user.allowed_categories
            # Исключаем категории, к которым у пользователя нет доступа
            private_categories = [cat_id for cat_id in private_categories 
                                 if cat_id not in allowed_private_categories]
        
        if private_categories:
            filter_criteria['category_id'] = {'$nin': [ObjectId(cat_id) for cat_id in private_categories]}
    
    # Получаем статьи с пагинацией
    posts_data = Post.get_posts(
        current_app.db,
        filter_criteria=filter_criteria,
        page=page,
        per_page=per_page
    )
    
    # Получаем все категории для меню
    categories = Category.get_main_categories(current_app.db)
    
    return render_template(
        'index.html',
        posts=posts_data['posts'],
        total=posts_data['total'],
        page=page,
        per_page=per_page,
        pages=posts_data['pages'],
        categories=categories
    )

@main.route('/search')
def search():
    """Поиск по блогу"""
    query = request.args.get('q', '')
    if not query:
        return redirect(url_for('main.index'))
    
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['POSTS_PER_PAGE']
    
    # Создаем текстовый индекс для поиска
    current_app.db.posts.create_index([
        ('title', 'text'), 
        ('content', 'text')
    ])
    
    # Формируем критерии поиска
    filter_criteria = {
        '$text': {'$search': query},
        'is_published': True
    }
    
    # Если пользователь не авторизован, исключаем приватные категории
    if not current_user.is_authenticated or not current_user.is_admin:
        # Получаем ID всех приватных категорий
        private_categories = [cat.id for cat in Category.get_all(current_app.db, include_private=True) 
                             if cat.is_private]
        
        # Если пользователь авторизован, но не админ, проверяем доступ к приватным категориям
        if current_user.is_authenticated:
            allowed_private_categories = current_user.allowed_categories
            # Исключаем категории, к которым у пользователя нет доступа
            private_categories = [cat_id for cat_id in private_categories 
                                 if cat_id not in allowed_private_categories]
        
        if private_categories:
            filter_criteria['category_id'] = {'$nin': [ObjectId(cat_id) for cat_id in private_categories]}
    
    # Получаем статьи с пагинацией, сортируя по релевантности
    posts_data = Post.get_posts(
        current_app.db,
        filter_criteria=filter_criteria,
        sort_by=[('score', {'$meta': 'textScore'})],
        page=page,
        per_page=per_page
    )
    
    # Получаем все категории для меню
    categories = Category.get_main_categories(current_app.db)
    
    return render_template(
        'search.html',
        posts=posts_data['posts'],
        total=posts_data['total'],
        page=page,
        per_page=per_page,
        pages=posts_data['pages'],
        query=query,
        categories=categories
    )

@main.route('/about')
def about():
    """Страница 'О блоге'"""
    return render_template('about.html')

@main.route('/contact')
def contact():
    """Контактная страница"""
    return render_template('contact.html') 