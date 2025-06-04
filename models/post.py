from bson.objectid import ObjectId
from datetime import datetime
import markdown
import re
from slugify import slugify

class Post:
    def __init__(self, post_data):
        self.post_data = post_data
    
    @property
    def id(self):
        return str(self.post_data.get('_id'))
    
    @property
    def title(self):
        return self.post_data.get('title')
    
    @property
    def slug(self):
        return self.post_data.get('slug')
    
    @property
    def content(self):
        return self.post_data.get('content')
    
    @property
    def content_html(self):
        """Преобразует Markdown в HTML"""
        md = markdown.Markdown(
            extensions=[
                'markdown.extensions.fenced_code',
                'markdown.extensions.codehilite',
                'markdown.extensions.tables',
                'markdown.extensions.toc'
            ]
        )
        return md.convert(self.content)
    
    @property
    def excerpt(self):
        """Возвращает короткий отрывок статьи"""
        # Сначала удаляем все markdown-разметки
        plain_text = re.sub(r'!\[.*?\]\(.*?\)', '', self.content)  # Удаляем изображения
        plain_text = re.sub(r'\[.*?\]\(.*?\)', r'\1', plain_text)  # Заменяем ссылки текстом
        plain_text = re.sub(r'#{1,6}\s+', '', plain_text)  # Удаляем заголовки
        plain_text = re.sub(r'```.*?```', '', plain_text, flags=re.DOTALL)  # Удаляем блоки кода
        plain_text = re.sub(r'`.*?`', '', plain_text)  # Удаляем инлайн-код
        
        # Берем первые 200 символов
        if len(plain_text) > 200:
            return plain_text[:200].strip() + '...'
        return plain_text.strip()
    
    @property
    def author_id(self):
        return str(self.post_data.get('author_id'))
    
    @property
    def category_id(self):
        return str(self.post_data.get('category_id'))
    
    @property
    def subcategory_id(self):
        return str(self.post_data.get('subcategory_id')) if self.post_data.get('subcategory_id') else None
    
    @property
    def created_at(self):
        return self.post_data.get('created_at')
    
    @property
    def updated_at(self):
        return self.post_data.get('updated_at')
    
    @property
    def is_published(self):
        return self.post_data.get('is_published', False)
    
    @property
    def cover_image(self):
        return self.post_data.get('cover_image')
    
    @property
    def tags(self):
        return self.post_data.get('tags', [])
    
    @property
    def view_count(self):
        return self.post_data.get('view_count', 0)
    
    @staticmethod
    def create_post(db, title, content, author_id, category_id, subcategory_id=None, 
                   tags=None, cover_image=None, is_published=False):
        """Создание новой статьи"""
        slug = slugify(title)
        
        # Проверка на уникальность slug
        existing = db.posts.find_one({'slug': slug})
        if existing:
            # Если slug уже существует, добавляем к нему timestamp
            slug = f"{slug}-{int(datetime.utcnow().timestamp())}"
        
        post_data = {
            'title': title,
            'slug': slug,
            'content': content,
            'author_id': ObjectId(author_id),
            'category_id': ObjectId(category_id),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'is_published': is_published,
            'view_count': 0,
            'tags': tags or []
        }
        
        if subcategory_id:
            post_data['subcategory_id'] = ObjectId(subcategory_id)
            
        if cover_image:
            post_data['cover_image'] = cover_image
        
        result = db.posts.insert_one(post_data)
        post_data['_id'] = result.inserted_id
        return Post(post_data)
    
    @staticmethod
    def get_by_id(db, post_id):
        """Получение статьи по ID"""
        try:
            post_data = db.posts.find_one({'_id': ObjectId(post_id)})
            if post_data:
                return Post(post_data)
        except:
            pass
        return None
    
    @staticmethod
    def get_by_slug(db, slug):
        """Получение статьи по slug"""
        post_data = db.posts.find_one({'slug': slug})
        if post_data:
            return Post(post_data)
        return None
    
    @staticmethod
    def get_posts(db, filter_criteria=None, sort_by=None, page=1, per_page=10):
        """Получение списка статей с пагинацией"""
        filter_criteria = filter_criteria or {}
        sort_by = sort_by or [('created_at', -1)]
        
        skip = (page - 1) * per_page
        
        cursor = db.posts.find(filter_criteria).sort(sort_by).skip(skip).limit(per_page)
        total = db.posts.count_documents(filter_criteria)
        
        posts = [Post(post_data) for post_data in cursor]
        
        return {
            'posts': posts,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }
    
    def update(self, db, update_data):
        """Обновление статьи"""
        # Если обновляется заголовок, обновляем и slug
        if 'title' in update_data and update_data['title'] != self.title:
            update_data['slug'] = slugify(update_data['title'])
            
            # Проверка на уникальность slug
            existing = db.posts.find_one({'slug': update_data['slug'], '_id': {'$ne': ObjectId(self.id)}})
            if existing:
                # Если slug уже существует, добавляем к нему timestamp
                update_data['slug'] = f"{update_data['slug']}-{int(datetime.utcnow().timestamp())}"
        
        # Добавляем дату обновления
        update_data['updated_at'] = datetime.utcnow()
        
        # Преобразуем ID в ObjectId, если они есть
        if 'category_id' in update_data and update_data['category_id']:
            update_data['category_id'] = ObjectId(update_data['category_id'])
        
        if 'subcategory_id' in update_data and update_data['subcategory_id']:
            update_data['subcategory_id'] = ObjectId(update_data['subcategory_id'])
        
        db.posts.update_one(
            {'_id': ObjectId(self.id)},
            {'$set': update_data}
        )
        
        # Обновляем локальные данные
        for key, value in update_data.items():
            self.post_data[key] = value
    
    def delete(self, db):
        """Удаление статьи"""
        # Удаляем все комментарии к статье
        db.comments.delete_many({'post_id': ObjectId(self.id)})
        
        # Удаляем все реакции к статье
        db.reactions.delete_many({'post_id': ObjectId(self.id)})
        
        # Удаляем саму статью
        db.posts.delete_one({'_id': ObjectId(self.id)})
    
    def increment_view(self, db):
        """Увеличивает счетчик просмотров статьи"""
        db.posts.update_one(
            {'_id': ObjectId(self.id)},
            {'$inc': {'view_count': 1}}
        )
        self.post_data['view_count'] = self.view_count + 1 