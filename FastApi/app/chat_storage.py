# chat_storage.py
import redis
import json
import os
from typing import Dict, Any, List
redis_host = os.environ.get('REDIS_HOST') # ip redis (если куб, то сервис redis)


class ChatStorage:
    def __init__(self, host=redis_host, port=6379, db=0):
        self.redis = redis.StrictRedis(host=host, port=port, db=db)
        
    def create_profile(self, user_id: int, first_name: str, username: str, language_code: str, chat_id: int) -> bool:
        if self.redis.sismember('users', user_id):
            return False
        token_summ = 50
        language_audio_mode = "ru-RU" if language_code == "ru" else "en-US"
        profile = {
            "first_name": first_name, 
            "username": username, 
            "language_code": language_code, 
            "chat_id": chat_id, 
            "token_summ": token_summ, 
            "language_audio_mode": language_audio_mode
        }
        self.redis.sadd('users', user_id)
        self.redis.set(user_id, json.dumps(profile))
        return True
        
    def get_profile(self, user_id: int, fields: List[str] = None) -> dict:
        profile_json = self.redis.get(user_id)
        if profile_json is None:
            return None
        profile = json.loads(profile_json)
        if fields:
            return {field: profile.get(field) for field in fields}
        else:
            return profile
    
    def delete_profile(self, user_id: int) -> bool:
        if not self.redis.sismember('users', user_id):
            return False
        self.redis.srem('users', user_id)
        self.redis.delete(user_id)
        return True
            
    def set_language_audio_mode(self, user_id: int, new_mode: str) -> bool:
        if not self.redis.sismember('users', user_id):
            return False
        profile = json.loads(self.redis.get(user_id))
        profile["language_audio_mode"] = new_mode
        self.redis.set(user_id, json.dumps(profile))
        return True
        
    def add_message_to_chat(self, chat_user, role, message):
        # добавление сообщения в чат
        
        new_message = {'role':role, 'content': message}
        chat_data = json.loads(self.redis.get(chat_user) or '{}')
        chat_data['messages'] = chat_data.get('messages', []) + [new_message]
        self.redis.set(chat_user, json.dumps(chat_data))
        return True
        
    def remove_message_from_chat(self, chat_user):
        # удаление сообщения из чата
        chat_data = json.loads(self.redis.get(chat_user) or '{}')
        chat_data['messages'] = []
        self.redis.set(chat_user, json.dumps(chat_data))
        return True

    def get_chat_history(self, chat_user):
        # получение последних 5 сообщений чата
        chat_data = json.loads(self.redis.get(chat_user) or '{}')
        messages = chat_data.get('messages', [])
        return messages
