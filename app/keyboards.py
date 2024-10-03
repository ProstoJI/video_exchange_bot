from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from database.db_query import get_likes_and_dislikes, get_count_of_dangerous_videos

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Профиль"), KeyboardButton(text="INFO")],
    [KeyboardButton(text="Загрузить видео")],
    [KeyboardButton(text="Получить видео")],
    # [KeyboardButton(text="Больше времени")],
],
    resize_keyboard=True, input_field_placeholder="Выберите действие")  # one_time_keyboard=True,

stop_load = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="STOP")]
],
    resize_keyboard=True, one_time_keyboard=True)


video_verify = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Не опасное", callback_data="not_dangerous")],
    [InlineKeyboardButton(text="Бан пользователя", callback_data="ban_user")],
])

buy_time = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Выбрать время", callback_data="buy_time")]
])


choice_offer_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="1 час", callback_data="buy_1")],
    [InlineKeyboardButton(text="2 часа", callback_data="buy_2")],
    [InlineKeyboardButton(text="5 часов", callback_data="buy_5")],
    [InlineKeyboardButton(text="15 часов", callback_data="buy_15")],
    [InlineKeyboardButton(text="150 часов", callback_data="buy_150")],
],
    resize_keyboard=True)


# want_to_be_moderator = InlineKeyboardMarkup(inline_keyboard=[
#     [InlineKeyboardButton(text="Хочу работать модератором", callback_data="want_to_be_moderator")]
# ])


async def thank_for_mark(video_hash):
    keyboard = InlineKeyboardBuilder()
    likes, dislikes = await get_likes_and_dislikes(video_hash)
    keyboard.add(
        InlineKeyboardButton(text=f"{likes}👍", callback_data="thanks"),
        InlineKeyboardButton(text="Пожаловаться", callback_data="complain"),
        InlineKeyboardButton(text=f"{dislikes}👎", callback_data="thanks"),
        InlineKeyboardButton(text="Спасибо за оценку", callback_data="thanks")
    )

    return keyboard.adjust(3, 1).as_markup(resize_keyboard=True)


async def thank_for_complain(video_hash):
    keyboard = InlineKeyboardBuilder()
    likes, dislikes = await get_likes_and_dislikes(video_hash)
    keyboard.add(
        InlineKeyboardButton(text=f"{likes}👍", callback_data="already_complain"),
        InlineKeyboardButton(text="Пожаловаться", callback_data="already_complain"),
        InlineKeyboardButton(text=f"{dislikes}👎", callback_data="already_complain"),
        InlineKeyboardButton(text="На проверке...", callback_data="already_complain")
    )

    return keyboard.adjust(3, 1).as_markup(resize_keyboard=True)


async def inline_keyboard_bild(video_hash):
    keyboard = InlineKeyboardBuilder()
    likes, dislikes = await get_likes_and_dislikes(video_hash)
    keyboard.add(
        InlineKeyboardButton(text=f"{likes}👍", callback_data="new_like"),
        InlineKeyboardButton(text="Пожаловаться", callback_data="complain"),
        InlineKeyboardButton(text=f"{dislikes}👎", callback_data="new_dislike")
    )

    return keyboard.adjust(3).as_markup(resize_keyboard=True)


async def admin_main():
    builder = ReplyKeyboardBuilder()
    builder.add(
        KeyboardButton(text="Профиль"), KeyboardButton(text="INFO"),
        KeyboardButton(text="Загрузить видео"),
        KeyboardButton(text="Получить видео"),
        KeyboardButton(text="Больше времени"),
        KeyboardButton(text=f"Проверить видео({await get_count_of_dangerous_videos()})"),

    )

    return builder.adjust(2, 1, 1, 1).as_markup(resize_keyboard=True)   # , one_time_keyboard=True
