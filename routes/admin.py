from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, abort
from flask_login import login_required, current_user
from models.user import User
from models.post import Post
from models.category import Category
from models.comment import Comment
from models.thesaurus import Term
from forms.admin import CategoryForm, UserAccessForm
from bson.objectid import ObjectId
from pymongo import DESCENDING

admin = Blueprint('admin', __name__)
admin_bp = admin  # Добавляем алиас для соответствия импорту в app.py

# Декоратор для проверки прав администратора
def admin_required(func):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('У вас нет доступа к этой странице', 'danger')
            return redirect(url_for('main.index'))
        return func(*args, **kwargs)
    decorated_function.__name__ = func.__name__
    return decorated_function

@admin.route('/')
@login_required
@admin_required
def index():
    """Главная страница админ-панели"""
    # Статистика
    stats = {
        'users_count': current_app.db.users.count_documents({}),
        'posts_count': current_app.db.posts.count_documents({}),
        'published_posts': current_app.db.posts.count_documents({'is_published': True}),
        'draft_posts': current_app.db.posts.count_documents({'is_published': False}),
        'categories_count': current_app.db.categories.count_documents({}),
        'comments_count': current_app.db.comments.count_documents({}),
        'terms_count': current_app.db.thesaurus.count_documents({})
    }
    
    # Последние 5 статей
    recent_posts = Post.get_posts(
        current_app.db,
        sort_by=[('created_at', -1)],
        page=1,
        per_page=5
    )['posts']
    
    # Последние 5 комментариев
    recent_comments_cursor = current_app.db.comments.find().sort('created_at', -1).limit(5)
    recent_comments = [Comment(comment_data) for comment_data in recent_comments_cursor]
    
    # Последние 5 пользователей
    recent_users_cursor = current_app.db.users.find().sort('created_at', -1).limit(5)
    recent_users = [User(user_data) for user_data in recent_users_cursor]
    
    return render_template(
        'admin/index.html',
        stats=stats,
        recent_posts=recent_posts,
        recent_comments=recent_comments,
        recent_users=recent_users
    )

@admin.route('/users')
@login_required
@admin_required
def users():
    """Управление пользователями"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Получаем пользователей с пагинацией
    skip = (page - 1) * per_page
    users_cursor = current_app.db.users.find().sort('username', 1).skip(skip).limit(per_page)
    users_list = [User(user_data) for user_data in users_cursor]
    
    total_users = current_app.db.users.count_documents({})
    
    return render_template(
        'admin/users.html',
        users=users_list,
        page=page,
        per_page=per_page,
        total=total_users,
        pages=(total_users + per_page - 1) // per_page
    )

@admin.route('/users/<user_id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    """Включение/выключение прав администратора"""
    user = User.get_by_id(current_app.db, user_id)
    if not user:
        abort(404)
    
    # Нельзя снять права администратора у самого себя
    if user.id == current_user.id:
        flash('Нельзя снять права администратора у самого себя', 'danger')
        return redirect(url_for('admin.users'))
    
    # Переключаем права администратора
    user.update_profile(current_app.db, {'is_admin': not user.is_admin})
    
    flash(f'Права администратора для пользователя {user.username} {"включены" if user.is_admin else "выключены"}', 'success')
    return redirect(url_for('admin.users'))

@admin.route('/users/<user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Удаление пользователя"""
    user = User.get_by_id(current_app.db, user_id)
    if not user:
        abort(404)
    
    # Нельзя удалить самого себя
    if user.id == current_user.id:
        flash('Нельзя удалить самого себя', 'danger')
        return redirect(url_for('admin.users'))
    
    # Удаляем все комментарии пользователя
    current_app.db.comments.delete_many({'author_id': ObjectId(user.id)})
    
    # Удаляем все реакции пользователя
    current_app.db.reactions.delete_many({'user_id': ObjectId(user.id)})
    
    # Удаляем пользователя
    current_app.db.users.delete_one({'_id': ObjectId(user.id)})
    
    flash(f'Пользователь {user.username} удален', 'success')
    return redirect(url_for('admin.users'))

@admin.route('/users/<user_id>/access', methods=['GET', 'POST'])
@login_required
@admin_required
def user_access(user_id):
    """Управление доступом пользователя к категориям"""
    user = User.get_by_id(current_app.db, user_id)
    if not user:
        abort(404)
    
    form = UserAccessForm()
    
    # Получаем все приватные категории
    private_categories = [cat for cat in Category.get_all(current_app.db, include_private=True) if cat.is_private]
    form.categories.choices = [(cat.id, cat.name) for cat in private_categories]
    
    if form.validate_on_submit():
        user.update_profile(current_app.db, {'allowed_categories': form.categories.data})
        flash(f'Доступ пользователя {user.username} обновлен', 'success')
        return redirect(url_for('admin.users'))
    
    # Заполняем выбранные категории
    form.categories.data = user.allowed_categories
    
    return render_template(
        'admin/user_access.html',
        user=user,
        form=form
    )

@admin.route('/categories')
@login_required
@admin_required
def categories():
    """Управление категориями"""
    # Получаем все категории
    categories = Category.get_all(current_app.db, include_private=True)
    
    # Группируем подкатегории по родительским категориям
    main_categories = [cat for cat in categories if not cat.parent_id]
    subcategories = {}
    
    for cat in categories:
        if cat.parent_id:
            if cat.parent_id not in subcategories:
                subcategories[cat.parent_id] = []
            subcategories[cat.parent_id].append(cat)
    
    return render_template(
        'admin/categories.html',
        main_categories=main_categories,
        subcategories=subcategories
    )

@admin.route('/categories/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_category():
    """Создание новой категории"""
    form = CategoryForm()
    
    # Заполняем выпадающий список родительских категорий
    main_categories = Category.get_main_categories(current_app.db, include_private=True)
    form.parent_id.choices = [('', 'Нет (главная категория)')] + [(cat.id, cat.name) for cat in main_categories]
    
    if form.validate_on_submit():
        parent_id = form.parent_id.data if form.parent_id.data else None
        
        category = Category.create_category(
            current_app.db,
            form.name.data,
            form.description.data,
            parent_id,
            form.is_private.data,
            form.icon.data
        )
        
        flash('Категория успешно создана', 'success')
        return redirect(url_for('admin.categories'))
    
    return render_template('admin/category_editor.html', form=form, is_new=True)

@admin.route('/categories/<category_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_category(category_id):
    """Редактирование категории"""
    category = Category.get_by_id(current_app.db, category_id)
    if not category:
        abort(404)
    
    form = CategoryForm(obj=category)
    
    # Заполняем выпадающий список родительских категорий
    main_categories = [cat for cat in Category.get_main_categories(current_app.db, include_private=True) if cat.id != category.id]
    form.parent_id.choices = [('', 'Нет (главная категория)')] + [(cat.id, cat.name) for cat in main_categories]
    
    if form.validate_on_submit():
        parent_id = form.parent_id.data if form.parent_id.data else None
        
        # Проверяем, не создается ли цикл в иерархии категорий
        if parent_id and category.id == parent_id:
            flash('Категория не может быть родительской для самой себя', 'danger')
            return render_template('admin/category_editor.html', form=form, is_new=False, category=category)
        
        update_data = {
            'name': form.name.data,
            'description': form.description.data,
            'is_private': form.is_private.data,
            'icon': form.icon.data
        }
        
        if parent_id:
            update_data['parent_id'] = parent_id
        elif category.parent_id:
            # Если категория была подкатегорией, а теперь становится главной
            current_app.db.categories.update_one(
                {'_id': ObjectId(category.id)},
                {'$unset': {'parent_id': ''}}
            )
        
        category.update(current_app.db, update_data)
        
        flash('Категория успешно обновлена', 'success')
        return redirect(url_for('admin.categories'))
    
    return render_template('admin/category_editor.html', form=form, is_new=False, category=category)

@admin.route('/categories/<category_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_category(category_id):
    """Удаление категории"""
    category = Category.get_by_id(current_app.db, category_id)
    if not category:
        abort(404)
    
    try:
        category.delete(current_app.db)
        flash('Категория успешно удалена', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
    
    return redirect(url_for('admin.categories'))

@admin.route('/posts')
@login_required
@admin_required
def posts():
    """Управление статьями"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Фильтры
    status = request.args.get('status')
    category_id = request.args.get('category_id')
    author_id = request.args.get('author_id')
    
    filter_criteria = {}
    
    if status == 'published':
        filter_criteria['is_published'] = True
    elif status == 'draft':
        filter_criteria['is_published'] = False
    
    if category_id:
        filter_criteria['category_id'] = ObjectId(category_id)
    
    if author_id:
        filter_criteria['author_id'] = ObjectId(author_id)
    
    # Получаем статьи с пагинацией
    posts_data = Post.get_posts(
        current_app.db,
        filter_criteria=filter_criteria,
        page=page,
        per_page=per_page
    )
    
    # Получаем все категории и авторов для фильтров
    categories = Category.get_all(current_app.db, include_private=True)
    
    authors_cursor = current_app.db.users.find({}, {'username': 1})
    authors = [{'id': str(user['_id']), 'username': user['username']} for user in authors_cursor]
    
    return render_template(
        'admin/posts.html',
        posts=posts_data['posts'],
        page=page,
        per_page=per_page,
        total=posts_data['total'],
        pages=posts_data['pages'],
        status=status,
        category_id=category_id,
        author_id=author_id,
        categories=categories,
        authors=authors
    )

@admin.route('/comments')
@login_required
@admin_required
def comments():
    """Управление комментариями"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Фильтры
    post_id = request.args.get('post_id')
    author_id = request.args.get('author_id')
    is_deleted = request.args.get('is_deleted')
    
    filter_criteria = {}
    
    if post_id:
        filter_criteria['post_id'] = ObjectId(post_id)
    
    if author_id:
        filter_criteria['author_id'] = ObjectId(author_id)
    
    if is_deleted == 'true':
        filter_criteria['is_deleted'] = True
    elif is_deleted == 'false':
        filter_criteria['is_deleted'] = False
    
    # Получаем комментарии с пагинацией
    skip = (page - 1) * per_page
    comments_cursor = current_app.db.comments.find(filter_criteria).sort('created_at', -1).skip(skip).limit(per_page)
    comments_list = [Comment(comment_data) for comment_data in comments_cursor]
    
    total_comments = current_app.db.comments.count_documents(filter_criteria)
    
    # Получаем информацию о статьях и авторах для комментариев
    posts_info = {}
    authors_info = {}
    
    for comment in comments_list:
        if comment.post_id not in posts_info:
            post = Post.get_by_id(current_app.db, comment.post_id)
            if post:
                posts_info[comment.post_id] = {'title': post.title, 'slug': post.slug}
            else:
                posts_info[comment.post_id] = {'title': 'Удаленная статья', 'slug': ''}
        
        if comment.author_id not in authors_info:
            author = User.get_by_id(current_app.db, comment.author_id)
            if author:
                authors_info[comment.author_id] = author.username
            else:
                authors_info[comment.author_id] = 'Удаленный пользователь'
    
    # Получаем все статьи и авторов для фильтров
    posts_cursor = current_app.db.posts.find({}, {'title': 1})
    posts = [{'id': str(post['_id']), 'title': post['title']} for post in posts_cursor]
    
    authors_cursor = current_app.db.users.find({}, {'username': 1})
    authors = [{'id': str(user['_id']), 'username': user['username']} for user in authors_cursor]
    
    return render_template(
        'admin/comments.html',
        comments=comments_list,
        page=page,
        per_page=per_page,
        total=total_comments,
        pages=(total_comments + per_page - 1) // per_page,
        post_id=post_id,
        author_id=author_id,
        is_deleted=is_deleted,
        posts=posts,
        authors=authors,
        posts_info=posts_info,
        authors_info=authors_info
    )

@admin.route('/comments/<comment_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_comment_admin(comment_id):
    """Удаление комментария (админ)"""
    comment = Comment.get_by_id(current_app.db, comment_id)
    if not comment:
        abort(404)
    
    comment.soft_delete(current_app.db)
    
    flash('Комментарий удален', 'success')
    return redirect(url_for('admin.comments'))

@admin.route('/comments/<comment_id>/hard-delete', methods=['POST'])
@login_required
@admin_required
def hard_delete_comment(comment_id):
    """Полное удаление комментария"""
    comment = Comment.get_by_id(current_app.db, comment_id)
    if not comment:
        abort(404)
    
    comment.hard_delete(current_app.db)
    
    flash('Комментарий полностью удален', 'success')
    return redirect(url_for('admin.comments'))

@admin.route('/terms')
@login_required
@admin_required
def terms():
    """Управление терминами тезауруса"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Фильтры
    category = request.args.get('category')
    
    filter_criteria = {}
    
    if category:
        filter_criteria['category'] = category
    
    # Получаем термины с пагинацией
    skip = (page - 1) * per_page
    terms_cursor = current_app.db.thesaurus.find(filter_criteria).sort('term', 1).skip(skip).limit(per_page)
    terms_list = [Term(term_data) for term_data in terms_cursor]
    
    total_terms = current_app.db.thesaurus.count_documents(filter_criteria)
    
    # Получаем все категории для фильтра
    categories = Term.get_categories(current_app.db)
    
    return render_template(
        'admin/terms.html',
        terms=terms_list,
        page=page,
        per_page=per_page,
        total=total_terms,
        pages=(total_terms + per_page - 1) // per_page,
        category=category,
        categories=categories
    ) 