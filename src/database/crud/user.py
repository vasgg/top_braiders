from logging import getLogger

from aiogram.types import User as AiogramUser
from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User


logger = getLogger(__name__)


async def add_user_to_db(user: AiogramUser, db_session) -> User:
    new_user = User(
        id=user.id,
        fullname=user.full_name,
        username=user.username,
    )
    db_session.add(new_user)
    await db_session.flush()
    return new_user


async def get_user_from_db_by_tg_id(telegram_id: int, db_session: AsyncSession) -> User | None:
    query = select(User).filter(User.id == telegram_id)
    result: Result = await db_session.execute(query)
    user = result.scalar()
    return user


async def get_all_payment_ids(db_session: AsyncSession) -> set[str]:
    from bot.internal.controllers import extract_digits
    query = select(User.payment_id).where(User.payment_id.isnot(None), User.is_paid.is_(False))
    result = await db_session.scalars(query)
    payment_ids = {extract_digits(payment_id) for payment_id in result if payment_id}
    logger.info("All unpaid (cleaned) payment_ids: %s", payment_ids)
    return payment_ids


async def get_user_by_payment_id(payment_id: str, db_session: AsyncSession) -> User:
    query = select(User).where(User.payment_id == payment_id)
    result: Result = await db_session.execute(query)
    user = result.scalar()
    return user


async def get_user_ids_without_payment(db_session: AsyncSession) -> list[int]:
    query = select(User.id).where(User.payment_id.is_(None))
    result: Result = await db_session.execute(query)
    user_ids = list(result.scalars().all())
    return user_ids


async def get_users_with_payment_but_not_published(db_session: AsyncSession) -> list[User]:
    query = select(User).where(User.is_paid.is_(True), User.is_published.is_(False))
    result: Result = await db_session.execute(query)
    users = list(result.scalars().all())
    return users
