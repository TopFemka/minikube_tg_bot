from markup_keyboard import reply_markups
from typing import Dict, Any, List

class AlloCallback:
    def __init__(self, chat_storage, tg_api):
        self.chat_storage = chat_storage
        self.tg_api = tg_api
        self.audio_modes = ["ru-RU", "en-US"]

    async def button_callback(self, update: Dict[str, Any]):
            try:
                callback_query = update['callback_query']
                chat_id = callback_query['message']['chat']['id']
                message_id = callback_query['message']['message_id']
                callback_data = callback_query['data']
                user_id = callback_query['from']['id']

                handlers = {
                    'voice_modeRU': self.handle_voice_modeRU,
                    'voice_modeEN': self.handle_voice_modeEN,
                    'helps': self.handle_helps,
                    'tokens': self.handle_tokens,
                    'profile': self.handle_profile
                }

                handler = handlers.get(callback_data)
                if handler:
                    await handler(chat_id, message_id, user_id)
                    return {'ok': True}
            except Exception as e:
                await self.tg_api.send_message(chat_id, f"Произошла ошибка при получении колбэка. {e}")
                return {'ok': True}

    async def handle_voice_modeRU(self, chat_id, message_id, user_id):
        new_mode = self.audio_modes[0]
        self.chat_storage.set_language_audio_mode(user_id, new_mode)
        await self.tg_api.edit_message_markup(chat_id, message_id=message_id, reply_markup=reply_markups[1])

    async def handle_voice_modeEN(self, chat_id, message_id, user_id):
        new_mode = self.audio_modes[1]
        self.chat_storage.set_language_audio_mode(user_id, new_mode)
        await self.tg_api.edit_message_markup(chat_id, message_id=message_id, reply_markup=reply_markups[2])

    async def handle_helps(self, chat_id, message_id, user_id):
        text = f'Бот умеет распознавать голосовые сообщения на русском и английском языке\n' \
           f'Также запоминает контекст 5 сообщений (без системных), чтобы сбросить контекст введите команду /refresh\n\n' \
           f'Пока что никаких ограничений по запросам нет\n\n' \
           f'Если возникают трудности, то обращайтесь к @TopFemka'
        await self.tg_api.edit_message(chat_id, message_id=message_id, message_text=text, reply_markup=reply_markups[0])

    async def handle_tokens(self, chat_id, message_id, user_id):
        text = "У вас 50 пробных запросов. \nВ данный момент они не расходуются :)"
        await self.tg_api.edit_message(chat_id, message_id=message_id, message_text=text, reply_markup=reply_markups[0])

    async def handle_profile(self, chat_id, message_id, user_id):
        profile = self.chat_storage.get_profile(user_id)
        profile_dict = profile
        message_text = f'Имя: {profile_dict["first_name"]}\n' \
                        f'Username: {profile_dict["username"]}\n' \
                        f'Код языка: {profile_dict["language_code"]}\n' \
                        f'Chat ID: {profile_dict["chat_id"]}\n' \
                        f'Модель GPT: ChatGPT-3.5-turbo\n' \
                        f'Кол-во запросов: {profile_dict["token_summ"]}'
        reply_markup = reply_markups[1] if profile['language_audio_mode'] == "ru-RU" else reply_markups[2]
        await self.tg_api.edit_message(chat_id, message_id=message_id, message_text=message_text, reply_markup=reply_markup)
