"""
Фильтры для шаблонов Jinja
"""
import re
import markdown
from datetime import datetime
from flask import Markup
from bs4 import BeautifulSoup
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

def format_datetime(value, format='%d.%m.%Y %H:%M'):
    """
    Форматирует дату и время
    
    Args:
        value: Дата и время
        format: Формат даты и времени
    
    Returns:
        str: Отформатированная дата и время
    """
    if isinstance(value, datetime):
        return value.strftime(format)
    return value

def time_ago(value):
    """
    Форматирует дату и время в виде "5 минут назад"
    
    Args:
        value: Дата и время
    
    Returns:
        str: Отформатированная дата и время
    """
    if not isinstance(value, datetime):
        return value
    
    now = datetime.now()
    diff = now - value
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return 'только что'
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f'{minutes} {"минуту" if minutes == 1 else "минуты" if 2 <= minutes <= 4 else "минут"} назад'
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f'{hours} {"час" if hours == 1 else "часа" if 2 <= hours <= 4 else "часов"} назад'
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f'{days} {"день" if days == 1 else "дня" if 2 <= days <= 4 else "дней"} назад'
    else:
        return format_datetime(value)

def markdown_to_html(text):
    """
    Преобразует Markdown в HTML
    
    Args:
        text: Текст в формате Markdown
    
    Returns:
        str: HTML
    """
    if not text:
        return ''
    
    # Обработка блоков кода
    pattern = r'```(\w+)?\n(.*?)```'
    
    def replace_code_block(match):
        language = match.group(1) or 'text'
        code = match.group(2)
        
        try:
            lexer = get_lexer_by_name(language, stripall=True)
        except:
            lexer = get_lexer_by_name('text', stripall=True)
            
        formatter = HtmlFormatter(cssclass='highlight')
        result = highlight(code, lexer, formatter)
        return result
    
    text = re.sub(pattern, replace_code_block, text, flags=re.DOTALL)
    
    # Преобразуем оставшийся Markdown в HTML
    html = markdown.markdown(text, extensions=['tables', 'fenced_code', 'codehilite', 'nl2br'])
    
    return Markup(html)

def truncate_html(html, length=100, ellipsis='...'):
    """
    Обрезает HTML-текст до указанной длины
    
    Args:
        html: HTML-текст
        length: Максимальная длина текста
        ellipsis: Символы, добавляемые в конце обрезанного текста
    
    Returns:
        str: Обрезанный HTML-текст
    """
    if not html:
        return ''
    
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text()
    
    if len(text) <= length:
        return html
    
    return text[:length] + ellipsis

def nl2br(text):
    """
    Заменяет переносы строк на <br>
    
    Args:
        text: Текст
    
    Returns:
        str: Текст с заменёнными переносами строк
    """
    if not text:
        return ''
    
    return Markup(text.replace('\n', '<br>'))

def register_filters(app):
    """
    Регистрирует все фильтры
    
    Args:
        app: Экземпляр приложения Flask
    """
    app.jinja_env.filters['datetime'] = format_datetime
    app.jinja_env.filters['time_ago'] = time_ago
    app.jinja_env.filters['markdown'] = markdown_to_html
    app.jinja_env.filters['truncate_html'] = truncate_html
    app.jinja_env.filters['nl2br'] = nl2br 