from markup_keyboard import reply_markups


class SetCommand:
    def __init__(self, chat_storage, tg_api):
        self.chat_storage = chat_storage
        self.tg_api = tg_api

    async def post_command(self, message_text, chat_id, user_id, chat_user):
        commands = {
            '/profile': self.handle_profile,
            '/killprofile': self.handle_killprofile,
            '/refresh': self.handle_refresh,
            '/history': self.handle_history,
            '/start': self.handle_start
        }

        command = commands.get(message_text)
        if command:
            await command(chat_id, user_id, chat_user)
            return {'ok': True}
        elif message_text == '':
            return Response(content='True', media_type='text/plain')
        else:
            return False

    async def handle_profile(self, chat_id, user_id, chat_user):
            try:
                profile = self.chat_storage.get_profile(user_id)
                if profile == None:
                    await self.tg_api.send_message(chat_id, "Ваш профиль не найден.")
                else:
                    profile_dict = profile
                    formatted_profile = f'Имя: {profile_dict["first_name"]}\n' \
                                        f'Username: {profile_dict["username"]}\n' \
                                        f'Код языка: {profile_dict["language_code"]}\n' \
                                        f'Chat ID: {profile_dict["chat_id"]}\n' \
                                        f'Модель GPT: ChatGPT-3.5-turbo\n' \
                                        f'Кол-во запросов: {profile_dict["token_summ"]}'
                    reply_markup = reply_markups[1] if profile['language_audio_mode'] == "ru-RU" else reply_markups[2]
                    await self.tg_api.send_message(chat_id, message_text=formatted_profile, reply_markup=reply_markup)
                return {'ok': True}
            except Exception as e:
                await self.tg_api.send_message(chat_id, f'Произошла ошибка при получении профиля.{e}')
                return {'ok': True}

    async def handle_killprofile(self, chat_id, user_id, chat_user):
        self.chat_storage.delete_profile(user_id)
        await self.tg_api.send_message(chat_id, '🫡Анонимус, ваш профиль удалён🫡')

    async def handle_refresh(self, chat_id, user_id, chat_user):
        self.chat_storage.remove_message_from_chat(chat_user)
        await self.tg_api.send_message(chat_id, 'История очищена😉')

    async def handle_history(self, chat_id, user_id, chat_user):
        user_history = self.chat_storage.get_chat_history(chat_user)
        history_string = 'Контекcт переписки: \n'
        for message in user_history:
            role = message['role']
            content = message['content']
            scontent = f"\n\n{role}: {content}" 
            history_string += scontent
                   
        if len(history_string) > 3500:
            MAX_MESSAGE_LENGTH = 3500
            # Вычисляем количество частей
            num_parts = (len(history_string) - 1) // MAX_MESSAGE_LENGTH + 1
            for i in range(num_parts):
                # Вычисляем начало и конец очередной части строки
                start = i * MAX_MESSAGE_LENGTH
                end = (i + 1) * MAX_MESSAGE_LENGTH
                # Если это последняя часть, то берем оставшуюся часть строки
                if i == num_parts - 1:
                    end = len(history_string)
                # Отправляем очередную часть строки в Telegram
                await self.tg_api.send_message(chat_id, message_text=history_string[start:end])
        else:
            await self.tg_api.send_message(chat_id, str(user_history))

    async def handle_start(self, chat_id, user_id, chat_user):
        message_text = f'Привет! Я ChatGPT by @TopFemka.\n' \
            f'Если есть вопросы по боту или сотрудничеству - пишите разработчику. Для всех остальных вопросов существую я\n\n' \
            f'🧠 /refresh - сбросить историю переписки\n' \
            f'👤 /profile - ваш профиль \n' \
            f'📝 /history - контекст \n\n' \
            f'Всего запоминается контекст 5 последних сообщений, включая от нейросети'
        await self.tg_api.send_message(chat_id, message_text=message_text)
