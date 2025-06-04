"""
Модуль для работы с изображениями
"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageFont
import random
import numpy as np
import logging

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

def create_avatar_placeholder(username, size=(300, 300), save_path=None):
    """
    Создает аватар-заполнитель с инициалами пользователя
    
    Args:
        username (str): Имя пользователя
        size (tuple): Размер аватара (ширина, высота)
        save_path (str): Путь для сохранения аватара
        
    Returns:
        str: Путь к созданному аватару
    """
    # Цвета в стиле киберпанк
    bg_colors = [
        (10, 10, 30),      # Темно-синий
        (20, 10, 30),      # Темно-фиолетовый
        (10, 30, 30),      # Темно-бирюзовый
        (30, 10, 20),      # Темно-бордовый
        (20, 30, 20)       # Темно-зеленый
    ]
    
    text_colors = [
        (0, 255, 157),     # Неоново-зеленый
        (0, 255, 255),     # Неоново-голубой
        (255, 0, 160),     # Неоново-розовый
        (255, 204, 0),     # Неоново-желтый
        (174, 129, 255)    # Неоново-фиолетовый
    ]
    
    # Выбираем случайные цвета
    bg_color = random.choice(bg_colors)
    text_color = random.choice(text_colors)
    
    # Создаем изображение
    img = Image.new('RGB', size, color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Получаем инициалы
    if username:
        initials = username[0].upper()
        if ' ' in username:
            parts = username.split()
            if len(parts) > 1 and parts[1]:
                initials += parts[1][0].upper()
        elif len(username) > 1:
            initials += username[1].upper()
    else:
        initials = "??"
    
    # Добавляем сетку в стиле киберпанк
    grid_color = (bg_color[0] + 20, bg_color[1] + 20, bg_color[2] + 20)
    grid_spacing = 15
    
    for x in range(0, size[0], grid_spacing):
        draw.line([(x, 0), (x, size[1])], fill=grid_color, width=1)
    
    for y in range(0, size[1], grid_spacing):
        draw.line([(0, y), (size[0], y)], fill=grid_color, width=1)
    
    # Добавляем случайные элементы в стиле киберпанк
    for _ in range(10):
        x1 = random.randint(0, size[0])
        y1 = random.randint(0, size[1])
        x2 = random.randint(0, size[0])
        y2 = random.randint(0, size[1])
        draw.line([(x1, y1), (x2, y2)], fill=text_color, width=1)
    
    # Добавляем круг для инициалов
    circle_size = min(size) * 0.6
    circle_pos = ((size[0] - circle_size) // 2, (size[1] - circle_size) // 2)
    draw.ellipse([circle_pos[0], circle_pos[1], 
                 circle_pos[0] + circle_size, circle_pos[1] + circle_size], 
                 outline=text_color, width=3)
    
    # Добавляем инициалы
    try:
        font_size = int(circle_size * 0.6)
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        # Если шрифт не найден, используем шрифт по умолчанию
        font = ImageFont.load_default()
    
    # В новых версиях PIL/Pillow метод textsize устарел
    try:
        # Для новых версий PIL/Pillow
        font_bbox = font.getbbox(initials)
        text_width = font_bbox[2] - font_bbox[0]
        text_height = font_bbox[3] - font_bbox[1]
    except AttributeError:
        # Для старых версий PIL/Pillow
        text_width, text_height = draw.textsize(initials, font=font)
    
    text_pos = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
    
    # В новых версиях PIL/Pillow метод text может иметь другие параметры
    try:
        draw.text(text_pos, initials, fill=text_color, font=font)
    except TypeError:
        # Для новых версий PIL/Pillow
        draw.text(text_pos, initials, fill=text_color, font=font)
    
    # Добавляем свечение
    img = img.filter(ImageFilter.GaussianBlur(radius=1))
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(1.2)
    
    # Сохраняем изображение
    if save_path:
        # Создаем директорию, если она не существует
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        img.save(save_path)
        return save_path
    
    # Если путь не указан, сохраняем во временный файл
    temp_filename = f"avatar_{username.lower().replace(' ', '_')}_{random.randint(1000, 9999)}.png"
    
    if has_flask:
        temp_path = os.path.join(current_app.static_folder, 'uploads/avatars', temp_filename)
    else:
        temp_path = os.path.join('static', 'uploads/avatars', temp_filename)
    
    # Создаем директорию, если она не существует
    os.makedirs(os.path.dirname(temp_path), exist_ok=True)
    img.save(temp_path)
    
    return os.path.join('uploads/avatars', temp_filename)

def apply_cyberpunk_filter(image_path, output_path=None):
    """
    Применяет киберпанк-фильтр к изображению
    
    Args:
        image_path (str): Путь к исходному изображению
        output_path (str): Путь для сохранения обработанного изображения
        
    Returns:
        str: Путь к обработанному изображению
    """
    try:
        # Открываем изображение
        img = Image.open(image_path)
        
        # Увеличиваем контрастность
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.5)
        
        # Увеличиваем насыщенность
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.8)
        
        # Добавляем свечение
        img = img.filter(ImageFilter.GaussianBlur(radius=1))
        img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
        
        # Преобразуем в массив NumPy для манипуляций с цветом
        img_array = np.array(img)
        
        # Усиливаем синие и зеленые оттенки (киберпанк-эффект)
        img_array[:, :, 0] = np.clip(img_array[:, :, 0] * 0.8, 0, 255)  # Уменьшаем красный
        img_array[:, :, 1] = np.clip(img_array[:, :, 1] * 1.2, 0, 255)  # Увеличиваем зеленый
        img_array[:, :, 2] = np.clip(img_array[:, :, 2] * 1.1, 0, 255)  # Увеличиваем синий
        
        # Преобразуем обратно в изображение
        img = Image.fromarray(img_array)
        
        # Сохраняем результат
        if output_path:
            # Создаем директорию, если она не существует
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            img.save(output_path)
            return output_path
        
        # Если выходной путь не указан, перезаписываем исходное изображение
        img.save(image_path)
        return image_path
    
    except Exception as e:
        if has_flask:
            current_app.logger.error(f"Ошибка при применении киберпанк-фильтра: {e}")
        else:
            print(f"ERROR: Ошибка при применении киберпанк-фильтра: {e}")
        return image_path  # Возвращаем исходный путь в случае ошибки 