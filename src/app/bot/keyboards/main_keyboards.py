from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_model_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🤖 ChatGPT", callback_data="model_chatgpt"
                ),
                InlineKeyboardButton(
                    text="🌐 YandexGPT", callback_data="model_yandexgpt"
                ),
            ]
        ]
    )
    return keyboard
