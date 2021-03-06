from telebot import *
import random
import secrets
from button_processor import ButtonProcessor
from mongodb_manager import MongoDBManager
from output_manager import IOManager


with open(".env", "r", encoding="utf8") as f:
    TOKEN, MONGO_LINK = f.read().split('\n')

bot = TeleBot(TOKEN)
mongo = MongoDBManager(MONGO_LINK)


def parse_messages_file(path):
    with open(path, "r", encoding="utf8") as f:
        result = f.read().split('\n')
    return result

# List of special users to make easter eggs
IMPORTANT_IDS = {"@DarkArtheme": 934414507, "@zactho": 626264651}

# List of long bot messages which are written in the file for the better code readability
MESSAGES = parse_messages_file("data/messages_default")

# Dictionary of states which allow to implement state machine
STATES = {"default": 0, "game_st": 1, "gm_dep_0": 2, "gm_dep_1": 3, "game_end": 4, "ord_0": 5, "ord_1": 6, "ord_2": 7,
          "ord_2.5": 8, "ord_3": 9, "ord_4": 10, "ord_5": 11, "ord_6": 12}

# List of button texts which are written in the file for the better code readability and allow to make button generating easier
BUTTONS_TEXT = parse_messages_file("data/game_button_texts")


btn_proc = ButtonProcessor(bot, mongo, BUTTONS_TEXT, STATES, MESSAGES)


@bot.message_handler(commands=["start"])
def start_command(message):
    """Handler of the /start command. Changes user state to default and removes any markup."""
    user_id = message.from_user.id
    mongo.update_state(user_id, STATES["default"])
    markup = types.ReplyKeyboardRemove()
    new_msg = bot.send_message(message.chat.id, MESSAGES[0], reply_markup=markup)
    mongo.update_last_message(user_id, new_msg.id)


@bot.message_handler(commands=["help"])
def help_command(message):
    """Handler of the /help command."""
    current_state = mongo.get_state(message.from_user.id)
    if current_state == STATES["default"]:
        with open("data/help_command_default_state", "r", encoding="utf8") as f:
            text = f.read()
        new_msg = bot.send_message(message.chat.id, text)
        mongo.update_last_message(message.from_user.id, new_msg.id)
    elif STATES["game_st"] <= current_state <= STATES["game_end"]:
        text = """
            ???? ???????????????????? ?? ???????????? ????????. ?????????????? /restart ?????? ?????????????? ???????? ?????????????? ?? /exit ?????????? ?????????? ???? ????????.
                """
        new_msg = bot.send_message(message.chat.id, text)
        mongo.update_last_message(message.from_user.id, new_msg.id)
    elif STATES["ord_0"] <= current_state <= STATES["ord_6"]:
        text = """
                    ???? ???????????????????? ?? ???????????? ????????????. ?????????????? /start ?????? ???????????? ???? ????????.
                        """
        new_msg = bot.send_message(message.chat.id, text)
        mongo.update_last_message(message.from_user.id, new_msg.id)
    else:
        pass


@bot.message_handler(commands=["send_random_geo"])
def send_random_geo_command(message):
    """Handler of the /send_random_geo command. Bot sends random geo location."""
    user_id = message.from_user.id
    current_state = mongo.get_state(user_id)
    if current_state != STATES["default"]:
        return
    latitude = random.uniform(-90.0, 90.0)
    longitude = random.uniform(-180.0, 180.0)
    if user_id == IMPORTANT_IDS["@zactho"]:         # easter egg, do not pay attention :)
        latitude = 56.118651
        longitude = 47.180606
    new_msg = bot.send_location(message.chat.id, latitude, longitude)
    mongo.update_last_message(message.from_user.id, new_msg.id)


@bot.message_handler(commands=["send_random_sticker"])
def send_random_sticker_command(message):
    """Handler of the /send_random_sticker command. Bot sends random sticker from ./data/stickers/misos/webp."""
    current_state = mongo.get_state(message.from_user.id)
    if current_state != STATES["default"]:
        return
    number = 52859554
    path = f"data/stickers/misos/webp/file_{number + secrets.randbelow(37)}.webp"
    with open(path, "rb") as sticker:
        new_msg = bot.send_sticker(message.chat.id, sticker)
    mongo.update_last_message(message.from_user.id, new_msg.id)


@bot.message_handler(commands=["start_game"])
def start_game_command(message):
    """Handler of the /start_game command. A small demo what buttons can be capable of."""
    current_state = mongo.get_state(message.from_user.id)
    if current_state != STATES["default"]:
        return
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text="Ok", callback_data="game_started")
    markup.add(btn1)
    mongo.update_state(message.from_user.id, STATES["game_st"])
    new_msg = bot.send_message(message.chat.id, MESSAGES[1], reply_markup=markup)
    mongo.update_last_message(message.from_user.id, new_msg.id)


@bot.message_handler(commands=["restart"])
def restart_command(message):
    """Handler of the /restart command. Available only in /start_game state and restarts it."""
    current_state = mongo.get_state(message.from_user.id)
    if STATES["game_st"] <= current_state <= STATES["game_end"]:
        new_msg = bot.send_message(message.chat.id, "???????????????????? ??????????????????", reply_markup=types.ReplyKeyboardRemove())
        mongo.update_last_message(message.from_user.id, new_msg.id)
        mongo.update_state(message.from_user.id, STATES["default"])
        start_game_command(message)


@bot.message_handler(commands=["exit"])
def exit_command(message):
    """Handler of the /exit command. Available only in /start_game state and exits from it."""
    current_state = mongo.get_state(message.from_user.id)
    if STATES["game_st"] <= current_state <= STATES["game_end"]:
        mongo.update_state(message.from_user.id, STATES["default"])
        markup = types.ReplyKeyboardRemove(selective=False)
        new_msg = bot.send_message(message.chat.id, "???????? ?????????????????? ??????????????????????????", reply_markup=markup)
        mongo.update_last_message(message.from_user.id, new_msg.id)


@bot.message_handler(commands=["order"])
def order_command(message):
    """Handler of the /order command. Simulates the process of making an order and gathering user info."""
    current_state = mongo.get_state(message.from_user.id)
    checkpoint = mongo.get_checkpoint(message.from_user.id)
    if current_state == STATES["default"]:
        if checkpoint != 0:
            mongo.update_state(message.from_user.id, STATES["ord_6"])
            new_msg = bot.send_message(message.chat.id, "???? ?????? ?????????????? ??????????. ?????????????? ???? ???? ?????????????????????? ??????-???? ???????",
                                       reply_markup=btn_proc.generate_buttons(BUTTONS_TEXT[7:14]))
        else:
            btn1 = types.InlineKeyboardButton(text="Ok", callback_data="order_started")
            markup = types.InlineKeyboardMarkup()
            markup.add(btn1)
            new_msg = bot.send_message(message.chat.id, MESSAGES[4], reply_markup=markup)
            mongo.update_state(message.from_user.id, STATES["ord_0"])
        mongo.update_last_message(message.from_user.id, new_msg.id)


@bot.message_handler(content_types=["text"])
def check_button_click(message):
    """Handler of all usual buttons clicks."""
    current_state = mongo.get_state(message.from_user.id)
    text = message.text
    if current_state == STATES["gm_dep_0"]:
        btn_proc.process_gm_dep_0(message, text)
    elif current_state == STATES["game_end"]:
        btn_proc.process_gm_end(message, text)
    elif current_state == STATES["ord_1"]:
        btn_proc.process_ord_1(message, text, IOManager.get_products_name_list(mongo.get_products()))
    elif current_state == STATES["ord_2"]:
        btn_proc.process_ord_2(message, text)
    elif current_state == STATES["ord_2.5"]:
        products = IOManager.get_products(mongo.get_products())
        products_list = IOManager.get_products_name_list(mongo.get_products())
        cart = IOManager.get_all_orders(mongo.get_all_orders(message.from_user.id),
                                        mongo.count_total_sum(message.from_user.id))
        btn_proc.process_ord_2_5(message, text, products, products_list, cart)
    elif current_state == STATES["ord_3"]:
        btn_proc.process_ord_3(message, IOManager.check_phone_number(text))
    elif current_state == STATES["ord_4"]:
        btn_proc.process_ord_4(message, text)
    elif current_state == STATES["ord_5"]:
        btn_proc.process_ord_5(message, text)
    elif current_state == STATES["ord_6"]:
        cart = IOManager.get_all_orders(mongo.get_all_orders(message.from_user.id),
                                        mongo.count_total_sum(message.from_user.id))
        contact_info = IOManager.get_contact_info(mongo.get_user(message.from_user.id))
        btn_proc.process_ord_6(message, text, cart, contact_info)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    """Handler of all inline buttons clicks."""
    user_id = call.message.chat.id
    current_state = mongo.get_state(user_id)
    if current_state == STATES["game_st"]:
        if call.data == "game_started":
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=None)
            markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            btn1 = types.KeyboardButton(BUTTONS_TEXT[0])
            btn2 = types.KeyboardButton(BUTTONS_TEXT[1])
            markup.add(btn1, btn2)
            new_msg = bot.send_message(call.message.chat.id, MESSAGES[2], reply_markup=markup)
            mongo.update_state(user_id, STATES["gm_dep_0"])
            mongo.update_last_message(user_id, new_msg.id)
    elif current_state == STATES["ord_0"]:
        if call.data == "order_started":
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=None)
            products_list = IOManager.get_products_name_list(mongo.get_products())
            markup = btn_proc.generate_buttons(products_list)
            new_msg = bot.send_message(user_id, IOManager.get_products(mongo.get_products()), reply_markup=markup)
            mongo.update_last_message(user_id, new_msg.id)
            mongo.update_state(user_id, STATES["ord_1"])


def main():
    bot.polling()       # allows bot to process requests.


if __name__ == "__main__":
    main()
