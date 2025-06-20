from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.enums import AcceptanceChoice
from bot.internal.callbacks import AcceptanceCallbackFactory

yes_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✅ Да, поехали!", callback_data="yes")]])


def get_acceptance_kb():
    kb = InlineKeyboardBuilder()
    for text, callback in [
        ("✅ Да", AcceptanceCallbackFactory(choice=AcceptanceChoice.YES).pack()),
        ("❌ Нет", AcceptanceCallbackFactory(choice=AcceptanceChoice.NO).pack()),
    ]:
        kb.button(text=text, callback_data=callback)
    kb.adjust(1)
    return kb.as_markup()


payment_kb = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="✅ Оплатить участие", url="https://kurs-afromari.ru/top_100")]]
)

request_contact_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="✅ Поделиться",
                request_contact=True,
            )
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)
