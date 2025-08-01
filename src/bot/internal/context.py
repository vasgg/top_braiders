# fmt: off

from aiogram.fsm.state import State, StatesGroup


class Form(StatesGroup):
    fio = State()
    phone = State()
    city = State()
    experience = State()
    portfolio = State()
    essay = State()
    photo_id = State()
    repost = State()
    is_paid = State()
    payment_id = State()


FORM_FIELDS = [
    "fio",
    "phone",
    "city",
    "experience",
    "portfolio",
    "essay",
    "photo_id",
    "repost",
    "is_paid",
    "acceptance",
]

FORM_QUESTIONS = {
    "fio": "Как тебя зовут?\nНапиши свои ФИО и псевдоним, под которым ты работаешь.",
    "phone": "Оставь свой номер для связи. Нажми кнопку ✅ Поделиться.",
    "city": "Из какого ты города?",
    "experience": "Сколько лет (или месяцев) ты занимаешься плетением?",
    "portfolio": "Поделись ссылками на свои соцсети:\n"
                 "Instagram, ВК, Telegram, TikTok, что угодно — где тебя можно найти и посмотреть больше твоих работ.",
    "essay": "Расскажи, почему именно ты достойна/достоин попасть в Топ-100 брейдеров?\n"
             "Кратко опиши свои достижения и поделись с нами своими успехами.",
    "photo_id": "Загрузи свою САМУЮ лучшую фотографию, на которой ты себе больше всего нравишься 😍\n"
                "Фото должно быть в хорошем качестве, желательно портрет или полный рост.",
    "repost": "Загрузи скриншот репоста поста про Топ-100\n"
              "https://www.instagram.com/p/DLMjm2XMgXK/?igsh=MWsxaXM1emxzdjUybw==.",
    "is_paid": "Перейди по ссылке и оплати участие в проекте 💳\n\n"
               "Во время оплаты тебе покажут <b>номер заказа</b> — сохрани его и пришли нам в чат.\n"
               "❗️Не копируй пример! Отправь именно свой номер.\n\n"
               "Если забыла/забыл — проверь свою почту, он придёт туда после оплаты 📬",
    "acceptance": "Ты даёшь согласие на хранение, "
                  "обработку и использование своих данных для публикации в рейтинге и соцсетях проекта?",
}
# fmt: on
