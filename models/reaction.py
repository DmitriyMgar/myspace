from bson.objectid import ObjectId
from datetime import datetime

class Reaction:
    def __init__(self, reaction_data):
        self.reaction_data = reaction_data
    
    @property
    def id(self):
        return str(self.reaction_data.get('_id'))
    
    @property
    def user_id(self):
        return str(self.reaction_data.get('user_id'))
    
    @property
    def post_id(self):
        return str(self.reaction_data.get('post_id'))
    
    @property
    def reaction_type(self):
        return self.reaction_data.get('reaction_type')
    
    @property
    def created_at(self):
        return self.reaction_data.get('created_at')
    
    @staticmethod
    def create_reaction(db, user_id, post_id, reaction_type):
        """Создание новой реакции или обновление существующей"""
        # Проверяем, существует ли уже реакция от этого пользователя к этой статье
        existing = db.reactions.find_one({
            'user_id': ObjectId(user_id),
            'post_id': ObjectId(post_id)
        })
        
        if existing:
            # Если реакция такого же типа, удаляем её (toggle)
            if existing['reaction_type'] == reaction_type:
                db.reactions.delete_one({'_id': existing['_id']})
                return None
            # Если реакция другого типа, обновляем
            else:
                db.reactions.update_one(
                    {'_id': existing['_id']},
                    {'$set': {'reaction_type': reaction_type, 'created_at': datetime.utcnow()}}
                )
                existing['reaction_type'] = reaction_type
                existing['created_at'] = datetime.utcnow()
                return Reaction(existing)
        else:
            # Создаем новую реакцию
            reaction_data = {
                'user_id': ObjectId(user_id),
                'post_id': ObjectId(post_id),
                'reaction_type': reaction_type,
                'created_at': datetime.utcnow()
            }
            
            result = db.reactions.insert_one(reaction_data)
            reaction_data['_id'] = result.inserted_id
            return Reaction(reaction_data)
    
    @staticmethod
    def get_user_reaction(db, user_id, post_id):
        """Получение реакции пользователя на статью"""
        reaction_data = db.reactions.find_one({
            'user_id': ObjectId(user_id),
            'post_id': ObjectId(post_id)
        })
        
        if reaction_data:
            return Reaction(reaction_data)
        return None
    
    @staticmethod
    def get_post_reactions(db, post_id):
        """Получение всех реакций на статью"""
        cursor = db.reactions.find({'post_id': ObjectId(post_id)})
        return [Reaction(reaction_data) for reaction_data in cursor]
    
    @staticmethod
    def count_reactions_by_type(db, post_id):
        """Подсчет количества реакций каждого типа для статьи"""
        pipeline = [
            {'$match': {'post_id': ObjectId(post_id)}},
            {'$group': {'_id': '$reaction_type', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}
        ]
        
        result = list(db.reactions.aggregate(pipeline))
        return {item['_id']: item['count'] for item in result}
    
    @staticmethod
    def delete_user_reactions(db, user_id):
        """Удаление всех реакций пользователя"""
        db.reactions.delete_many({'user_id': ObjectId(user_id)})
    
    @staticmethod
    def delete_post_reactions(db, post_id):
        """Удаление всех реакций к статье"""
        db.reactions.delete_many({'post_id': ObjectId(post_id)}) 