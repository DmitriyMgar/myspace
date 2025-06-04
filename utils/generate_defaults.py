"""
Скрипт для генерации изображений по умолчанию
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import random
import numpy as np

# Добавляем родительскую директорию в путь для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_noise_texture(size=(500, 500), output_path='static/img/noise.png'):
    """Создает текстуру шума для фона"""
    # Создаем массив случайных значений
    noise = np.random.rand(size[1], size[0]) * 255
    
    # Преобразуем в изображение
    img = Image.fromarray(noise.astype(np.uint8))
    
    # Преобразуем в режим RGBA
    img = img.convert('RGBA')
    
    # Делаем шум полупрозрачным
    data = img.getdata()
    new_data = []
    for item in data:
        # Устанавливаем альфа-канал на 50
        new_data.append((item[0], item[0], item[0], 50))
    
    img.putdata(new_data)
    
    # Сохраняем изображение
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)
    print(f"Создана текстура шума: {output_path}")
    return output_path

def create_grid_background(size=(1000, 1000), output_path='static/img/grid-bg.png'):
    """Создает фон с сеткой в стиле киберпанк"""
    # Создаем черное изображение
    img = Image.new('RGB', size, color=(10, 10, 12))
    draw = ImageDraw.Draw(img)
    
    # Добавляем сетку
    grid_color = (30, 30, 40)
    grid_spacing = 50
    
    # Горизонтальные линии
    for y in range(0, size[1], grid_spacing):
        draw.line([(0, y), (size[0], y)], fill=grid_color, width=1)
    
    # Вертикальные линии
    for x in range(0, size[0], grid_spacing):
        draw.line([(x, 0), (x, size[1])], fill=grid_color, width=1)
    
    # Добавляем свечение
    img = img.filter(ImageFilter.GaussianBlur(radius=1))
    
    # Добавляем случайные яркие точки
    bright_colors = [
        (0, 255, 157, 100),    # Неоново-зеленый
        (0, 255, 255, 100),    # Неоново-голубой
        (255, 0, 160, 100)     # Неоново-розовый
    ]
    
    # Преобразуем в RGBA для поддержки прозрачности
    img = img.convert('RGBA')
    draw = ImageDraw.Draw(img)
    
    # Добавляем яркие точки
    for _ in range(50):
        x = random.randint(0, size[0])
        y = random.randint(0, size[1])
        color = random.choice(bright_colors)
        radius = random.randint(1, 3)
        draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=color)
    
    # Сохраняем изображение
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)
    print(f"Создан фон с сеткой: {output_path}")
    return output_path

def create_default_avatar(output_path='static/uploads/avatars/default.png'):
    """Создает аватар по умолчанию"""
    from utils.images import create_avatar_placeholder
    
    # Создаем директорию, если она не существует
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Создаем аватар
    create_avatar_placeholder("User", size=(300, 300), save_path=output_path)
    print(f"Создан аватар по умолчанию: {output_path}")
    return output_path

def create_default_category_image(name, output_path=None):
    """Создает изображение категории по умолчанию"""
    if output_path is None:
        output_path = f'static/uploads/categories/{name.lower().replace(" ", "_")}.png'
    
    # Создаем директорию, если она не существует
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
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
    size = (200, 200)
    img = Image.new('RGB', size, color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Добавляем сетку
    grid_color = (bg_color[0] + 20, bg_color[1] + 20, bg_color[2] + 20)
    grid_spacing = 20
    
    for x in range(0, size[0], grid_spacing):
        draw.line([(x, 0), (x, size[1])], fill=grid_color, width=1)
    
    for y in range(0, size[1], grid_spacing):
        draw.line([(0, y), (size[0], y)], fill=grid_color, width=1)
    
    # Добавляем название категории
    try:
        font_size = 30
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()
    
    # В новых версиях PIL/Pillow метод textsize устарел
    try:
        # Для новых версий PIL/Pillow
        font_bbox = font.getbbox(name)
        text_width = font_bbox[2] - font_bbox[0]
        text_height = font_bbox[3] - font_bbox[1]
    except AttributeError:
        # Для старых версий PIL/Pillow
        text_width, text_height = draw.textsize(name, font=font)
    
    text_pos = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
    draw.text(text_pos, name, fill=text_color, font=font)
    
    # Добавляем свечение
    img = img.filter(ImageFilter.GaussianBlur(radius=1))
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(1.2)
    
    # Сохраняем изображение
    img.save(output_path)
    print(f"Создано изображение категории {name}: {output_path}")
    return output_path

def create_default_post_image(title, output_path=None):
    """Создает изображение статьи по умолчанию"""
    if output_path is None:
        output_path = f'static/uploads/posts/{title.lower().replace(" ", "_")}.png'
    
    # Создаем директорию, если она не существует
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Создаем изображение
    size = (1200, 630)
    img = Image.new('RGB', size, color=(10, 10, 12))
    draw = ImageDraw.Draw(img)
    
    # Добавляем сетку
    grid_color = (30, 30, 40)
    grid_spacing = 50
    
    for x in range(0, size[0], grid_spacing):
        draw.line([(x, 0), (x, size[1])], fill=grid_color, width=1)
    
    for y in range(0, size[1], grid_spacing):
        draw.line([(0, y), (size[0], y)], fill=grid_color, width=1)
    
    # Добавляем случайные элементы
    for _ in range(20):
        x1 = random.randint(0, size[0])
        y1 = random.randint(0, size[1])
        x2 = random.randint(0, size[0])
        y2 = random.randint(0, size[1])
        color = (0, 255, 157, 100)  # Неоново-зеленый
        draw.line([(x1, y1), (x2, y2)], fill=color, width=2)
    
    # Добавляем название статьи
    try:
        font_size = 60
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()
    
    # Если название слишком длинное, разбиваем его на несколько строк
    words = title.split()
    lines = []
    current_line = []
    
    for word in words:
        current_line.append(word)
        test_line = ' '.join(current_line)
        
        # В новых версиях PIL/Pillow метод textsize устарел
        try:
            # Для новых версий PIL/Pillow
            font_bbox = font.getbbox(test_line)
            test_width = font_bbox[2] - font_bbox[0]
        except AttributeError:
            # Для старых версий PIL/Pillow
            test_width, _ = draw.textsize(test_line, font=font)
        
        if test_width > size[0] - 100:
            current_line.pop()
            lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    # Рисуем текст
    # Вычисляем общую высоту текста
    total_height = 0
    for line in lines:
        try:
            # Для новых версий PIL/Pillow
            font_bbox = font.getbbox(line)
            _, _, _, text_height = font_bbox
            total_height += text_height + 10
        except AttributeError:
            # Для старых версий PIL/Pillow
            _, text_height = draw.textsize(line, font=font)
            total_height += text_height + 10
    
    total_height -= 10  # Убираем лишний отступ после последней строки
    
    y_offset = (size[1] - total_height) // 2
    
    for line in lines:
        try:
            # Для новых версий PIL/Pillow
            font_bbox = font.getbbox(line)
            text_width = font_bbox[2] - font_bbox[0]
            text_height = font_bbox[3] - font_bbox[1]
        except AttributeError:
            # Для старых версий PIL/Pillow
            text_width, text_height = draw.textsize(line, font=font)
        
        text_pos = ((size[0] - text_width) // 2, y_offset)
        
        # Добавляем свечение (рисуем текст несколько раз с разными цветами)
        draw.text((text_pos[0]+2, text_pos[1]+2), line, fill=(0, 255, 255, 100), font=font)
        draw.text(text_pos, line, fill=(0, 255, 157), font=font)
        
        y_offset += text_height + 10
    
    # Сохраняем изображение
    img.save(output_path)
    print(f"Создано изображение статьи {title}: {output_path}")
    return output_path

def create_favicon(output_path='static/img/favicon.ico'):
    """Создает иконку сайта"""
    # Создаем изображение
    size = (32, 32)
    img = Image.new('RGB', size, color=(10, 10, 12))
    draw = ImageDraw.Draw(img)
    
    # Рисуем букву "К" в киберпанк-стиле
    draw.line([(8, 8), (8, 24)], fill=(0, 255, 157), width=3)
    draw.line([(8, 16), (20, 8)], fill=(0, 255, 157), width=3)
    draw.line([(8, 16), (20, 24)], fill=(0, 255, 157), width=3)
    
    # Добавляем свечение
    img = img.filter(ImageFilter.GaussianBlur(radius=1))
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(1.2)
    
    # Сохраняем изображение
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)
    print(f"Создана иконка сайта: {output_path}")
    return output_path

def generate_all_defaults():
    """Генерирует все изображения по умолчанию"""
    # Создаем текстуры и фоны
    create_noise_texture()
    create_grid_background()
    
    # Создаем иконку сайта
    create_favicon()
    
    # Создаем аватар по умолчанию
    create_default_avatar()
    
    # Создаем изображения для категорий
    categories = [
        "Технологии", "Наука", "Киберпанк", 
        "Программирование", "Искусство", "Игры"
    ]
    
    for category in categories:
        create_default_category_image(category)
    
    # Создаем изображения для статей
    posts = [
        "Введение в киберпанк", 
        "Основы программирования на Python", 
        "Искусственный интеллект в современном мире",
        "Виртуальная реальность: настоящее и будущее"
    ]
    
    for post in posts:
        create_default_post_image(post)
    
    print("Все изображения по умолчанию успешно созданы!")

if __name__ == "__main__":
    generate_all_defaults() 