from bson.objectid import ObjectId
from datetime import datetime
import markdown
from slugify import slugify

class Term:
    def __init__(self, term_data):
        self.term_data = term_data
    
    @property
    def id(self):
        return str(self.term_data.get('_id'))
    
    @property
    def term(self):
        return self.term_data.get('term')
    
    @property
    def slug(self):
        return self.term_data.get('slug')
    
    @property
    def definition(self):
        return self.term_data.get('definition')
    
    @property
    def definition_html(self):
        """Преобразует Markdown в HTML"""
        md = markdown.Markdown(
            extensions=[
                'markdown.extensions.fenced_code',
                'markdown.extensions.codehilite',
                'markdown.extensions.tables'
            ]
        )
        return md.convert(self.definition)
    
    @property
    def category(self):
        return self.term_data.get('category', '')
    
    @property
    def created_at(self):
        return self.term_data.get('created_at')
    
    @property
    def updated_at(self):
        return self.term_data.get('updated_at')
    
    @property
    def author_id(self):
        return str(self.term_data.get('author_id'))
    
    @property
    def related_terms(self):
        return self.term_data.get('related_terms', [])
    
    @staticmethod
    def create_term(db, term, definition, author_id, category='', related_terms=None):
        """Создание нового термина"""
        slug = slugify(term)
        
        # Проверка на уникальность slug
        existing = db.thesaurus.find_one({'slug': slug})
        if existing:
            # Если slug уже существует, добавляем к нему timestamp
            slug = f"{slug}-{int(datetime.utcnow().timestamp())}"
        
        term_data = {
            'term': term,
            'slug': slug,
            'definition': definition,
            'category': category,
            'author_id': ObjectId(author_id),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'related_terms': related_terms or []
        }
        
        result = db.thesaurus.insert_one(term_data)
        term_data['_id'] = result.inserted_id
        return Term(term_data)
    
    @staticmethod
    def get_by_id(db, term_id):
        """Получение термина по ID"""
        try:
            term_data = db.thesaurus.find_one({'_id': ObjectId(term_id)})
            if term_data:
                return Term(term_data)
        except:
            pass
        return None
    
    @staticmethod
    def get_by_slug(db, slug):
        """Получение термина по slug"""
        term_data = db.thesaurus.find_one({'slug': slug})
        if term_data:
            return Term(term_data)
        return None
    
    @staticmethod
    def get_all(db, sort_by='term'):
        """Получение всех терминов"""
        cursor = db.thesaurus.find().sort(sort_by, 1)
        return [Term(term_data) for term_data in cursor]
    
    @staticmethod
    def get_by_category(db, category, sort_by='term'):
        """Получение терминов по категории"""
        cursor = db.thesaurus.find({'category': category}).sort(sort_by, 1)
        return [Term(term_data) for term_data in cursor]
    
    @staticmethod
    def search(db, query, limit=10):
        """Поиск терминов по запросу"""
        # Создаем текстовый индекс для поиска
        db.thesaurus.create_index([('term', 'text'), ('definition', 'text')])
        
        cursor = db.thesaurus.find(
            {'$text': {'$search': query}},
            {'score': {'$meta': 'textScore'}}
        ).sort([('score', {'$meta': 'textScore'})]).limit(limit)
        
        return [Term(term_data) for term_data in cursor]
    
    @staticmethod
    def get_categories(db):
        """Получение всех категорий терминов"""
        pipeline = [
            {'$group': {'_id': '$category'}},
            {'$sort': {'_id': 1}}
        ]
        
        result = list(db.thesaurus.aggregate(pipeline))
        return [item['_id'] for item in result if item['_id']]
    
    def update(self, db, update_data):
        """Обновление термина"""
        # Если обновляется термин, обновляем и slug
        if 'term' in update_data and update_data['term'] != self.term:
            update_data['slug'] = slugify(update_data['term'])
            
            # Проверка на уникальность slug
            existing = db.thesaurus.find_one({'slug': update_data['slug'], '_id': {'$ne': ObjectId(self.id)}})
            if existing:
                # Если slug уже существует, добавляем к нему timestamp
                update_data['slug'] = f"{update_data['slug']}-{int(datetime.utcnow().timestamp())}"
        
        # Добавляем дату обновления
        update_data['updated_at'] = datetime.utcnow()
        
        db.thesaurus.update_one(
            {'_id': ObjectId(self.id)},
            {'$set': update_data}
        )
        
        # Обновляем локальные данные
        for key, value in update_data.items():
            self.term_data[key] = value
    
    def delete(self, db):
        """Удаление термина"""
        # Удаляем термин из связанных терминов
        db.thesaurus.update_many(
            {'related_terms': self.id},
            {'$pull': {'related_terms': self.id}}
        )
        
        # Удаляем сам термин
        db.thesaurus.delete_one({'_id': ObjectId(self.id)}) 