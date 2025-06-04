# КиберБлог

Персональная блог-платформа с киберпанк-дизайном на Flask и MongoDB.

## Особенности

- Современный киберпанк-дизайн с неоновыми элементами
- Адаптивный интерфейс для мобильных устройств
- Авторизация и регистрация пользователей
- Редактор статей с поддержкой Markdown
- Система комментариев и реакций
- Управление категориями и тегами
- Тезаурус с терминами
- Загрузка изображений с автоматической обработкой
- Административная панель для управления контентом

## Технологии

- **Backend**: Python, Flask
- **База данных**: MongoDB
- **Frontend**: HTML5, CSS3, JavaScript
- **Шаблонизатор**: Jinja2
- **Стилизация**: SCSS, CSS Grid, Flexbox
- **Работа с изображениями**: Pillow, NumPy

## Установка и запуск

### Предварительные требования

- Python 3.8+
- MongoDB

### Установка

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/yourusername/cyberblog.git
   cd cyberblog
   ```

2. Создайте виртуальное окружение и активируйте его:
   ```bash
   python -m venv venv
   # Для Windows
   venv\Scripts\activate
   # Для Linux/MacOS
   source venv/bin/activate
   ```

3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

4. Создайте файл `.env` на основе `.env.example` и настройте переменные окружения:
   ```bash
   cp .env.example .env
   ```

5. Сгенерируйте изображения по умолчанию:
   ```bash
   python utils/generate_defaults.py
   ```

### Запуск

1. Запустите MongoDB:
   ```bash
   # Для Windows
   mongod
   # Для Linux/MacOS
   sudo service mongod start
   ```

2. Запустите приложение:
   ```bash
   flask run
   ```

3. Откройте браузер и перейдите по адресу [http://localhost:5000](http://localhost:5000)

## Структура проекта

```
cyberblog/
├── app.py                  # Точка входа в приложение
├── config.py               # Конфигурация приложения
├── models/                 # Модели данных
├── routes/                 # Маршруты и представления
├── forms/                  # Формы для валидации данных
├── utils/                  # Вспомогательные функции
├── static/                 # Статические файлы (CSS, JS, изображения)
│   ├── css/                # CSS-стили
│   ├── js/                 # JavaScript-файлы
│   ├── img/                # Изображения
│   └── uploads/            # Загруженные пользователями файлы
└── templates/              # HTML-шаблоны
    ├── base.html           # Базовый шаблон
    ├── index.html          # Главная страница
    ├── auth/               # Шаблоны авторизации
    ├── blog/               # Шаблоны блога
    ├── admin/              # Шаблоны админки
    └── errors/             # Шаблоны ошибок
```

## Лицензия

MIT License 