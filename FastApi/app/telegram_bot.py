
from typing import Dict, Any, List
from chat_storage import ChatStorage
from chat_gptapi import ApiChat
from voice_to_text import describe_audio
from telegram_api import TelegramAPI
from post_callback import AlloCallback

class TelegramBot:
    def __init__(self, telegram_api_token, chat_storage, api_key, url, SetCommand):
        self.telegram_api_token = telegram_api_token
        self.chat_storage = chat_storage
        self.audio_modes = ["ru-RU", "en-US"]
        self.tg_api = TelegramAPI(self.telegram_api_token)
        self.gpt = ApiChat(api_key, url, self.tg_api)
        self.command = SetCommand(self.chat_storage, self.tg_api)
        self.callbachnaya = AlloCallback(self.chat_storage, self.tg_api)
        #self.client = aiohttp.ClientSession() возможно так более корректно?
        

    async def telegram_webhook(self, update: Dict[str, Any]):
        # Создаем профиль пользователя в соответствии с user_id. (В методе db уже стоит проверка на повтор)
        try:
            user_id = update['message']['from']['id']
            chat_id = update['message']['chat']['id']
            chat_user = "{}_{}".format(user_id, chat_id) #ключ для хранения чатов пользователя отдельно от профилей
            first_name = update['message']['from']['first_name']
            username = update['message']['from'].get('username')
            language_code = update['message']['from'].get('language_code')
            self.chat_storage.create_profile(user_id, first_name, username, language_code, chat_id)
        except Exception as e:
            return {"ok": True}
            
        message = update['message']  
        
        if 'voice' in message and message['voice']:
            profile = self.chat_storage.get_profile(user_id)
            audio_mode = profile["laungle_audio_mode"]                        
            message_text = await describe_audio(message, audio_mode, self.telegram_api_token)

        elif 'text' in message and message['text']:
            message_text = message['text'].strip()
        
        if message_text is not None:
            if not await self.command.post_command(message_text, chat_id, user_id, chat_user):                              
                try:

                    self.chat_storage.add_message_to_chat(chat_user, 'user', message_text)
                    message_id = await self.tg_api.send_message(chat_id, 'Хм...')
                    await self.tg_api.send_message_Action(chat_id)
                    chat_history = self.chat_storage.get_chat_history(chat_user)
                    ai_response = await self.gpt.generate_response(chat_id, chat_history, message_id)                
                    self.chat_storage.add_message_to_chat(chat_user, 'assistant', ai_response)
                    return {"ok": True}
                
                except Exception as e:
                    print('ошибка НА СЕРВАКЕ ищи', e, 'MESSAGE: ', message_text)
                    return {"ok": True}

    async def button_callback(self, update: Dict[str, Any]):
        await self.callbachnaya.button_callback(update)
        return {"ok": True}
    
