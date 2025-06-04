from bson.objectid import ObjectId
from datetime import datetime
from slugify import slugify

class Category:
    def __init__(self, category_data):
        self.category_data = category_data
    
    @property
    def id(self):
        return str(self.category_data.get('_id'))
    
    @property
    def name(self):
        return self.category_data.get('name')
    
    @property
    def slug(self):
        return self.category_data.get('slug')
    
    @property
    def description(self):
        return self.category_data.get('description', '')
    
    @property
    def parent_id(self):
        return str(self.category_data.get('parent_id')) if self.category_data.get('parent_id') else None
    
    @property
    def is_private(self):
        return self.category_data.get('is_private', False)
    
    @property
    def created_at(self):
        return self.category_data.get('created_at')
    
    @property
    def icon(self):
        return self.category_data.get('icon', 'folder')
    
    @staticmethod
    def create_category(db, name, description='', parent_id=None, is_private=False, icon='folder'):
        """Создание новой категории"""
        slug = slugify(name)
        
        # Проверка на уникальность slug
        existing = db.categories.find_one({'slug': slug})
        if existing:
            # Если slug уже существует, добавляем к нему timestamp
            slug = f"{slug}-{int(datetime.utcnow().timestamp())}"
        
        category_data = {
            'name': name,
            'slug': slug,
            'description': description,
            'is_private': is_private,
            'created_at': datetime.utcnow(),
            'icon': icon
        }
        
        if parent_id:
            category_data['parent_id'] = ObjectId(parent_id)
        
        result = db.categories.insert_one(category_data)
        category_data['_id'] = result.inserted_id
        return Category(category_data)
    
    @staticmethod
    def get_by_id(db, category_id):
        """Получение категории по ID"""
        try:
            category_data = db.categories.find_one({'_id': ObjectId(category_id)})
            if category_data:
                return Category(category_data)
        except:
            pass
        return None
    
    @staticmethod
    def get_by_slug(db, slug):
        """Получение категории по slug"""
        category_data = db.categories.find_one({'slug': slug})
        if category_data:
            return Category(category_data)
        return None
    
    @staticmethod
    def get_all(db, include_private=False):
        """Получение всех категорий"""
        filter_criteria = {}
        if not include_private:
            filter_criteria['is_private'] = False
        
        cursor = db.categories.find(filter_criteria).sort('name', 1)
        return [Category(category_data) for category_data in cursor]
    
    @staticmethod
    def get_main_categories(db, include_private=False):
        """Получение только главных категорий (без подкатегорий)"""
        filter_criteria = {'parent_id': {'$exists': False}}
        if not include_private:
            filter_criteria['is_private'] = False
        
        cursor = db.categories.find(filter_criteria).sort('name', 1)
        return [Category(category_data) for category_data in cursor]
    
    @staticmethod
    def get_subcategories(db, parent_id, include_private=False):
        """Получение подкатегорий для указанной родительской категории"""
        filter_criteria = {'parent_id': ObjectId(parent_id)}
        if not include_private:
            filter_criteria['is_private'] = False
        
        cursor = db.categories.find(filter_criteria).sort('name', 1)
        return [Category(category_data) for category_data in cursor]
    
    def update(self, db, update_data):
        """Обновление категории"""
        # Если обновляется имя, обновляем и slug
        if 'name' in update_data and update_data['name'] != self.name:
            update_data['slug'] = slugify(update_data['name'])
            
            # Проверка на уникальность slug
            existing = db.categories.find_one({'slug': update_data['slug'], '_id': {'$ne': ObjectId(self.id)}})
            if existing:
                # Если slug уже существует, добавляем к нему timestamp
                update_data['slug'] = f"{update_data['slug']}-{int(datetime.utcnow().timestamp())}"
        
        # Преобразуем parent_id в ObjectId, если он есть
        if 'parent_id' in update_data and update_data['parent_id']:
            update_data['parent_id'] = ObjectId(update_data['parent_id'])
        
        db.categories.update_one(
            {'_id': ObjectId(self.id)},
            {'$set': update_data}
        )
        
        # Обновляем локальные данные
        for key, value in update_data.items():
            self.category_data[key] = value
    
    def delete(self, db):
        """Удаление категории"""
        # Сначала проверяем, есть ли подкатегории
        subcategories = db.categories.find_one({'parent_id': ObjectId(self.id)})
        if subcategories:
            raise ValueError("Нельзя удалить категорию, у которой есть подкатегории")
        
        # Проверяем, есть ли статьи в этой категории
        posts = db.posts.find_one({'category_id': ObjectId(self.id)})
        if posts:
            raise ValueError("Нельзя удалить категорию, в которой есть статьи")
        
        # Удаляем категорию
        db.categories.delete_one({'_id': ObjectId(self.id)}) 