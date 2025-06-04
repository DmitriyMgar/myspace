"""
Конфигурация приложения Flask
"""
import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    """Базовый класс конфигурации"""
    # Основные настройки Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'супер-секретный-ключ-для-разработки'
    DEBUG = False
    TESTING = False
    
    # Настройки для MongoDB
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/cyberblog'
    MONGO_DBNAME = os.environ.get('MONGO_DBNAME') or 'cyberblog'
    
    # Настройки для Flask-Mail
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.googlemail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') or True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@cyberblog.com'
    
    # Настройки для загрузки файлов
    UPLOAD_FOLDER = os.path.join('static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 МБ максимальный размер файла
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Настройки для сессий
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Настройки для Flask-WTF
    WTF_CSRF_ENABLED = True
    
    # Настройки для Pygments (подсветка синтаксиса)
    PYGMENTS_STYLE = 'monokai'
    
    # Настройки для Flask-Misaka (Markdown)
    MISAKA_EXTENSIONS = [
        'tables',
        'fenced-code',
        'footnotes',
        'strikethrough',
        'underline',
        'highlight',
        'quote',
        'superscript',
        'math'
    ]
    
    # Настройки для пагинации
    POSTS_PER_PAGE = 6
    COMMENTS_PER_PAGE = 10
    
    # Настройки для API
    API_TOKEN_EXPIRATION = timedelta(days=30)
    
    # Настройки для категорий статей
    DEFAULT_CATEGORIES = [
        'Личные записи',
        'Рецензии',
        'Размышления',
        'Data Science',
        'Machine Learning',
        'Программирование'
    ]
    
    # Настройки для реакций
    REACTION_TYPES = [
        {'name': 'like', 'emoji': '❤️', 'description': 'Нравится'},
        {'name': 'fire', 'emoji': '🔥', 'description': 'Огонь!'},
        {'name': 'thinking', 'emoji': '🤔', 'description': 'Интересно...'},
        {'name': 'wow', 'emoji': '😮', 'description': 'Вау!'},
        {'name': 'genius', 'emoji': '🧠', 'description': 'Гениально!'}
    ]
    
    # Настройки кэширования
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300  # 5 минут


class DevelopmentConfig(Config):
    """Конфигурация для разработки"""
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Конфигурация для тестирования"""
    DEBUG = False
    TESTING = True
    MONGO_URI = 'mongodb://localhost:27017/cyberblog_test'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Конфигурация для продакшена"""
    DEBUG = False
    TESTING = False
    
    # В продакшене SECRET_KEY должен быть установлен через переменную окружения
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Настройки для безопасности
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True


# Словарь доступных конфигураций
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 