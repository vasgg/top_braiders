from bot.internal.lexicon import text
from database.models import User


def compose_braider_form(user: User) -> str:
    username = f"@{user.username}" if user.username else "—"
    return text["summary"].format(
        fullname=user.fullname,
        username=username,
        fio=user.fio,
        phone=user.phone,
        city=user.city,
        experience=user.experience,
        portfolio=user.portfolio,
        essay=user.essay,
    )
