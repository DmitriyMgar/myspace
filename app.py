"""
Основной файл приложения Flask
"""
import os
from flask import Flask
from flask_pymongo import PyMongo
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_misaka import Misaka
from flask_mail import Mail
from flask_caching import Cache
from dotenv import load_dotenv

# Импорт конфигурации
from config import config

# Инициализация расширений
mongo = PyMongo()
login_manager = LoginManager()
csrf = CSRFProtect()
md = Misaka()
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
    md.init_app(app)
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
    from routes.main import main as main_bp
    from routes.auth import auth as auth_bp
    from routes.blog import blog as blog_bp
    from routes.thesaurus import thesaurus as thesaurus_bp
    from routes.admin import admin as admin_bp
    
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
    
    return app

if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    app.run(debug=app.config['DEBUG']) 