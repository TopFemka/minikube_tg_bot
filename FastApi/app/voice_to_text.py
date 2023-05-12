# voice_to_text
import asyncio
import aiohttp
import io
import speech_recognition as sr
import ffmpeg
import json
import time
import requests
import os
from fastapi import Request, Response
from typing import Dict, Any, List


async def describe_audio(message, audio_mode, telegram_api_token):
    try:
        voice_data = message.get('voice', {}).get('file_id')
        voice_duration = message.get('voice', {}).get('duration')
        if not voice_data:
            return "Не удалось получить файл с голосовым сообщением"
        url_get_file = f"https://api.telegram.org/bot{telegram_api_token}/getFile?file_id={voice_data}"
        response = requests.get(url_get_file)
        if not response.ok:
            return "Не удалось получить файл с голосовым сообщением"
        file_path = response.json().get('result', {}).get('file_path')
        if not file_path:
            return "Не удалось получить путь к файлу с голосовым сообщением"
        url_download_file = f"https://api.telegram.org/file/bot{telegram_api_token}/{file_path}"
        file_name = f"audio_{int(time.time()*1000)}.ogg"  
        output_file_name = f"audio_{int(time.time()*1000)}.wav" 
        async with aiohttp.ClientSession() as session:
            async with session.get(url_download_file) as resp:
                with open(file_name, 'wb') as f:
                    while True:
                        chunk = await resp.content.read(1024)
                        if not chunk:
                            break
                        f.write(chunk)
        try:
            # Convert audio file from OGG to WAV format using ffmpeg
            stream = ffmpeg.input(file_name)
            stream = ffmpeg.output(stream, output_file_name)
            ffmpeg.run(stream, overwrite_output=True)
            # Load the converted audio file using SpeechRecognition library
            recognizer = sr.Recognizer()
            with sr.AudioFile(output_file_name) as source:
                audio_data = recognizer.record(source)
            # Recognize the speech in the audio using Google Speech Recognition API
            text = recognizer.recognize_google(audio_data, language=audio_mode)
            print('РАСШИФРОВКА', text)
            return text
        except sr.UnknownValueError:
            return "Не удалось распознать речь"
        except sr.RequestError:
            return "Не удалось получить ответ от сервера API распознавания речи"
        except ffmpeg.Error:
            return "Не удалось сконвертировать аудиодорожку в нужный формат"
        finally:
            pass
            #можно удалить файлы    
            #os.remove(file_name)
            #os.remove(output_file_name)
    except Exception as e:           
        return 'Факапчик на бэке'
