from flask_login import UserMixin
from bson.objectid import ObjectId
import bcrypt
from datetime import datetime

class User(UserMixin):
    def __init__(self, user_data):
        self.user_data = user_data
        
    def get_id(self):
        return str(self.user_data.get('_id'))
    
    @property
    def id(self):
        return self.get_id()
    
    @property
    def username(self):
        return self.user_data.get('username')
    
    @property
    def email(self):
        return self.user_data.get('email')
    
    @property
    def is_admin(self):
        return self.user_data.get('is_admin', False)
    
    @property
    def profile_image(self):
        return self.user_data.get('profile_image', 'default.png')
    
    @property
    def created_at(self):
        return self.user_data.get('created_at')
    
    @property
    def last_login(self):
        return self.user_data.get('last_login')
    
    @property
    def allowed_categories(self):
        return self.user_data.get('allowed_categories', [])
    
    @staticmethod
    def create_user(db, username, email, password, is_admin=False):
        """Создание нового пользователя"""
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        user_data = {
            'username': username,
            'email': email,
            'password': hashed_password,
            'is_admin': is_admin,
            'profile_image': 'default.png',
            'created_at': datetime.utcnow(),
            'last_login': datetime.utcnow(),
            'allowed_categories': []
        }
        
        result = db.users.insert_one(user_data)
        user_data['_id'] = result.inserted_id
        return User(user_data)
    
    @staticmethod
    def validate_login(db, email, password):
        """Проверка логина пользователя"""
        user_data = db.users.find_one({'email': email})
        
        if user_data and bcrypt.checkpw(password.encode('utf-8'), user_data['password']):
            # Обновление времени последнего входа
            db.users.update_one(
                {'_id': user_data['_id']},
                {'$set': {'last_login': datetime.utcnow()}}
            )
            return User(user_data)
        return None
    
    @staticmethod
    def get_by_email(db, email):
        """Получение пользователя по email"""
        user_data = db.users.find_one({'email': email})
        if user_data:
            return User(user_data)
        return None
    
    @staticmethod
    def get_by_username(db, username):
        """Получение пользователя по имени пользователя"""
        user_data = db.users.find_one({'username': username})
        if user_data:
            return User(user_data)
        return None
    
    @staticmethod
    def get_by_id(db, user_id):
        """Получение пользователя по ID"""
        try:
            user_data = db.users.find_one({'_id': ObjectId(user_id)})
            if user_data:
                return User(user_data)
        except:
            pass
        return None
    
    def update_profile(self, db, update_data):
        """Обновление профиля пользователя"""
        db.users.update_one(
            {'_id': ObjectId(self.id)},
            {'$set': update_data}
        )
        # Обновляем локальные данные
        for key, value in update_data.items():
            self.user_data[key] = value
    
    def has_access_to_category(self, category_id):
        """Проверка доступа пользователя к категории"""
        if self.is_admin:
            return True
        return str(category_id) in self.allowed_categories 