from datetime import datetime
import json

import aiohttp

from bot.config import Settings
from bot.internal.lexicon import text
from database.models import User


async def get_export_id(settings: Settings, data: dict) -> str:
    url = get_export_url(settings, data.get("created_at", datetime.now().strftime("%Y-%m-%d")))
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            json_data = await response.json()

            if json_data.get("success") and "info" in json_data and "export_id" in json_data["info"]:
                export_id = json_data["info"]["export_id"]
                return str(export_id)
            else:
                return "Не удалось получить export_id из ответа"


def get_export_url(settings: Settings, date: str) -> str:
    return (
        f"https://{settings.course.account_name}."
        f"getcourse.ru/pl/api/account/payments?key="
        f"{settings.course.api_key.get_secret_value()}&created_at[from]={date}"
    )


def get_deals_url(settings: Settings, export_id: str) -> str:
    return (
        f"https://{settings.course.account_name}.getcourse.ru/pl/api/account/exports/"
        f"{export_id}?key={settings.course.api_key.get_secret_value()}"
    )


async def get_deal(settings: Settings, export_id: str, deal_id: str) -> dict | None:
    url = get_deals_url(settings, export_id)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            json_data = await response.json()

            if not json_data["success"]:
                return None

            info = json_data["info"]
            print(json.dumps(json_data, indent=2, ensure_ascii=False))

            fields = info["fields"]

            idx_number = fields.index("Заказ")

            for item in info["items"]:
                if item[idx_number] == str(deal_id):
                    return item

            return None


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
