#chat_gptapi

import aiohttp
import json
from typing import Dict, Any, List
import math

class ApiChat:
    def __init__(self, api_key, url, bot):
        self.api_key = api_key
        self.api_base = url
        self.headers = {"Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key[0]}"}
        self.bot = bot
        self.current_key_index = 0
        #self.client = aiohttp.ClientSession() возможно это более корректно


    # функция принимает контекст, и запускает процесс обработки в openai. Возвращает полный ответ, чтобы отправить его в БД
    async def generate_response(self, chat_id, messages: List[Dict[str, str]], message_id) -> str:    
        try:
            async with aiohttp.ClientSession() as session:
                response = await self.send_request(session, messages)
                content = await self.process_stream_response(response, chat_id, message_id)
                return content
        except Exception as e:
            print(e)
            return  'assistant', f'Извините, произошла ошибка при обработке запроса. {e}'

    # Формирование запроса + алгоритм смены api_key
    async def send_request(self, session, messages):
        request_body={"model": "gpt-3.5-turbo", "messages": messages,
                        "temperature": 0.7, "stream": True}
        response = await session.post(url = self.api_base,
            headers=self.headers,
            json=request_body)
        if response.status == 429 or response.status == 400 or response.status == 401: # unauthorized, switch to next key
                print('429 or 400 or 401', response.status)
                self.current_key_index = (self.current_key_index + 1) % len(self.api_key)
                self.headers = {"Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key[self.current_key_index]}"}
                print('Сменили key на ', self.api_key[self.current_key_index])
                response = await session.post(url = self.api_base,
                    headers=self.headers,
                    json=request_body)
        return response

    # Потоковая обработка
    async def process_stream_response(self, response, chat_id, message_id):
        eof = False # флаг окончания процесса трансляции данных
        content = ''
        x = 1
        async for response_text in response.content:
            response_text = response_text.decode('utf-8')
            if response_text.startswith('data:'):
                response_text = response_text[6:].strip()
                if response_text.startswith('[DONE]'): # Ловим окончание потока
                    if len(content) <=2000:  
                        await self.bot.edit_message(chat_id, message_id, message_text=content)
                    else:
                        middle = math.floor(len(content) / 2)
                        await self.bot.edit_message(chat_id, message_id, message_text=content[:middle])
                        await self.bot.send_message(chat_id, message_text=content[middle:])
                    eof = True 
                    return content
                try:
                    response_data = json.loads(response_text)   
                    choices = response_data.get('choices')  
                    if choices:
                        char_block = choices[0].get('delta').get('content')    
                        if char_block:
                            content += str(char_block)
                            if len(content) >= x and len(content) <= 2000:
                                x = x*1.6
                                await self.bot.edit_message(chat_id, message_id, message_text=content + '🖋')
                except Exception as e:
                    print('факапчик на обработке данных', e)
                    return f'Извините, произошла ошибка при обработке данных. {e}'
        if eof:
            return content
        else:
            content = 'Ошибка process_stream_response'
            return content
