from aiogram.filters.callback_data import CallbackData

from bot.enums import AcceptanceChoice


class AcceptanceCallbackFactory(CallbackData, prefix="acceptance"):
    choice: AcceptanceChoice
