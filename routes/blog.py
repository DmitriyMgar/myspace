from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, abort
from flask_login import login_required, current_user
from models.post import Post
from models.category import Category
from models.comment import Comment
from models.reaction import Reaction
from models.user import User
from forms.blog import PostForm, CommentForm
from bson.objectid import ObjectId
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from slugify import slugify

blog = Blueprint('blog', __name__)

@blog.route('/')
def index():
    """Список всех статей блога"""
    return redirect(url_for('main.index'))

@blog.route('/category/<slug>')
def category(slug):
    """Список статей в категории"""
    category = Category.get_by_slug(current_app.db, slug)
    if not category:
        abort(404)
    
    # Проверяем доступ к приватной категории
    if category.is_private:
        if not current_user.is_authenticated:
            flash('У вас нет доступа к этой категории', 'warning')
            return redirect(url_for('main.index'))
        
        if not current_user.is_admin and not current_user.has_access_to_category(category.id):
            flash('У вас нет доступа к этой категории', 'warning')
            return redirect(url_for('main.index'))
    
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['POSTS_PER_PAGE']
    
    # Получаем статьи из этой категории и всех её подкатегорий
    subcategories = Category.get_subcategories(current_app.db, category.id)
    subcategory_ids = [ObjectId(subcat.id) for subcat in subcategories]
    
    filter_criteria = {
        'is_published': True,
        '$or': [
            {'category_id': ObjectId(category.id)},
            {'category_id': {'$in': subcategory_ids}}
        ]
    }
    
    # Получаем статьи с пагинацией
    posts_data = Post.get_posts(
        current_app.db,
        filter_criteria=filter_criteria,
        page=page,
        per_page=per_page
    )
    
    # Получаем все категории для меню
    categories = Category.get_main_categories(current_app.db)
    
    return render_template(
        'blog/category.html',
        category=category,
        subcategories=subcategories,
        posts=posts_data['posts'],
        total=posts_data['total'],
        page=page,
        per_page=per_page,
        pages=posts_data['pages'],
        categories=categories
    )

@blog.route('/post/<slug>', methods=['GET', 'POST'])
def post(slug):
    """Просмотр статьи"""
    post = Post.get_by_slug(current_app.db, slug)
    if not post:
        abort(404)
    
    # Проверяем доступ к статье в приватной категории
    category = Category.get_by_id(current_app.db, post.category_id)
    if category and category.is_private:
        if not current_user.is_authenticated:
            flash('У вас нет доступа к этой статье', 'warning')
            return redirect(url_for('main.index'))
        
        if not current_user.is_admin and not current_user.has_access_to_category(category.id):
            flash('У вас нет доступа к этой статье', 'warning')
            return redirect(url_for('main.index'))
    
    # Увеличиваем счетчик просмотров
    post.increment_view(current_app.db)
    
    # Получаем автора статьи
    author = User.get_by_id(current_app.db, post.author_id)
    
    # Получаем комментарии к статье
    comments = Comment.get_comments_for_post(current_app.db, post.id)
    
    # Получаем реакции к статье
    reactions_count = Reaction.count_reactions_by_type(current_app.db, post.id)
    user_reaction = None
    if current_user.is_authenticated:
        user_reaction = Reaction.get_user_reaction(current_app.db, current_user.id, post.id)
    
    # Форма для комментариев
    form = CommentForm()
    
    if form.validate_on_submit() and current_user.is_authenticated:
        Comment.create_comment(
            current_app.db,
            form.content.data,
            current_user.id,
            post.id
        )
        flash('Комментарий добавлен', 'success')
        return redirect(url_for('blog.post', slug=post.slug))
    
    # Получаем все категории для меню
    categories = Category.get_main_categories(current_app.db)
    
    return render_template(
        'blog/post.html',
        post=post,
        author=author,
        category=category,
        comments=comments,
        form=form,
        reactions_count=reactions_count,
        user_reaction=user_reaction.reaction_type if user_reaction else None,
        reaction_types=current_app.config['REACTION_TYPES'],
        categories=categories
    )

@blog.route('/new', methods=['GET', 'POST'])
@login_required
def new_post():
    """Создание новой статьи"""
    form = PostForm()
    
    # Заполняем выпадающий список категорий
    categories = Category.get_all(current_app.db, include_private=current_user.is_admin)
    form.category_id.choices = [(cat.id, cat.name) for cat in categories if not cat.parent_id]
    
    if form.validate_on_submit():
        # Проверяем доступ к категории
        category = Category.get_by_id(current_app.db, form.category_id.data)
        if category.is_private and not current_user.is_admin and not current_user.has_access_to_category(category.id):
            flash('У вас нет доступа к этой категории', 'warning')
            return redirect(url_for('blog.new_post'))
        
        # Обработка загрузки обложки
        cover_image = None
        if form.cover_image.data:
            filename = secure_filename(form.cover_image.data.filename)
            # Добавляем timestamp к имени файла для уникальности
            filename = f"{datetime.utcnow().timestamp()}_{filename}"
            
            # Создаем директорию для обложек, если она не существует
            covers_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'covers')
            if not os.path.exists(covers_dir):
                os.makedirs(covers_dir)
            
            # Сохраняем файл
            cover_path = os.path.join(covers_dir, filename)
            form.cover_image.data.save(cover_path)
            
            cover_image = f"uploads/covers/{filename}"
        
        # Создаем новую статью
        post = Post.create_post(
            current_app.db,
            form.title.data,
            form.content.data,
            current_user.id,
            form.category_id.data,
            form.subcategory_id.data if form.subcategory_id.data else None,
            form.tags.data.split(',') if form.tags.data else [],
            cover_image,
            form.is_published.data
        )
        
        flash('Статья успешно создана', 'success')
        return redirect(url_for('blog.post', slug=post.slug))
    
    return render_template('blog/editor.html', form=form, is_new=True)

@blog.route('/edit/<slug>', methods=['GET', 'POST'])
@login_required
def edit_post(slug):
    """Редактирование статьи"""
    post = Post.get_by_slug(current_app.db, slug)
    if not post:
        abort(404)
    
    # Проверяем права на редактирование
    if not current_user.is_admin and post.author_id != current_user.id:
        flash('У вас нет прав на редактирование этой статьи', 'danger')
        return redirect(url_for('blog.post', slug=post.slug))
    
    form = PostForm(obj=post)
    
    # Заполняем выпадающий список категорий
    categories = Category.get_all(current_app.db, include_private=current_user.is_admin)
    form.category_id.choices = [(cat.id, cat.name) for cat in categories if not cat.parent_id]
    
    # Заполняем выпадающий список подкатегорий, если выбрана категория
    if post.category_id:
        subcategories = Category.get_subcategories(current_app.db, post.category_id)
        if subcategories:
            form.subcategory_id.choices = [(subcat.id, subcat.name) for subcat in subcategories]
    
    # Преобразуем список тегов в строку
    if post.tags:
        form.tags.data = ','.join(post.tags)
    
    if form.validate_on_submit():
        # Проверяем доступ к категории
        category = Category.get_by_id(current_app.db, form.category_id.data)
        if category.is_private and not current_user.is_admin and not current_user.has_access_to_category(category.id):
            flash('У вас нет доступа к этой категории', 'warning')
            return redirect(url_for('blog.edit_post', slug=post.slug))
        
        update_data = {
            'title': form.title.data,
            'content': form.content.data,
            'category_id': form.category_id.data,
            'is_published': form.is_published.data,
            'tags': form.tags.data.split(',') if form.tags.data else []
        }
        
        if form.subcategory_id.data:
            update_data['subcategory_id'] = form.subcategory_id.data
        
        # Обработка загрузки обложки
        if form.cover_image.data:
            filename = secure_filename(form.cover_image.data.filename)
            # Добавляем timestamp к имени файла для уникальности
            filename = f"{datetime.utcnow().timestamp()}_{filename}"
            
            # Создаем директорию для обложек, если она не существует
            covers_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'covers')
            if not os.path.exists(covers_dir):
                os.makedirs(covers_dir)
            
            # Сохраняем файл
            cover_path = os.path.join(covers_dir, filename)
            form.cover_image.data.save(cover_path)
            
            update_data['cover_image'] = f"uploads/covers/{filename}"
        
        # Обновляем статью
        post.update(current_app.db, update_data)
        
        flash('Статья успешно обновлена', 'success')
        return redirect(url_for('blog.post', slug=post.slug))
    
    return render_template('blog/editor.html', form=form, is_new=False, post=post)

@blog.route('/delete/<slug>', methods=['POST'])
@login_required
def delete_post(slug):
    """Удаление статьи"""
    post = Post.get_by_slug(current_app.db, slug)
    if not post:
        abort(404)
    
    # Проверяем права на удаление
    if not current_user.is_admin and post.author_id != current_user.id:
        flash('У вас нет прав на удаление этой статьи', 'danger')
        return redirect(url_for('blog.post', slug=post.slug))
    
    post.delete(current_app.db)
    
    flash('Статья успешно удалена', 'success')
    return redirect(url_for('main.index'))

@blog.route('/comment/<comment_id>/reply', methods=['POST'])
@login_required
def reply_comment(comment_id):
    """Ответ на комментарий"""
    comment = Comment.get_by_id(current_app.db, comment_id)
    if not comment:
        abort(404)
    
    form = CommentForm()
    
    if form.validate_on_submit():
        Comment.create_comment(
            current_app.db,
            form.content.data,
            current_user.id,
            comment.post_id,
            comment_id
        )
        
        flash('Ответ добавлен', 'success')
    
    # Получаем статью для редиректа
    post = Post.get_by_id(current_app.db, comment.post_id)
    return redirect(url_for('blog.post', slug=post.slug))

@blog.route('/comment/<comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    """Удаление комментария"""
    comment = Comment.get_by_id(current_app.db, comment_id)
    if not comment:
        abort(404)
    
    # Проверяем права на удаление
    if not current_user.is_admin and comment.author_id != current_user.id:
        flash('У вас нет прав на удаление этого комментария', 'danger')
    else:
        comment.soft_delete(current_app.db)
        flash('Комментарий удален', 'success')
    
    # Получаем статью для редиректа
    post = Post.get_by_id(current_app.db, comment.post_id)
    return redirect(url_for('blog.post', slug=post.slug))

@blog.route('/post/<post_id>/react/<reaction_type>', methods=['POST'])
@login_required
def react_to_post(post_id, reaction_type):
    """Реакция на статью"""
    post = Post.get_by_id(current_app.db, post_id)
    if not post:
        abort(404)
    
    # Проверяем, существует ли такой тип реакции
    valid_reaction_types = [r['name'] for r in current_app.config['REACTION_TYPES']]
    if reaction_type not in valid_reaction_types:
        abort(400)
    
    # Создаем или обновляем реакцию
    Reaction.create_reaction(current_app.db, current_user.id, post_id, reaction_type)
    
    return redirect(url_for('blog.post', slug=post.slug))

@blog.route('/get-subcategories/<category_id>')
def get_subcategories(category_id):
    """AJAX-запрос для получения подкатегорий"""
    subcategories = Category.get_subcategories(current_app.db, category_id)
    return {'subcategories': [{'id': subcat.id, 'name': subcat.name} for subcat in subcategories]} 