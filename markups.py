from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# KeyboardButton - экземпляр кнопки
# ReplyKeyboardMarkup - меню для бота


# --- Main Menu ---
btn_main_menu = KeyboardButton('Главное меню')
btn_make_appointment = KeyboardButton('Записаться на процедуру')
btn_user_profile = KeyboardButton('Личный кабинет')
main_menu = ReplyKeyboardMarkup(resize_keyboard = True).add(btn_make_appointment, btn_user_profile)


# --- Orders History ---
btn_orders_history = KeyboardButton('История заказов')
user_profile = ReplyKeyboardMarkup(resize_keyboard = True).add(btn_orders_history)
orders_history = ReplyKeyboardMarkup(resize_keyboard = True).add(btn_main_menu)



# --- Make Appointment ---
## --- Pick Premise ---
with open('premises.json', 'r', encoding='utf-8') as file:
    premises = json.load(file)

btn_premise_01 = KeyboardButton(f"{premises['premises'][0]['premise_name']}")
btn_premise_02 = KeyboardButton(f"{premises['premises'][1]['premise_name']}")
btn_premise_03 = KeyboardButton(f"{premises['premises'][2]['premise_name']}")
btn_premise_04 = KeyboardButton(f"{premises['premises'][3]['premise_name']}")
btn_premise_05 = KeyboardButton(f"{premises['premises'][4]['premise_name']}")
btn_premise_06 = KeyboardButton(f"{premises['premises'][5]['premise_name']}")

pick_premises_menu = ReplyKeyboardMarkup(resize_keyboard = True).add(btn_premise_01, btn_premise_02, btn_premise_03, 
                                                                    btn_premise_04, btn_premise_05, btn_premise_06)


## --- Pick Service ---

btn_pick_service_haircut = KeyboardButton('Парикмахерские услуги')
btn_pick_service_makeup = KeyboardButton('Макияж')
btn_pick_service_esthetics = KeyboardButton('Косметология')
btn_pick_service_tattoo = KeyboardButton('Тату и пирсинг')
btn_pick_service_brows = KeyboardButton('Брови')

pick_service_menu = ReplyKeyboardMarkup(resize_keyboard = True).add(btn_pick_service_haircut, btn_pick_service_makeup, 
                                                                    btn_pick_service_esthetics, btn_pick_service_tattoo, 
                                                                    btn_pick_service_brows)

btn_return_to_service_menu = KeyboardButton('Вернуться к списку услуг')




### --- Pick Date & Specialist ---
btn_pick_date_time_menu = KeyboardButton('Выбрать дату и время')
btn_pick_specialist_menu = KeyboardButton('Выбрать мастера')

btn_pick_specialist_01 = KeyboardButton('Мастер 1')
btn_pick_specialist_02 = KeyboardButton('Мастер 2')
btn_pick_specialist_03 = KeyboardButton('Мастер 3')
btn_pick_specialist_04 = KeyboardButton('Мастер 4')
btn_pick_specialist_05 = KeyboardButton('Мастер 5')
btn_pick_specialist_06 = KeyboardButton('Мастер 6')
btn_pick_specialist_07 = KeyboardButton('Мастер 7')
btn_pick_specialist_08 = KeyboardButton('Мастер 8')
btn_pick_specialist_09 = KeyboardButton('Мастер 9')
btn_pick_specialist_10 = KeyboardButton('Мастер 10')
btn_pick_specialist_11 = KeyboardButton('Мастер 11')
btn_pick_specialist_12 = KeyboardButton('Мастер 12')
btn_pick_specialist_13 = KeyboardButton('Мастер 13')
btn_pick_specialist_14 = KeyboardButton('Мастер 14')
btn_pick_specialist_15 = KeyboardButton('Мастер 15')


return_or_pick_specialist = ReplyKeyboardMarkup(resize_keyboard = True).add(btn_return_to_service_menu, btn_pick_specialist_menu)
pick_specialist_menu = ReplyKeyboardMarkup(resize_keyboard = True).add(btn_pick_specialist_01, btn_pick_specialist_02, btn_pick_specialist_03, btn_pick_specialist_04, btn_pick_specialist_05,
                                                            btn_pick_specialist_06, btn_pick_specialist_07, btn_pick_specialist_08, btn_pick_specialist_09, btn_pick_specialist_10,
                                                            btn_pick_specialist_11, btn_pick_specialist_12, btn_pick_specialist_13, btn_pick_specialist_14, btn_pick_specialist_15,
                                                            btn_return_to_service_menu, btn_main_menu)


btn_pick_date_01 = KeyboardButton('16 декабря, 2022')
btn_pick_date_02 = KeyboardButton('17 декабря, 2022')
btn_pick_date_03 = KeyboardButton('18 декабря, 2022')
btn_pick_date_04 = KeyboardButton('19 декабря, 2022')
btn_pick_date_05 = KeyboardButton('20 декабря, 2022')

pick_date_menu = ReplyKeyboardMarkup(resize_keyboard = True).add(btn_pick_date_01, btn_pick_date_02, btn_pick_date_03, btn_pick_date_04,
                                                                        btn_pick_date_05)

btn_pick_time_01 = KeyboardButton('10-00')
btn_pick_time_02 = KeyboardButton('11-00')
btn_pick_time_03 = KeyboardButton('12-00')
btn_pick_time_04 = KeyboardButton('13-00')
btn_pick_time_05 = KeyboardButton('14-00')
btn_pick_time_06 = KeyboardButton('15-00')
btn_pick_time_07 = KeyboardButton('16-00')
btn_pick_time_08 = KeyboardButton('17-00')
btn_pick_time_09 = KeyboardButton('18-00')
btn_pick_time_10 = KeyboardButton('19-00')

pick_time_menu = ReplyKeyboardMarkup(resize_keyboard = True).add(btn_pick_time_01, btn_pick_time_02, btn_pick_time_03, btn_pick_time_04,
                                                    btn_pick_time_05, btn_pick_time_06, btn_pick_time_07, btn_pick_time_08, btn_pick_time_09, btn_pick_time_10)

# --- Repeat Order ---

btn_last_order_repeat = pick_date_menu
last_order_repeat_menu = ReplyKeyboardMarkup(resize_keyboard = True).add(btn_last_order_repeat, btn_main_menu)

# --- Orders History ---

btn_orders_history_01 = KeyboardButton('Услуга #00001\n2022-12-05 11:00 \nБрови\nМосква, Салон 2\nМастер 8')
btn_orders_history_02 = KeyboardButton('Услуга #00002\n2022-12-07 13:00 \nМакияж\nМосква, Салон 1\nМастер 4')
orders_history_menu = ReplyKeyboardMarkup(resize_keyboard = True).add(btn_orders_history_01, btn_orders_history_02, 
                                                btn_main_menu)


# --- Registration Menu ---

btn_registration = KeyboardButton('Регистрация')
registration_menu = ReplyKeyboardMarkup(resize_keyboard = True).add(btn_registration, 
                                                btn_main_menu)

btn_registration_complete = btn_main_menu
registration_complete = ReplyKeyboardMarkup(resize_keyboard = True).add(btn_main_menu)