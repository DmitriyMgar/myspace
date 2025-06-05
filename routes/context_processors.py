"""
Контекстные процессоры для шаблонов Jinja
"""
from datetime import datetime
from flask import current_app
from app import mongo
from models.category import Category

def inject_categories():
    """
    Добавляет список категорий в контекст шаблонов
    
    Returns:
        dict: Словарь с категориями
    """
    # Получаем клиент MongoDB из конфигурации приложения
    client = current_app.config['MONGO_CLIENT']
    db = client.get_database()
    categories = Category.get_all(db)
    return {'categories': categories}

def inject_now():
    """
    Добавляет текущую дату и время в контекст шаблонов
    
    Returns:
        dict: Словарь с текущей датой и временем
    """
    return {'now': datetime.now}

def inject_app_config():
    """
    Добавляет некоторые настройки приложения в контекст шаблонов
    
    Returns:
        dict: Словарь с настройками приложения
    """
    return {
        'app_name': 'КиберБлог',
        'app_version': '1.0.0',
        'debug': current_app.debug
    }

def inject_helper_functions():
    """
    Добавляет вспомогательные функции в контекст шаблонов
    
    Returns:
        dict: Словарь с вспомогательными функциями
    """
    def get_user(user_id):
        """Получает пользователя по ID"""
        from models.user import User
        # Получаем клиент MongoDB из конфигурации приложения
        client = current_app.config['MONGO_CLIENT']
        db = client.get_database()
        return User.get_by_id(db, user_id)
    
    def get_post(post_id):
        """Получает статью по ID"""
        from models.post import Post
        # Получаем клиент MongoDB из конфигурации приложения
        client = current_app.config['MONGO_CLIENT']
        db = client.get_database()
        return Post.get_by_id(db, post_id)
    
    def get_user_posts(user_id, limit=None):
        """Получает статьи пользователя"""
        from models.post import Post
        # Получаем клиент MongoDB из конфигурации приложения
        client = current_app.config['MONGO_CLIENT']
        db = client.get_database()
        return Post.get_by_author(db, user_id, limit)
    
    def get_user_posts_count(user_id):
        """Получает количество статей пользователя"""
        # Используем mongo.db вместо получения из конфигурации
        return mongo.db.posts.count_documents({'author_id': user_id})
    
    def get_related_posts(post_id, category_id, limit=3):
        """Получает связанные статьи"""
        from models.post import Post
        # Получаем клиент MongoDB из конфигурации приложения
        client = current_app.config['MONGO_CLIENT']
        db = client.get_database()
        return Post.get_related(db, post_id, category_id, limit)
    
    def get_popular_posts(limit=5):
        """Получает популярные статьи"""
        from models.post import Post
        # Получаем клиент MongoDB из конфигурации приложения
        client = current_app.config['MONGO_CLIENT']
        db = client.get_database()
        return Post.get_popular(db, limit)
    
    def get_comment_replies(comment_id):
        """Получает ответы на комментарий"""
        from models.comment import Comment
        # Получаем клиент MongoDB из конфигурации приложения
        client = current_app.config['MONGO_CLIENT']
        db = client.get_database()
        return Comment.get_replies(db, comment_id)
    
    def get_popular_tags(limit=20):
        """Получает популярные теги"""
        from models.post import Post
        # Получаем клиент MongoDB из конфигурации приложения
        client = current_app.config['MONGO_CLIENT']
        db = client.get_database()
        return Post.get_popular_tags(db, limit)
    
    def get_alphabet():
        """Получает алфавит для тезауруса"""
        from models.term import Term
        # Получаем клиент MongoDB из конфигурации приложения
        client = current_app.config['MONGO_CLIENT']
        db = client.get_database()
        return Term.get_alphabet(db)
    
    return {
        'get_user': get_user,
        'get_post': get_post,
        'get_user_posts': get_user_posts,
        'get_user_posts_count': get_user_posts_count,
        'get_related_posts': get_related_posts,
        'get_popular_posts': get_popular_posts,
        'get_comment_replies': get_comment_replies,
        'get_popular_tags': get_popular_tags,
        'get_alphabet': get_alphabet
    }

def register_context_processors(app):
    """
    Регистрирует все контекстные процессоры
    
    Args:
        app: Экземпляр приложения Flask
    """
    app.context_processor(inject_categories)
    app.context_processor(inject_now)
    app.context_processor(inject_app_config)
    app.context_processor(inject_helper_functions) 