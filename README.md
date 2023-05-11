# Описание проекта

Данный проект является телеграм-ботом, написанным на языке Python с использованием фреймворка FastAPI. Он работает на локальном компьютере с использованием Minikube, Nginx и Redis. Бот использует самоподписанные SSL сертификаты для защиты связи.

## Особенности

- Бот работает на вебхуках Telegram и использует чистые POST запросы к эндопинтам Telegram API через aiohttp.
- Ответ бота представляет собой поток данных.
- Бот понимает и отвечает на русские и английские войсы (язык расшифровки войса меняется в профиле).
- Бот использует последние 5 сообщений контекста для формирования ответа.
- Бот асинхронно работает через модуль asyncio.gather.
- Имеется небольшой профиль с кнопками на колбэках.
- Бот принимает список API ключей от OpenAI.

## Требования к установке

- Python ;
- Кластер  Minikube;
- Сертификаты для проксирования ssl трафика tls.pem, tls.crt

## Установка

1. Скачайте проект с GitHub;
2. Установите Python и Minikube;
3. Запустите Minikube с помощью команды 'minikube start';
4. Переключитесь на Docker демона, чтобы создавать образы видимые для манифестов 'eval $(minikube docker-env)';
5. Сгенерируйте секреты для Minikube; 
-  'my-tls-secret'  SSL сертификаты:  'tls.pem', 'tls.crt' (можно воспользоваться манифестом для секрета, добавив его в BASE64, но я создаю вручную через generic).
-  'api-keys'  Список API ключей от OpenAI "api_keys.txt".
-  'tg-token'  Один token для TG бота "tg_token".
6. Примените ConfigMap, определяющий nginx на 80 и 443 порту. Использует секрет 'my-tls-secret', монтируя файлы в /etc/nginx/certs;
7. Создайте необходимые объекты Kubernetes с помощью команды kubectl apply -f <manifest_name>.yml;
- nginx-service.yaml определяет ноду порт 443, на которой будет доступен сервис, а также селекторы, которые определяют, к каким подам будет направлен трафик.
- nginx-deployment.yaml будет слушать 80\443 порты, ssl-прокладка, проксирующая на fastapi-service.
- redis-service.yaml сюда будут направляться запросы к БД от приложения.
- redis-pvc.yaml определяем 1гиг под хранилище, чтобы при перезапуске и факапах история не терялась.
- redis-deployment.yaml непосредственно сама БД Redis.
- fastapi-deployment.yaml создаст эндпоинт для вебхука /webhook со всей логикой.
- NetworkPolicy-fastapi.yaml даст доступ FastApi во внешнюю сеть.

## Использование

- Добавьте бота в Telegram и введите команду /start, чтобы начать его работу.
- Введите текстовое сообщение или отправьте голосовое сообщение.
- Бот автоматически сформирует ответ на основе контекста последних 5 сообщений.
- Используйте кнопки на колбэках для получения дополнительной информации.
