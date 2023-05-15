
from typing import Dict, Any, List
from chat_storage import ChatStorage
from chat_gptapi import ApiChat
from voice_to_text import describe_audio
from telegram_api import TelegramAPI
from post_callback import AlloCallback
import tiktoken

class TelegramBot:
    def __init__(self, telegram_api_token, chat_storage, api_key, url, SetCommand):
        self.telegram_api_token = telegram_api_token
        self.chat_storage = chat_storage
        self.audio_modes = ["ru-RU", "en-US"]
        self.tg_api = TelegramAPI(self.telegram_api_token)
        self.gpt = ApiChat(api_key, url, self.tg_api)
        self.command = SetCommand(self.chat_storage, self.tg_api)
        self.callbachnaya = AlloCallback(self.chat_storage, self.tg_api)
        

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
            audio_mode = profile["language_audio_mode"]                        
            message_text = await describe_audio(message, audio_mode, self.telegram_api_token)

        elif 'text' in message and message['text']:
            message_text = message['text'].strip()
        
        if message_text is not None:
            if not await self.command.post_command(message_text, chat_id, user_id, chat_user):                              
                try:

                    self.chat_storage.add_message_to_chat(chat_user, 'user', message_text)
                    message_id = await self.tg_api.send_message(chat_id, 'Хм...')
                    await self.tg_api.send_message_Action(chat_id)
                    await self.handle_message(chat_id, chat_user, message_id)
                    return {"ok": True}
                
                except Exception as e:
                    print('ошибка НА СЕРВАКЕ ищи', e, 'MESSAGE: ', message_text)
                    return {"ok": True}
                
    async def handle_message(self, chat_id, chat_user, message_id):
        try:
            chat_history = self.chat_storage.get_chat_history(chat_user)
            num_tokens = await self.num_tokens_from_messages(chat_history)

            if num_tokens >= 4000:
                await self.handle_context_overflow(chat_id, chat_user, message_id, chat_history)
            else:
                ai_response = await self.gpt.generate_response(chat_id, chat_history, message_id)
                self.chat_storage.add_message_to_chat(chat_user, 'assistant', ai_response)
            return {"ok": True}
        except Exception as e:
                    print('ошибка handle_message', e)
                    return {"ok": True}

    async def handle_context_overflow(self, chat_id, chat_user, message_id, chat_history):
        try:
            context = []
            for message in reversed(chat_history):
                if await self.num_tokens_from_messages(context + [message]) <= 4000:
                    context.append(message)
                else:
                    await self.handle_context_response(chat_id, chat_user, context, message_id)
                    break
        except Exception as e:
            print('ошибка handle_context_overflow', e)
            return {"ok": True}
                    
    async def handle_context_response(self, chat_id, chat_user, context, message_id):
        try:
            chat_history = list(reversed(context))
            print(chat_history)
            ai_response = await self.gpt.generate_response(chat_id, chat_history, message_id)
            self.chat_storage.add_message_to_chat(chat_user, 'assistant', ai_response)
            await self.tg_api.send_message(chat_id, 'Слишком большая история, пора сбросить контекст /refresh')
        except Exception as e:
            print('ошибка handle_context_response', e)
            return {"ok": True}
    
    async def button_callback(self, update: Dict[str, Any]):
        await self.callbachnaya.button_callback(update)
        return {"ok": True}
    
    async def num_tokens_from_messages(self, messages, model="gpt-3.5-turbo-0301"):
        if model == "gpt-3.5-turbo-0301":
            tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
            tokens_per_name = -1  # if there's a name, the role is omitted
        else:
            raise NotImplementedError(f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")
        num_tokens = 0
        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(self.encoding.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name
        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        return num_tokens
    
