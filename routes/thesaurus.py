from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, abort
from flask_login import login_required, current_user
from models.thesaurus import Term
from forms.thesaurus import TermForm
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from bson.objectid import ObjectId
from pymongo import ASCENDING

thesaurus = Blueprint('thesaurus', __name__)
thesaurus_bp = thesaurus  # Добавляем алиас для соответствия импорту в app.py

@thesaurus.route('/')
def index():
    """Главная страница тезауруса"""
    # Получаем все категории терминов
    categories = Term.get_categories(current_app.db)
    
    # Получаем термины, сгруппированные по первой букве
    letters = {}
    terms = Term.get_all(current_app.db)
    
    for term in terms:
        first_letter = term.term[0].upper()
        if first_letter not in letters:
            letters[first_letter] = []
        letters[first_letter].append(term)
    
    # Сортируем буквы
    sorted_letters = sorted(letters.keys())
    
    return render_template(
        'thesaurus/index.html',
        categories=categories,
        letters=sorted_letters,
        terms_by_letter=letters
    )

@thesaurus.route('/category/<category>')
def category(category):
    """Термины по категории"""
    # Получаем все термины в категории
    terms = Term.get_by_category(current_app.db, category)
    
    # Получаем все категории для меню
    categories = Term.get_categories(current_app.db)
    
    return render_template(
        'thesaurus/category.html',
        terms=terms,
        current_category=category,
        categories=categories
    )

@thesaurus.route('/term/<slug>')
def term(slug):
    """Страница термина"""
    term = Term.get_by_slug(current_app.db, slug)
    if not term:
        abort(404)
    
    # Получаем связанные термины
    related_terms = []
    for related_id in term.related_terms:
        related_term = Term.get_by_id(current_app.db, related_id)
        if related_term:
            related_terms.append(related_term)
    
    # Получаем все категории для меню
    categories = Term.get_categories(current_app.db)
    
    return render_template(
        'thesaurus/term.html',
        term=term,
        related_terms=related_terms,
        categories=categories
    )

@thesaurus.route('/search')
def search():
    """Поиск терминов"""
    query = request.args.get('q', '')
    if not query:
        return redirect(url_for('thesaurus.index'))
    
    # Ищем термины
    terms = Term.search(current_app.db, query)
    
    # Получаем все категории для меню
    categories = Term.get_categories(current_app.db)
    
    return render_template(
        'thesaurus/search.html',
        terms=terms,
        query=query,
        categories=categories
    )

@thesaurus.route('/new', methods=['GET', 'POST'])
@login_required
def new_term():
    """Создание нового термина"""
    # Только администраторы могут создавать термины
    if not current_user.is_admin:
        flash('У вас нет прав для создания терминов', 'danger')
        return redirect(url_for('thesaurus.index'))
    
    form = TermForm()
    
    # Получаем все термины для выбора связанных
    all_terms = Term.get_all(current_app.db)
    form.related_terms.choices = [(term.id, term.term) for term in all_terms]
    
    # Получаем все категории для выбора
    categories = Term.get_categories(current_app.db)
    form.category.choices = [(cat, cat) for cat in categories]
    # Добавляем возможность создать новую категорию
    form.category.choices.append(('new', 'Создать новую категорию'))
    
    if form.validate_on_submit():
        category = form.category.data
        if category == 'new' and form.new_category.data:
            category = form.new_category.data
        
        term = Term.create_term(
            current_app.db,
            form.term.data,
            form.definition.data,
            current_user.id,
            category,
            form.related_terms.data
        )
        
        flash('Термин успешно создан', 'success')
        return redirect(url_for('thesaurus.term', slug=term.slug))
    
    return render_template('thesaurus/editor.html', form=form, is_new=True)

@thesaurus.route('/edit/<slug>', methods=['GET', 'POST'])
@login_required
def edit_term(slug):
    """Редактирование термина"""
    # Только администраторы могут редактировать термины
    if not current_user.is_admin:
        flash('У вас нет прав для редактирования терминов', 'danger')
        return redirect(url_for('thesaurus.index'))
    
    term = Term.get_by_slug(current_app.db, slug)
    if not term:
        abort(404)
    
    form = TermForm(obj=term)
    
    # Получаем все термины для выбора связанных
    all_terms = Term.get_all(current_app.db)
    form.related_terms.choices = [(t.id, t.term) for t in all_terms if t.id != term.id]
    
    # Получаем все категории для выбора
    categories = Term.get_categories(current_app.db)
    form.category.choices = [(cat, cat) for cat in categories]
    # Добавляем возможность создать новую категорию
    form.category.choices.append(('new', 'Создать новую категорию'))
    
    if form.validate_on_submit():
        category = form.category.data
        if category == 'new' and form.new_category.data:
            category = form.new_category.data
        
        update_data = {
            'term': form.term.data,
            'definition': form.definition.data,
            'category': category,
            'related_terms': form.related_terms.data
        }
        
        term.update(current_app.db, update_data)
        
        flash('Термин успешно обновлен', 'success')
        return redirect(url_for('thesaurus.term', slug=term.slug))
    
    # Заполняем выбранные связанные термины
    form.related_terms.data = term.related_terms
    
    return render_template('thesaurus/editor.html', form=form, is_new=False, term=term)

@thesaurus.route('/delete/<slug>', methods=['POST'])
@login_required
def delete_term(slug):
    """Удаление термина"""
    # Только администраторы могут удалять термины
    if not current_user.is_admin:
        flash('У вас нет прав для удаления терминов', 'danger')
        return redirect(url_for('thesaurus.index'))
    
    term = Term.get_by_slug(current_app.db, slug)
    if not term:
        abort(404)
    
    term.delete(current_app.db)
    
    flash('Термин успешно удален', 'success')
    return redirect(url_for('thesaurus.index')) 