# main.py

import os
import uvicorn
import asyncio
from fastapi import FastAPI, Request, Response
from telegram_bot import TelegramBot
from chat_storage import ChatStorage
from set_commands import SetCommand
#костыль main
tasks = []

# Получение списка api_key, получение tg_token из виртуального окружения\контейнера
with open(os.environ['API_KEYS_FILE'], 'r') as f:
    api_key = [key.strip() for key in f.readlines()]
with open(os.environ['TG_TOKEN_FILE'], 'r') as f:
    telegram_api_tokens = [token.strip() for token in f.readlines()]
    telegram_api_token = telegram_api_tokens[0]
url = "https://api.openai.com/v1/chat/completions"

# Создание экземплявов fastapi и классов Телеграм-бота и хранилища чатов
app = FastAPI()
bot = TelegramBot(telegram_api_token, ChatStorage(), api_key, url, SetCommand)

# Обработчик post-запросов от Telegram(события в боте)
@app.post('/webhook')
async def telegram_webhook(request: Request):
    global tasks
    try:
        update = await request.json()
        # Cобытие должно содержать сообщение или callback
        if 'message' in update and not update['message']['from']['is_bot']: # Cобытие должно содержать сообщение не от бота
            tasks.append(asyncio.create_task(bot.telegram_webhook(update)))
        elif 'callback_query' in update: # иначе ищем callback
            tasks.append(asyncio.create_task(bot.button_callback(update)))
        return {'ok': True}        
    except Exception as e:
        return {'ok': True}
        
async def main():
    global tasks
    # Здесь может быть инициализация вебхука(WebhookSet)
    
    # Ждем завершения всех задач()
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())
    uvicorn.run(app, host='0.0.0.0', port=8000)
