from aiogram import types

markup_start = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1_start = types.KeyboardButton("За работу")
btn2_start = types.KeyboardButton("/help")
markup_start.add(btn1_start, btn2_start)

markup_admin = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1_admin = types.KeyboardButton("Получить базу данных")
btn2_admin = types.KeyboardButton("Получить логгер")
btn3_admin = types.KeyboardButton("Написать пользователю")
markup_admin.add(btn1_admin, btn2_admin)
markup_admin.add(btn3_admin)

markup_communication = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1_communication = types.KeyboardButton("Отмена")
markup_communication.add(btn1_communication)

markup_feedback = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1_feedback = types.KeyboardButton("Нет, обойдемся без отзывов")
markup_feedback.add(btn1_feedback)

markup_site_selection = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1_site_selection = types.KeyboardButton("УПН")
btn2_site_selection = types.KeyboardButton("ЦИАН")
btn3_site_selection = types.KeyboardButton("Яндекс Недвижимость")
btn4_site_selection = types.KeyboardButton("Авито")
btn5_site_selection = types.KeyboardButton("Завершить работу")
markup_site_selection.add(btn1_site_selection, btn2_site_selection)
markup_site_selection.add(btn3_site_selection, btn4_site_selection)
markup_site_selection.add(btn5_site_selection)

markup_first_question = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1_first_question = types.KeyboardButton("Собрать новую информацию")
btn2_first_question = types.KeyboardButton("Обновить старую информацию")
markup_first_question.add(btn1_first_question, btn2_first_question)

markup_quit = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1_quit = types.KeyboardButton("Завершить работу")
markup_quit.add(btn1_quit)

markup_continuation_question = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1_continuation_question = types.KeyboardButton("Да")
btn2_continuation_question = types.KeyboardButton("Нет")
markup_continuation_question.add(btn1_continuation_question, btn2_continuation_question)

markup_sure = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1_sure = types.KeyboardButton("Да, уверен")
btn2_sure = types.KeyboardButton("Нет, давай продолжим")
markup_sure.add(btn1_sure, btn2_sure)

markup_save_file = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1_save_file = types.KeyboardButton("Да, хочу")
btn2_save_file = types.KeyboardButton("Нет, не хочу")
markup_save_file.add(btn1_save_file, btn2_save_file)

markup_result = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1_result = types.KeyboardButton(".csv")
btn2_result = types.KeyboardButton(".xlsx")
btn3_result = types.KeyboardButton(".txt")
btn4_result = types.KeyboardButton("Все форматы")
markup_result.add(btn1_result, btn2_result, btn3_result, btn4_result)

markup_settings = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1_settings = types.KeyboardButton(".csv")
btn2_settings = types.KeyboardButton(".xlsx")
btn3_settings = types.KeyboardButton(".txt")
btn4_settings = types.KeyboardButton("Все форматы")
btn5_settings = types.KeyboardButton("Буду выбирать каждый раз")
markup_settings.add(btn1_settings, btn2_settings, btn3_settings),
markup_settings.add(btn4_settings)
markup_settings.add(btn5_settings)
