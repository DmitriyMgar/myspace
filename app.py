"""
Основной файл приложения Flask
"""
import os
from flask import Flask, render_template
from flask_pymongo import PyMongo
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flaskext.markdown import Markdown
from flask_mail import Mail
from flask_caching import Cache
from dotenv import load_dotenv
from pymongo import MongoClient

# Импорт конфигурации
from config import config

# Инициализация расширений
mongo = PyMongo()
login_manager = LoginManager()
csrf = CSRFProtect()
mail = Mail()
cache = Cache()

def create_app(config_name='default'):
    """
    Фабрика приложения Flask
    
    Args:
        config_name (str): Имя конфигурации ('development', 'testing', 'production')
        
    Returns:
        Flask: Экземпляр приложения Flask
    """
    # Загрузка переменных окружения
    load_dotenv()
    
    # Создание экземпляра приложения
    app = Flask(__name__)
    
    # Загрузка конфигурации
    app.config.from_object(config[config_name])
    
    # Инициализация расширений
    mongo.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    Markdown(app)
    mail.init_app(app)
    cache.init_app(app)
    
    # Настройка Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице.'
    login_manager.login_message_category = 'info'
    
    # Регистрация моделей
    from models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        """Загрузка пользователя для Flask-Login"""
        return User.get_by_id(user_id)
    
    # Регистрация маршрутов
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.blog import blog_bp
    from routes.thesaurus import thesaurus_bp
    from routes.admin import admin_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(blog_bp, url_prefix='/blog')
    app.register_blueprint(thesaurus_bp, url_prefix='/thesaurus')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Регистрация обработчиков ошибок
    from routes.errors import register_error_handlers
    register_error_handlers(app)
    
    # Регистрация контекстных процессоров
    from routes.context_processors import register_context_processors
    register_context_processors(app)
    
    # Регистрация фильтров Jinja
    from utils.jinja_filters import register_filters
    register_filters(app)
    
    # Создание директорий для загрузки файлов, если они не существуют
    os.makedirs(os.path.join(app.static_folder, 'uploads/avatars'), exist_ok=True)
    os.makedirs(os.path.join(app.static_folder, 'uploads/posts'), exist_ok=True)
    os.makedirs(os.path.join(app.static_folder, 'uploads/categories'), exist_ok=True)
    os.makedirs(os.path.join(app.static_folder, 'uploads/thesaurus'), exist_ok=True)
    
    # Подключение к MongoDB
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/cyberblog')
    client = MongoClient(mongo_uri)
    db = client.get_database()
    
    # Добавляем клиент MongoDB в конфигурацию приложения
    app.config['MONGO_CLIENT'] = client
    
    return app

if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    app.run(debug=app.config['DEBUG']) 