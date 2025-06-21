from aiogram import F, Router, types
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram.utils.chat_action import ChatActionSender

from bot.enums import AcceptanceChoice
from bot.internal.callbacks import AcceptanceCallbackFactory
from bot.internal.context import FORM_FIELDS, FORM_QUESTIONS, Form
from bot.internal.keyboards import get_acceptance_kb, payment_kb, request_contact_kb, yes_kb
from bot.internal.lexicon import text
from database.models import User

router = Router()
warned_media_groups = set()


@router.message(CommandStart())
async def start_message(
    message: types.Message,
    state: FSMContext,
) -> None:
    await state.clear()
    await message.answer(text=text["start"], reply_markup=yes_kb)


@router.callback_query(F.data == "yes")
async def yes_callback(
    callback: types.CallbackQuery,
    user: User,
    state: FSMContext,
) -> None:
    await callback.answer()
    await state.update_data(user_id=user.id)
    first_field = FORM_FIELDS[0]
    await state.set_state(getattr(Form, first_field))
    question = FORM_QUESTIONS[first_field]
    await callback.message.edit_text(question)


@router.message(StateFilter(Form.essay), F.text)
async def essay_handler(
    message: Message,
    user: User,
    state: FSMContext,
):
    user_answer = message.text.strip()
    if len(user_answer) > 2000:
        await message.answer(text=text["long_essay"])
        return
    user.essay = user_answer
    await message.answer(text=FORM_QUESTIONS["photo_id"])
    await state.set_state(Form.photo_id)


@router.message(F.document)
async def document_handler(
    message: types.Message,
    state: FSMContext,
):
    current_state = await state.get_state()
    field = current_state.split(":")[-1]
    if field in ("photo_id", "repost"):
        await message.answer("Принимаются только фотографии, а не файлы. Пожалуйста, отправьте фотографию.")
        return
    else:
        return


@router.message(StateFilter(Form), F.photo)
async def photo_handler(
    message: Message,
    user: User,
    state: FSMContext,
):
    current_state = await state.get_state()
    field = current_state.split(":")[-1]
    if message.media_group_id is not None and field in ("photo_id", "repost"):
        key = (message.chat.id, message.media_group_id)
        if key not in warned_media_groups:
            warned_media_groups.add(key)
            await message.bot.send_message(message.chat.id, "Отправьте одну фотографию.")
        return
    match field:
        case "photo_id":
            photo_id = message.photo[-1].file_id
            user.photo_id = photo_id
            await message.answer(text=FORM_QUESTIONS["repost"])
            await state.set_state(Form.repost)
        case "repost":
            photo_id = message.photo[-1].file_id
            user.screenshot = photo_id
            file_path = "src/bot/internal/data/IMG.PNG"
            await message.answer_photo(
                FSInputFile(path=file_path), caption=FORM_QUESTIONS["is_paid"], reply_markup=payment_kb
            )
            await state.set_state(Form.payment_id)
        case _:
            return


@router.message(F.contact)
async def handle_contact(
    message: Message,
    user: User,
    state: FSMContext,
):
    current_state = await state.get_state()
    field = current_state.split(":")[-1]
    if field != "phone":
        return
    phone = message.contact.phone_number
    user.phone = phone
    await message.answer(text=FORM_QUESTIONS["city"])
    await state.set_state(Form.city)


@router.message(StateFilter(Form), F.text)
async def form_handler(
    message: Message,
    user: User,
    state: FSMContext,
):
    current_state = await state.get_state()
    field = current_state.split(":")[-1]

    user_answer = message.text.strip()

    if field == "payment_id":
        user_answer.lstrip('#')

    setattr(user, field, user_answer)

    async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
        match field:
            case "fio":
                await message.answer(text=FORM_QUESTIONS["phone"], reply_markup=request_contact_kb)
                await state.set_state(Form.phone)
            case "city":
                await message.answer(text=FORM_QUESTIONS["experience"])
                await state.set_state(Form.experience)
            case "experience":
                await message.answer(text=FORM_QUESTIONS["portfolio"])
                await state.set_state(Form.portfolio)
            case "portfolio":
                await message.answer(text=FORM_QUESTIONS["essay"])
                await state.set_state(Form.essay)
            case "payment_id":
                await message.answer(text=FORM_QUESTIONS["acceptance"], reply_markup=get_acceptance_kb())
                await state.set_state()


@router.callback_query(AcceptanceCallbackFactory.filter())
async def payment_handler(
    callback: CallbackQuery,
    callback_data: AcceptanceCallbackFactory,
    # user: User,
    # settings: Settings,
):
    await callback.answer()
    match callback_data.choice:
        case AcceptanceChoice.YES:
            await callback.message.edit_text(text=text["final"])
            # caption = compose_braider_form(user)
            # await callback.bot.send_photo(chat_id=settings.bot.channel_id, photo=user.photo_id, caption=caption)
        case AcceptanceChoice.NO:
            await callback.message.edit_text(text=text["no_acceptance"])
            await callback.message.answer(text=FORM_QUESTIONS["acceptance"], reply_markup=get_acceptance_kb())
