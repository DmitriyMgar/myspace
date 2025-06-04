"""
Модуль для работы с загрузкой файлов
"""
import os
import uuid
from PIL import Image
import imghdr

# Импортируем Flask только при необходимости
try:
    from flask import current_app
    has_flask = True
except ImportError:
    has_flask = False
    # Создаем заглушку для логгера
    class LoggerStub:
        def error(self, msg):
            print(f"ERROR: {msg}")
    
    # Создаем заглушку для current_app
    class AppStub:
        static_folder = "."
        logger = LoggerStub()
    
    current_app = AppStub()

# Импортируем werkzeug только при необходимости
try:
    from werkzeug.utils import secure_filename
    has_werkzeug = True
except ImportError:
    has_werkzeug = False
    
    # Создаем заглушку для secure_filename
    def secure_filename(filename):
        # Простая реализация для случаев, когда werkzeug недоступен
        return filename.replace('/', '_').replace('\\', '_')

# Разрешенные расширения файлов
ALLOWED_EXTENSIONS = {
    'images': {'png', 'jpg', 'jpeg', 'gif', 'webp'},
    'documents': {'pdf', 'doc', 'docx', 'txt', 'md'},
    'archives': {'zip', 'rar', '7z'}
}

# Максимальные размеры изображений
IMAGE_MAX_SIZE = {
    'avatar': (300, 300),
    'post_cover': (1200, 630),
    'category_icon': (200, 200),
    'term_image': (800, 600)
}

# Пути для сохранения файлов
UPLOAD_FOLDERS = {
    'avatar': 'uploads/avatars',
    'post_image': 'uploads/posts',
    'category_image': 'uploads/categories',
    'term_image': 'uploads/thesaurus'
}

def allowed_file(filename, file_type='images'):
    """Проверяет, разрешен ли файл с данным расширением"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS.get(file_type, set())

def validate_image(stream):
    """Проверяет, является ли файл действительным изображением"""
    header = stream.read(512)
    stream.seek(0)
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')

def save_file(file, file_type='avatar'):
    """
    Сохраняет загруженный файл
    
    Args:
        file: Объект загруженного файла
        file_type: Тип файла (avatar, post_image, category_image, term_image)
    
    Returns:
        str: Относительный путь к сохраненному файлу
    """
    if not file or file.filename == '':
        return None
        
    if not allowed_file(file.filename):
        return None
        
    # Проверка, что это действительно изображение
    if file_type in ['avatar', 'post_image', 'category_image', 'term_image']:
        if validate_image(file.stream) is None:
            return None
    
    # Создаем уникальное имя файла
    filename = secure_filename(file.filename)
    name, ext = os.path.splitext(filename)
    unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
    
    # Путь для сохранения
    if has_flask:
        upload_folder = os.path.join(current_app.static_folder, UPLOAD_FOLDERS.get(file_type, 'uploads'))
    else:
        upload_folder = os.path.join('static', UPLOAD_FOLDERS.get(file_type, 'uploads'))
    
    # Создаем директорию, если она не существует
    os.makedirs(upload_folder, exist_ok=True)
    
    file_path = os.path.join(upload_folder, unique_filename)
    
    # Сохраняем файл
    file.save(file_path)
    
    # Если это изображение, изменяем его размер
    if file_type in IMAGE_MAX_SIZE:
        resize_image(file_path, IMAGE_MAX_SIZE.get(file_type))
    
    # Возвращаем относительный путь для хранения в базе данных
    return os.path.join(UPLOAD_FOLDERS.get(file_type, 'uploads'), unique_filename)

def resize_image(file_path, size):
    """
    Изменяет размер изображения
    
    Args:
        file_path: Путь к файлу
        size: Кортеж (ширина, высота)
    """
    try:
        with Image.open(file_path) as img:
            # Сохраняем соотношение сторон
            img.thumbnail(size)
            img.save(file_path)
    except Exception as e:
        if has_flask:
            current_app.logger.error(f"Ошибка при изменении размера изображения: {e}")
        else:
            print(f"ERROR: Ошибка при изменении размера изображения: {e}")

def delete_file(file_path):
    """
    Удаляет файл
    
    Args:
        file_path: Относительный путь к файлу
    """
    if not file_path:
        return
        
    try:
        if has_flask:
            full_path = os.path.join(current_app.static_folder, file_path)
        else:
            full_path = os.path.join('static', file_path)
            
        if os.path.exists(full_path):
            os.remove(full_path)
    except Exception as e:
        if has_flask:
            current_app.logger.error(f"Ошибка при удалении файла: {e}")
        else:
            print(f"ERROR: Ошибка при удалении файла: {e}") 