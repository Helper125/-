import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = ''
bot = telebot.TeleBot(TOKEN)

books = {
    "I am legend": {
        "description": "книга про людину яка залишилася одна в великому місті",
        "rating": "4.5",
        "photo_url": "https://flibusta.su/b/img/big/7544.jpg",
        "link": "https://uabooks.net/96-ya-legenda.html"
    },
    "Тарас бульба": {
        "description": "Тарас Бульба - народний герой",
        "rating": "4.5",
        "photo_url": "https://staticlb.rmr.rocks/uploads/pics/01/49/529.jpg",
        "link": "https://www.ukrlib.com.ua/world/printit.php?tid=15"
    },
    "Книга джунглів": {
        "description": "Історія о мальчике, який був вихований в джунглях в стаї вовків, ведмідь і чорна пантера.",
        "rating": "7.1",
        "photo_url": "https://www.kino-teatr.ru/movie/posters/big/4/113154.jpg",
        "link": "https://www.ukrlib.com.ua/review-zl/printit.php?tid=12142"
    }
}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    for book_title in books.keys():
        markup.add(InlineKeyboardButton(book_title, callback_data=book_title))
    markup.add(InlineKeyboardButton("Налаштування", callback_data="settings"))
    bot.send_message(message.chat.id, "Оберіть книгу або перейдіть до налаштувань:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in books or call.data in ["add_book", "delete_book", "edit_book", "settings", "back_to_main", "back_to_settings"])
def callback_query(call):
    if call.data in books:
        book = books[call.data]
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Перейти за посиланням", url=book["link"]))
        markup.add(InlineKeyboardButton("Назад", callback_data="back_to_main"))

        bot.send_photo(call.message.chat.id, book["photo_url"],
                       caption=f"*{call.data}*\n\n{book['description']}\n\nОцінка: {book['rating']}",
                       parse_mode="Markdown",
                       reply_markup=markup)
    elif call.data == "settings":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Додати книгу", callback_data="add_book"))
        markup.add(InlineKeyboardButton("Видалити книгу", callback_data="delete_book"))
        markup.add(InlineKeyboardButton("Редагувати книгу", callback_data="edit_book"))
        markup.add(InlineKeyboardButton("Назад", callback_data="back_to_main"))
        bot.send_message(call.message.chat.id, "Налаштування:", reply_markup=markup)
    elif call.data == "add_book":
        msg = bot.send_message(call.message.chat.id, "Введіть назву книги:")
        bot.register_next_step_handler(msg, process_book_title_step)
    elif call.data == "delete_book":
        msg = bot.send_message(call.message.chat.id, "Введіть назву книги для видалення:")
        bot.register_next_step_handler(msg, process_book_delete_step)
    elif call.data == "edit_book":
        msg = bot.send_message(call.message.chat.id, "Введіть назву книги для редагування:")
        bot.register_next_step_handler(msg, process_book_edit_step)
    elif call.data == "back_to_main":
        send_welcome(call.message)
    elif call.data == "back_to_settings":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Додати книгу", callback_data="add_book"))
        markup.add(InlineKeyboardButton("Видалити книгу", callback_data="delete_book"))
        markup.add(InlineKeyboardButton("Редагувати книгу", callback_data="edit_book"))
        markup.add(InlineKeyboardButton("Назад", callback_data="back_to_main"))
        bot.send_message(call.message.chat.id, "Налаштування:", reply_markup=markup)

def process_book_title_step(message):
    book_title = message.text
    msg = bot.send_message(message.chat.id, "Введіть опис книги:")
    bot.register_next_step_handler(msg, process_book_description_step, book_title)

def process_book_description_step(message, book_title):
    description = message.text
    msg = bot.send_message(message.chat.id, "Введіть оцінку книги:")
    bot.register_next_step_handler(msg, process_book_rating_step, book_title, description)

def process_book_rating_step(message, book_title, description):
    rating = message.text
    msg = bot.send_message(message.chat.id, "Введіть URL фото книги:")
    bot.register_next_step_handler(msg, process_book_photo_url_step, book_title, description, rating)

def process_book_photo_url_step(message, book_title, description, rating):
    photo_url = message.text
    msg = bot.send_message(message.chat.id, "Введіть URL книги:")
    bot.register_next_step_handler(msg, process_book_link_step, book_title, description, rating, photo_url)

def process_book_link_step(message, book_title, description, rating, photo_url):
    link = message.text
    books[book_title] = {
        "description": description,
        "rating": rating,
        "photo_url": photo_url,
        "link": link
    }
    bot.send_message(message.chat.id, f"Книга '{book_title}' успішно додана!")
    send_welcome(message)

def process_book_delete_step(message):
    book_title = message.text
    if book_title in books:
        del books[book_title]
        bot.send_message(message.chat.id, f"Книга '{book_title}' успішно видалена!")
    else:
        bot.send_message(message.chat.id, f"Книга '{book_title}' не знайдена.")
    send_welcome(message)

def process_book_edit_step(message):
    book_title = message.text
    if book_title in books:
        bot.send_message(message.chat.id, f"Редагування книги '{book_title}'.")
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Змінити назву", callback_data=f"edit_title_{book_title}"))
        markup.add(InlineKeyboardButton("Змінити опис", callback_data=f"edit_description_{book_title}"))
        markup.add(InlineKeyboardButton("Змінити оцінку", callback_data=f"edit_rating_{book_title}"))
        markup.add(InlineKeyboardButton("Змінити URL фото", callback_data=f"edit_photo_url_{book_title}"))
        markup.add(InlineKeyboardButton("Змінити URL книги", callback_data=f"edit_link_{book_title}"))
        markup.add(InlineKeyboardButton("Назад", callback_data="back_to_settings"))
        bot.send_message(message.chat.id, "Оберіть поле для редагування:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, f"Книга '{book_title}' не знайдена.")
        send_welcome(message)

@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_'))
def edit_field_callback(call):
    action, field, book_title = call.data.split('_', 2)
    if action == "edit":
        msg = bot.send_message(call.message.chat.id, f"Введіть нове значення для {field}:")
        bot.register_next_step_handler(msg, process_edit_field_step, field, book_title)

def process_edit_field_step(message, field, book_title):
    new_value = message.text
    if book_title in books:
        if field == "title":
            books[new_value] = books.pop(book_title)
            bot.send_message(message.chat.id, f"Назва книги змінена на '{new_value}'.")
        else:
            books[book_title][field] = new_value
            bot.send_message(message.chat.id, f"{field.capitalize()} книги '{book_title}' змінено на '{new_value}'.")
    else:
        bot.send_message(message.chat.id, f"Книга '{book_title}' не знайдена.")
    send_welcome(message)

bot.polling(none_stop=True)
