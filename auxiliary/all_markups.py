from aiogram import types

markup_start = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1_start = types.KeyboardButton("За работу")
btn2_start = types.KeyboardButton("/help")
markup_start.add(btn1_start, btn2_start)

markup_admin = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1_admin = types.KeyboardButton("Получить базу данных")
btn2_admin = types.KeyboardButton("Получить логгер")
markup_admin.add(btn1_admin, btn2_admin)

markup_site_question = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1_site_question = types.KeyboardButton("УПН")
btn2_site_question = types.KeyboardButton("ЦИАН")
btn3_site_question = types.KeyboardButton("Яндекс Недвижимость")
btn4_site_question = types.KeyboardButton("Авито")
btn5_site_question = types.KeyboardButton("Завершить работу")
markup_site_question.add(btn1_site_question, btn2_site_question)
markup_site_question.add(btn3_site_question, btn4_site_question)
markup_site_question.add(btn5_site_question)

markup_first_question = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1_first_question = types.KeyboardButton("Собрать новую информацию")
btn2_first_question = types.KeyboardButton("Обновить старую информацию")
markup_first_question.add(btn1_first_question, btn2_first_question)

markup_quit = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1_quit = types.KeyboardButton("Завершить работу")
markup_quit.add(btn1_quit)

markup_continue_question = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1_continue_question = types.KeyboardButton("Да")
btn2_continue_question = types.KeyboardButton("Нет")
markup_continue_question.add(btn1_continue_question, btn2_continue_question)

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
