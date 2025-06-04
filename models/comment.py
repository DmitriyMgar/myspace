from bson.objectid import ObjectId
from datetime import datetime
import markdown

class Comment:
    def __init__(self, comment_data):
        self.comment_data = comment_data
    
    @property
    def id(self):
        return str(self.comment_data.get('_id'))
    
    @property
    def content(self):
        return self.comment_data.get('content')
    
    @property
    def content_html(self):
        """Преобразует Markdown в HTML"""
        md = markdown.Markdown(
            extensions=[
                'markdown.extensions.fenced_code',
                'markdown.extensions.codehilite',
            ]
        )
        return md.convert(self.content)
    
    @property
    def author_id(self):
        return str(self.comment_data.get('author_id'))
    
    @property
    def post_id(self):
        return str(self.comment_data.get('post_id'))
    
    @property
    def parent_id(self):
        return str(self.comment_data.get('parent_id')) if self.comment_data.get('parent_id') else None
    
    @property
    def created_at(self):
        return self.comment_data.get('created_at')
    
    @property
    def updated_at(self):
        return self.comment_data.get('updated_at')
    
    @property
    def is_edited(self):
        return self.comment_data.get('is_edited', False)
    
    @property
    def is_deleted(self):
        return self.comment_data.get('is_deleted', False)
    
    @staticmethod
    def create_comment(db, content, author_id, post_id, parent_id=None):
        """Создание нового комментария"""
        comment_data = {
            'content': content,
            'author_id': ObjectId(author_id),
            'post_id': ObjectId(post_id),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'is_edited': False,
            'is_deleted': False
        }
        
        if parent_id:
            comment_data['parent_id'] = ObjectId(parent_id)
        
        result = db.comments.insert_one(comment_data)
        comment_data['_id'] = result.inserted_id
        return Comment(comment_data)
    
    @staticmethod
    def get_by_id(db, comment_id):
        """Получение комментария по ID"""
        try:
            comment_data = db.comments.find_one({'_id': ObjectId(comment_id)})
            if comment_data:
                return Comment(comment_data)
        except:
            pass
        return None
    
    @staticmethod
    def get_comments_for_post(db, post_id, include_deleted=False):
        """Получение всех комментариев для статьи"""
        filter_criteria = {'post_id': ObjectId(post_id)}
        if not include_deleted:
            filter_criteria['is_deleted'] = False
        
        cursor = db.comments.find(filter_criteria).sort('created_at', 1)
        return [Comment(comment_data) for comment_data in cursor]
    
    @staticmethod
    def get_replies(db, comment_id, include_deleted=False):
        """Получение ответов на комментарий"""
        filter_criteria = {'parent_id': ObjectId(comment_id)}
        if not include_deleted:
            filter_criteria['is_deleted'] = False
        
        cursor = db.comments.find(filter_criteria).sort('created_at', 1)
        return [Comment(comment_data) for comment_data in cursor]
    
    def update(self, db, content):
        """Обновление комментария"""
        update_data = {
            'content': content,
            'updated_at': datetime.utcnow(),
            'is_edited': True
        }
        
        db.comments.update_one(
            {'_id': ObjectId(self.id)},
            {'$set': update_data}
        )
        
        # Обновляем локальные данные
        for key, value in update_data.items():
            self.comment_data[key] = value
    
    def soft_delete(self, db):
        """Мягкое удаление комментария"""
        db.comments.update_one(
            {'_id': ObjectId(self.id)},
            {'$set': {'is_deleted': True, 'content': '[Комментарий удален]'}}
        )
        self.comment_data['is_deleted'] = True
        self.comment_data['content'] = '[Комментарий удален]'
    
    def hard_delete(self, db):
        """Полное удаление комментария и всех ответов"""
        # Получаем все ответы на этот комментарий
        replies = self.get_replies(db, self.id, include_deleted=True)
        
        # Удаляем все ответы
        for reply in replies:
            reply.hard_delete(db)
        
        # Удаляем сам комментарий
        db.comments.delete_one({'_id': ObjectId(self.id)}) 