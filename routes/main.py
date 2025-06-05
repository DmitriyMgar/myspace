from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
from flask_login import current_user
from models.post import Post
from models.category import Category
from pymongo import DESCENDING

main = Blueprint('main', __name__)
main_bp = main  # Добавляем алиас для соответствия импорту в app.py

@main.route('/')
def index():
    """Главная страница"""
    # Получаем последние статьи из базы данных
    client = current_app.config['MONGO_CLIENT']
    db = client.get_database()
    latest_posts = list(db.posts.find({'status': 'published'}).sort('created_at', DESCENDING).limit(5))
    
    return render_template('index.html', posts=latest_posts)

@main.route('/search')
def search():
    """Поиск по сайту"""
    query = request.args.get('q', '')
    if not query:
        return render_template('search.html', results=[], query='')
    
    client = current_app.config['MONGO_CLIENT']
    db = client.get_database()
    
    # Поиск в статьях
    post_results = list(db.posts.find({
        '$and': [
            {'status': 'published'},
            {'$or': [
                {'title': {'$regex': query, '$options': 'i'}},
                {'content': {'$regex': query, '$options': 'i'}}
            ]}
        ]
    }).limit(10))
    
    # Поиск в терминах
    term_results = list(db.terms.find({
        '$or': [
            {'name': {'$regex': query, '$options': 'i'}},
            {'definition': {'$regex': query, '$options': 'i'}}
        ]
    }).limit(10))
    
    results = {
        'posts': post_results,
        'terms': term_results
    }
    
    return render_template('search.html', results=results, query=query)

@main.route('/about')
def about():
    """Страница 'О блоге'"""
    return render_template('about.html')

@main.route('/contact')
def contact():
    """Контактная страница"""
    return render_template('contact.html') 