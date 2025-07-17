from asyncio import sleep
from datetime import UTC, datetime, timedelta
import json
from logging import getLogger

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError
import aiohttp

from bot.config import Settings
from bot.internal.lexicon import text
from database.crud.user import get_all_payment_ids, get_user_by_payment_id, get_users_with_payment_but_not_published
from database.db_connector import DatabaseConnector
from database.models import User


logger = getLogger(__name__)


async def get_export_id(settings: Settings, max_attempts: int = 3, delay: float = 5.0) -> str:
    url = get_export_url(settings, "2025-06-20")
    last_exc = None
    for attempt in range(1, max_attempts + 1):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    json_data = await response.json()
                    if json_data.get("success") and "info" in json_data and "export_id" in json_data["info"]:
                        return str(json_data["info"]["export_id"])
                    else:
                        raise Exception(f"Can't get export_id, API response: {json_data}")
        except Exception as exc:
            last_exc = exc
            logger.warning(f"[get_export_id] attempt {attempt}/{max_attempts} failed: {exc}")
            if attempt < max_attempts:
                await sleep(delay)
    raise last_exc


def get_export_url(settings: Settings, date: str) -> str:
    return (
        f"https://{settings.course.account_name}."
        f"getcourse.ru/pl/api/account/payments?key="
        f"{settings.course.api_key.get_secret_value()}&created_at[from]={date}"
    )


def get_deals_url(settings: Settings, export_id: str) -> str:
    return (
        f"https://{settings.course.account_name}.getcourse.ru/pl/api/account/exports/"
        f"{export_id}?key={settings.course.api_key.get_secret_value()}&status=accepted"
    )


async def get_deals(settings: Settings, export_id: str) -> list | None:
    url = get_deals_url(settings, export_id)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            json_data = await response.json()

            if not json_data["success"]:
                return None

            deals = json_data["info"]["items"]
            logger.info("All accepted deals:\n%s", json.dumps(deals, indent=2, ensure_ascii=False))
            return deals

            # fields = info["fields"]
            #
            # idx_number = fields.index("Заказ")
            #
            # for item in info["items"]:
            #     if item[idx_number] == str(deal_id):
            #         return item
            #
            # return None


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


def extract_digits(string: str) -> str:
    return ''.join(c for c in string if c.isdigit())


async def wait_for_deals(settings, export_id, retries=3, delay=5.0):
    for attempt in range(1, retries + 1):
        await sleep(delay)
        deals = await get_deals(settings, export_id)
        logger.info("All deals: %s", deals)
        if deals is not None:
            return deals
    raise Exception(f"Error while waiting for deals. Retries: {retries}, export_id={export_id}")


def get_seconds_until_starting_mark(sttngs: Settings, utcnow):
    mark = utcnow.replace(hour=sttngs.bot.utc_starting_mark, minute=0, second=0, microsecond=0)
    if utcnow >= mark:
        mark += timedelta(days=1)
    return (mark - utcnow).total_seconds()


async def daily_routine(settings: Settings, bot: Bot, db_connector: DatabaseConnector) -> None:
    while True:
        utcnow = datetime.now(UTC)
        seconds_to_sleep = get_seconds_until_starting_mark(settings, utcnow)
        await sleep(seconds_to_sleep)
        logger.info("Daily routine started")
        try:
            export_id = await get_export_id(settings)
        except Exception as e:
            logger.exception(e)
            continue
        logger.info("Export_id: %s", export_id)

        try:
            deals = await wait_for_deals(settings, export_id)
        except Exception as e:
            logger.exception(f"Error while waiting for deals: {e}")
            continue
        async with db_connector.session_factory() as db_session:
            payments_set = await get_all_payment_ids(db_session)
            for deal in deals:
                payment_id = deal[3]
                if payment_id in payments_set:
                    user = await get_user_by_payment_id(payment_id, db_session)
                    if not user:
                        logger.warning("User with payment_id=%s not found", payment_id)
                        continue
                    if user.is_published:
                        logger.info("User %s already published, skipping", user.fullname)
                        continue
                    user.is_paid = True
                    photo_msg = await bot.send_photo(
                        chat_id=settings.bot.channel_id,
                        photo=user.photo_id
                    )
                    caption = compose_braider_form(user)
                    await bot.send_message(
                        chat_id=settings.bot.channel_id,
                        text=caption,
                        reply_to_message_id=photo_msg.message_id
                    )
                    user.is_published = True
                    db_session.add(user)
                    await db_session.commit()
                    logger.info("User %s is paid and published", user.fullname)
                    await sleep(8)

            # users = await get_users_with_payment_but_not_published(db_session)
            # for user in users:
            #     if user.is_published:
            #         logger.info("User %s already published, skipping", user.fullname)
            #         continue
            #     photo_msg = await bot.send_photo(
            #         chat_id=settings.bot.channel_id,
            #         photo=user.photo_id
            #     )
            #     caption = compose_braider_form(user)
            #     await bot.send_message(
            #         chat_id=settings.bot.channel_id,
            #         text=caption,
            #         reply_to_message_id=photo_msg.message_id
            #     )
            #     user.is_published = True
            #     db_session.add(user)
            #     await db_session.commit()
            #     logger.info("User %s is published", user.fullname)
            #     await sleep(8)

        #     users_without_payment = await get_user_ids_without_payment(db_session)
        #     for user_id in users_without_payment:
        #         try:
        #             await bot.send_message(
        #                 chat_id=user_id,
        #                 text=text["no_text_payment"],
        #             )
        #             await sleep(8)
        #             logger.info("User %s is notified", user_id)
        #         except TelegramForbiddenError:
        #             logger.info("User %s blocked the bot", user_id)
        #         except Exception as e:
        #             logger.exception(e)
        # logger.info("Users without payment: %s", users_without_payment)
        # logger.info("Users without payment are notified")
        # logger.info(f"Published {len(users)} new users")
        logger.info("Daily routine finished")
