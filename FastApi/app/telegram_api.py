import aiohttp
import json

class TelegramAPI:
    def __init__(self, telegram_api_token):
            self.telegram_api_token = telegram_api_token
            self.base_url = f'https://api.telegram.org/bot{telegram_api_token}/'

    async def _send_request(self, method: str, json_data: dict = None):
        url = self.base_url + method
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=json_data) as response:
                data = await response.json()
        if method == 'sendMessage':
            return data['result']['message_id']
        return data.get('result')

    async def send_message(self, chat_id: str, message_text: str, reply_markup=None):
        request_data = {'chat_id': chat_id, 'text': message_text}
        if reply_markup:
            request_data['reply_markup'] = json.dumps(reply_markup)
        return await self._send_request('sendMessage', json_data=request_data)

    async def edit_message(self, chat_id: str, message_id: int, message_text: str, reply_markup=None):
        request_data = {'chat_id': chat_id, 'message_id': message_id, 'text': message_text}
        if reply_markup:
            request_data['reply_markup'] = json.dumps(reply_markup)
        return await self._send_request('editMessageText', json_data=request_data)

    async def edit_message_markup(self, chat_id: str, message_id: int, reply_markup=None):
        request_data = {'chat_id': chat_id, 'message_id': message_id}
        if reply_markup:
            request_data['reply_markup'] = json.dumps(reply_markup)
        return await self._send_request('editMessageReplyMarkup', json_data=request_data)

    async def send_message_Action(self, chat_id: str):
        request_data = {'chat_id': chat_id, 'action': 'typing'}
        return await self._send_request('SendMessageAction', json_data=request_data)
