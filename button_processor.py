from telebot import *


class ButtonProcessor:
    def __init__(self, bot, mongo, buttons_text, states, messages):
        self.bot = bot
        self.mongo = mongo
        self.BUTTONS_TEXT = buttons_text
        self.STATES = states
        self.MESSAGES = messages

    def process_gm_dep_0(self, message, text):
        if text == self.BUTTONS_TEXT[0] or text == self.BUTTONS_TEXT[1]:
            self.mongo.update_state(message.from_user.id, self.STATES["game_end"])
            markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, resize_keyboard=2)
            btn1 = types.KeyboardButton(self.BUTTONS_TEXT[2])
            markup.add(btn1)
            new_msg = self.bot.send_message(message.chat.id, self.MESSAGES[3], reply_markup=markup)
            self.mongo.update_last_message(message.from_user.id, new_msg.id)

    def process_gm_end(self, message, text):
        if text == self.BUTTONS_TEXT[2]:
            self.mongo.update_state(message.from_user.id, self.STATES["default"])
            new_msg = self.bot.send_message(message.chat.id, "Вы находитесь в главном меню.",
                                            reply_markup=types.ReplyKeyboardRemove())
            self.mongo.update_last_message(message.from_user.id, new_msg.id)

    def process_ord_1(self, message, text, products_list):
        text_is_correct = False
        for product_name in products_list:
            if text == product_name:
                text_is_correct = True
                self.mongo.update_state(message.from_user.id, self.STATES["ord_2"])
                self.mongo.update_current_order(message.from_user.id, product=product_name)
                new_msg = self.bot.send_message(message.chat.id, "Введите количество:",
                                                reply_markup=types.ReplyKeyboardRemove())
                self.mongo.update_last_message(message.from_user.id, new_msg.id)
                break
        if not text_is_correct:
            bot_text = "Введен некорректный вариант. Пожалуйста, попробуйте снова."
            new_msg = self.bot.send_message(message.chat.id, bot_text)
            self.mongo.update_last_message(message.from_user.id, new_msg.id)

    def process_ord_2(self, message, text):
        try:
            value = int(text)
        except ValueError:
            bot_text = "Введено некорректное значение. Пожалуйста, введите число."
            new_msg = self.bot.send_message(message.chat.id, bot_text)
            self.mongo.update_last_message(message.from_user.id, new_msg.id)
        else:
            if value > 100:
                bot_text = "Введенное число слишком большое (максимум 100). Пожалуйста, попробуйте еще раз."
                new_msg = self.bot.send_message(message.chat.id, bot_text)
                self.mongo.update_last_message(message.from_user.id, new_msg.id)
                return
            if value < 1:
                bot_text = "Введенное число должно быть больше нуля. Пожалуйста, попробуйте еще раз."
                new_msg = self.bot.send_message(message.chat.id, bot_text)
                self.mongo.update_last_message(message.from_user.id, new_msg.id)
                return
            self.mongo.update_state(message.from_user.id, self.STATES["ord_2.5"])
            self.mongo.update_current_order(message.from_user.id, amount=value)
            if self.mongo.user_exists(message.from_user.id):
                self.mongo.add_order(message.from_user.id, self.mongo.get_current_order(message.from_user.id))
            else:
                self.mongo.create_user(message.from_user.id, self.mongo.get_current_order(message.from_user.id), 0)
            bot_text = "Готовы ли вы перейти к оформлению?"
            new_msg = self.bot.send_message(message.chat.id, bot_text,
                                            reply_markup=self.generate_buttons(self.BUTTONS_TEXT[3:7]))
            self.mongo.update_last_message(message.from_user.id, new_msg.id)

    def process_ord_2_5(self, message, text, products, products_list, cart):
        if text == self.BUTTONS_TEXT[3]:
            nw_msg = self.bot.send_message(message.chat.id, products, reply_markup=self.generate_buttons(products_list))
            self.mongo.update_last_message(message.from_user.id, nw_msg.id)
            self.mongo.update_state(message.from_user.id, self.STATES["ord_1"])
        elif text == self.BUTTONS_TEXT[4]:
            self.bot.send_message(message.chat.id, cart)
            if cart == "Ваша корзина пуста.":
                return
            new_msg = self.bot.send_message(message.chat.id, self.MESSAGES[5], reply_markup=types.ReplyKeyboardRemove())
            self.mongo.update_state(message.from_user.id, self.STATES["ord_3"])
            self.mongo.update_last_message(message.from_user.id, new_msg.id)
        elif text == self.BUTTONS_TEXT[5]:
            new_msg = self.bot.send_message(message.chat.id, cart)
            self.mongo.update_last_message(message.from_user.id, new_msg.id)
        elif text == self.BUTTONS_TEXT[6]:
            self.mongo.clear_orders(message.from_user.id)
            new_msg = self.bot.send_message(message.chat.id, "Корзина очищена!")
            self.mongo.update_last_message(message.from_user.id, new_msg.id)
        else:
            bot_text = "Введен некорректный вариант. Пожалуйста, попробуйте снова."
            new_msg = self.bot.send_message(message.chat.id, bot_text)
            self.mongo.update_last_message(message.from_user.id, new_msg.id)

    def process_ord_3(self, message, phone_number):
        if phone_number is None:
            bot_text = "Введенный номер телефона не соответствует заданному формату. Пожалуйста, попробуйте снова."
            new_msg = self.bot.send_message(message.chat.id, bot_text)
            self.mongo.update_last_message(message.from_user.id, new_msg.id)
            return
        self.mongo.update_state(message.from_user.id, self.STATES["ord_4"])
        self.mongo.update_phone_number(message.from_user.id, phone_number)
        new_msg = self.bot.send_message(message.chat.id, self.MESSAGES[6])
        self.mongo.update_last_message(message.from_user.id, new_msg.id)

    def process_ord_4(self, message, text):
        text_limit = 100
        if len(text) > text_limit:
            bot_text = f"Введенный текст слишком большой (больше {text_limit} символов). Пожалуйста, попробуйте снова."
            new_msg = self.bot.send_message(message.chat.id, bot_text)
            self.mongo.update_last_message(message.from_user.id, new_msg.id)
            return
        if len(text.split()) > 1:
            bot_text = "Введенный текст содержит пробелы. Пожалуйста, попробуйте снова."
            new_msg = self.bot.send_message(message.chat.id, bot_text)
            self.mongo.update_last_message(message.from_user.id, new_msg.id)
            return
        self.mongo.update_email(message.from_user.id, text)
        if self.mongo.check_desires(message.from_user.id):
            self.mongo.update_state(message.from_user.id, self.STATES["ord_6"])
            new_msg = self.bot.send_message(message.chat.id, "Контактные данные обновлены.",
                                            reply_markup=self.generate_buttons(self.BUTTONS_TEXT[7:14]))
            self.mongo.update_last_message(message.from_user.id, new_msg.id)
        else:
            self.mongo.update_state(message.from_user.id, self.STATES["ord_5"])
            new_msg = self.bot.send_message(message.chat.id, "Здесь вы можете оставить ваши пожелания к заказу.")
            self.mongo.update_last_message(message.from_user.id, new_msg.id)

    def process_ord_5(self, message, text):
        text_limit = 300
        if len(text) > text_limit:
            bot_text = f"Введенный текст слишком большой (больше {text_limit} символов). Пожалуйста, попробуйте снова."
            new_msg = self.bot.send_message(message.chat.id, bot_text)
            self.mongo.update_last_message(message.from_user.id, new_msg.id)
            return
        self.mongo.update_state(message.from_user.id, self.STATES["ord_6"])
        self.mongo.update_desires(message.from_user.id, text)
        new_msg = self.bot.send_message(message.chat.id, "Ваш заказ принят. Желаете ли вы сделать что-то ещё?",
                                        reply_markup=self.generate_buttons(self.BUTTONS_TEXT[7:14]))
        self.mongo.update_last_message(message.from_user.id, new_msg.id)

    def process_ord_6(self, message, text, cart, contact_info):
        self.mongo.set_checkpoint(message.from_user.id, self.STATES["ord_6"])
        if text == self.BUTTONS_TEXT[7]:
            self.mongo.update_state(message.from_user.id, self.STATES["default"])
            txt = "Вы находитесь в главном меню. Введите /help чтобы увидеть доступные команды."
            new_msg = self.bot.send_message(message.chat.id, txt, reply_markup=types.ReplyKeyboardRemove())
            self.mongo.update_last_message(message.from_user.id, new_msg.id)
        elif text == self.BUTTONS_TEXT[8]:
            new_msg = self.bot.send_message(message.chat.id, cart)
            self.mongo.update_last_message(message.from_user.id, new_msg.id)
        elif text == self.BUTTONS_TEXT[9]:
            new_msg = self.bot.send_message(message.chat.id, contact_info)
            self.mongo.update_last_message(message.from_user.id, new_msg.id)
        elif text == self.BUTTONS_TEXT[10]:
            self.mongo.set_checkpoint(message.from_user.id, 0)
            self.mongo.update_state(message.from_user.id, self.STATES["ord_3"])
            new_msg = self.bot.send_message(message.chat.id, self.MESSAGES[5], reply_markup=types.ReplyKeyboardRemove())
            self.mongo.update_last_message(message.from_user.id, new_msg.id)
        elif text == self.BUTTONS_TEXT[11]:
            bot_text = f'Ваши пожелания:\n"{self.mongo.get_desires(message.from_user.id)}"'
            new_msg = self.bot.send_message(message.chat.id, bot_text)
            self.mongo.update_last_message(message.from_user.id, new_msg.id)
        elif text == self.BUTTONS_TEXT[12]:
            self.mongo.set_checkpoint(message.from_user.id, 0)
            self.mongo.update_state(message.from_user.id, self.STATES["ord_5"])
            new_msg = self.bot.send_message(message.chat.id, "Здесь вы можете оставить ваши пожелания к заказу.")
            self.mongo.update_last_message(message.from_user.id, new_msg.id)
        elif text == self.BUTTONS_TEXT[13]:
            self.mongo.delete_user(message.from_user.id)
            self.mongo.update_state(message.from_user.id, self.STATES["default"])
            txt = "Ваши данные удалены. Вы находитесь в главном меню. Введите /help чтобы увидеть доступные команды."
            new_msg = self.bot.send_message(message.chat.id, txt, reply_markup=types.ReplyKeyboardRemove())
            self.mongo.update_last_message(message.from_user.id, new_msg.id)
        else:
            bot_text = "Введен некорректный вариант. Пожалуйста, попробуйте снова."
            new_msg = self.bot.send_message(message.chat.id, bot_text)
            self.mongo.update_last_message(message.from_user.id, new_msg.id)

    @staticmethod
    def generate_buttons(names):
        """Receives list of strings and generates markup with buttons, named with these strings"""
        row_width = 1
        resize_kb = True
        if len(names) > 4:
            row_width = 2
            resize_kb = False
        markup = types.ReplyKeyboardMarkup(row_width=row_width, resize_keyboard=resize_kb)
        buttons = [types.KeyboardButton(name) for name in names]
        for btn in buttons:
            markup.add(btn)
        return markup
