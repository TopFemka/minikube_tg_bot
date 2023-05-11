# markup_keyboard.py
button1 = {'text': '🇬🇧 Voice en-US 🇬🇧', 'callback_data': 'voice_modeRU'}
button2 = {'text': '🇷🇺 Voice ru-RU 🇷🇺', 'callback_data': 'voice_modeEN'}
button3 = {'text': '👤 Профиль', 'callback_data': 'profile'}
button4 = {'text': '📌 Информация', 'callback_data': 'helps'}
button5 = {'text': '📝 Запросы', 'callback_data': 'tokens'}

keyboard_profile = [[button3]]
keyboard_set_language_mode_ru = [[button2], [button4], [button5]]
keyboard_language_mode_en = [[button1], [button4], [button5]]
keyboard_set_helps = [[button3]]
keyboard_set_tokens = [[button3]]
reply_markups = [{'inline_keyboard': keyboard_profile, 'resize_keyboard': True, 'size_keyboard': 2},
                {'inline_keyboard': keyboard_set_language_mode_ru, 'resize_keyboard': True, 'size_keyboard': 2},
                {'inline_keyboard': keyboard_language_mode_en, 'resize_keyboard': True, 'size_keyboard': 2}]
            
