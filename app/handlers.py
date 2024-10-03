from aiogram import F, Router
from aiogram.filters import CommandStart, Command, Filter
from aiogram.types import Message, CallbackQuery  # LabeledPrice, PreCheckoutQuery, ContentType InputMediaPhoto
import app.keyboards as kb
from database.db_query import *

router = Router()


class FilterByMode(Filter):
    def __init__(self, mode):
        self.mode = mode

    async def __call__(self, message: Message):
        return await get_user_mode(message.from_user.id) == self.mode


async def keyboard_choice(message: Message):
    if await is_user_admin(message.from_user.id):
        return await kb.admin_main()
    else:
        return kb.main


@router.message(FilterByMode("ban"))
async def answer_to_banned_user(message: Message):
    await message.answer("Вы забанены и не можете пользоваться этим ботом")


@router.message(CommandStart(), FilterByMode("default"))
async def hello(message: Message):

    reply_markup = await keyboard_choice(message)

    await message.answer(f"Привет, {message.from_user.first_name}\nЭто бот для бесплатного обмена рандомными видео между юзерами\n\n1 секунда вашего видео = 1 секунде рандомного видео /rules", reply_markup=reply_markup)
    if await registration(message.from_user.id):
        await message.answer("Тебе начислено 5 бесплатных минут за регистрацию")
    print("Пользователь:", list(str(message).split(","))[10].split("=")[1].replace("'", ""), "запустил бот")


@router.message(Command("help"), FilterByMode("default"))
async def helpp(message: Message):

    reply_markup = await keyboard_choice(message)

    await message.answer("/start - перезапуск бота\n/info - информация о боте\n/profile - мой профиль\n/upload_video - загрузить видео\ndownload_video - получить видео", reply_markup=reply_markup)


@router.message(Command("rules"), FilterByMode("default"))
async def show_rules(message: Message):

    reply_markup = await keyboard_choice(message)

    await message.answer("1. За видео уже в базе времени не начисляется⚠️\n2. Всё разрешено❤", reply_markup=reply_markup)


@router.message(Command("info"), FilterByMode("default"))
@router.message(F.text == "INFO", FilterByMode("default"))
async def show_info(message: Message):

    reply_markup = await keyboard_choice(message)

    await message.answer("Это бот для бесплатного обмена рандомными видео между юзерами\n\n1 секунда вашего видео = 1 секунде рандомного видео", reply_markup=reply_markup)


@router.message(Command("profile"), FilterByMode("default"))
@router.message(F.text == "Профиль", FilterByMode("default"))
async def show_profile(message: Message):
    available_time, all_uploaded_time, admin = await get_profile(message.from_user.id)
    if not admin:
        await message.answer(f"Привет, {message.from_user.first_name}\n\nНа твоём счету {round(available_time/60, 2)} минут\nЗа всё время ты загрузил {round(all_uploaded_time/60, 2)} минут", reply_markup=kb.main)
    if admin:
        await message.answer(f"Привет, {message.from_user.first_name}\n\nНа твоём счету {round(available_time/60, 2)} минут\nЗа всё время ты загрузил {round(all_uploaded_time/60, 2)} минут\n\nТы админ. Спасибо за помощь", reply_markup=await kb.admin_main())


@router.message(Command("upload_video"), FilterByMode("default"))
@router.message(F.text == "Загрузить видео")
async def allow_load(message: Message):
    await message.answer("Можете загружать видео!", reply_markup=kb.stop_load)
    await set_mode(message.from_user.id, "load")


@router.message(Command("download_video"), FilterByMode("default"))
@router.message(F.text == "Получить видео")
async def allow_load(message: Message):
    print(f"Пользователь {message.from_user.first_name} скачивает видео")
    video = await get_random_video()
    if await is_user_admin(message.from_user.id):
        await message.answer_video(video.tg_hash, reply_markup=await kb.inline_keyboard_bild(video.tg_hash))
        await message.answer(f"-0 минут\nСпасибо, что работаешь админом и улучшаешь этот бот", reply_markup=await kb.admin_main())
    elif await get_available_time(message.from_user.id) > video.duration:
        await message.answer_video(video.tg_hash, reply_markup=await kb.inline_keyboard_bild(video.tg_hash))
        await message.answer(f"-{round(video.duration/60, 2)} минут", reply_markup=kb.main)
        await reduce_time(message.from_user.id, video.duration)
    else:
        await message.answer(f"Я хотел отправить тебе видео длинной {round(video.duration/60, 2)} минут, но у тебя не хватает времени", reply_markup=kb.main)


@router.message(F.text == "STOP", FilterByMode("load"))
async def stop_load(message: Message):

    reply_markup = await keyboard_choice(message)

    await message.answer("Загрузка окончена", reply_markup=reply_markup)
    await set_mode(message.from_user.id, "default")


# @router.message(F.text == "Больше времени", FilterByMode("default"))
# async def buy_time(message: Message):
#
#     reply_markup = await keyboard_choice(message)
#
#     await message.answer("Вы получаете время за загрузку своих видео\n"
#                          "1 секунда вашего видео = 1 секунде рандомного видео\n\n"
#                          "Также вы можете купить время\n\n"
#                          "1 час == 60 рублей\n"
#                          "2 часа == 110 рублей\n"
#                          "5 часов == 250 рублей\n"
#                          "15 часов == 700 рублей\n"
#                          "150 часов == 6000 рублей\n", reply_markup=kb.buy_time)


@router.message(F.text.contains("Проверить видео"), FilterByMode("default"))
async def check_video(message: Message):
    await message.answer_video(await get_requires_verification_video(), reply_markup=kb.video_verify)


@router.message(F.video, FilterByMode("default"))
async def almost_upload_video(message: Message):

    reply_markup = await keyboard_choice(message)

    await message.answer("Сначало нажми загрузить видео или /upload_video", reply_markup=reply_markup)


@router.message(F.video, FilterByMode("load"))
async def upload_video(message: Message):
    print(f"Пользователь {message.from_user.first_name} загружает видео")
    await upload_video_to_datadase(message)


@router.callback_query(F.data == "new_like")
async def new_like(callback: CallbackQuery):
    await callback.answer("Новый лайк")
    await add_new_like(callback.message.video.file_id)
    await callback.message.edit_reply_markup(reply_markup=await kb.thank_for_mark(callback.message.video.file_id))


@router.callback_query(F.data == "new_dislike")
async def new_dislike(callback: CallbackQuery):
    await callback.answer("Новый дислайк")
    await add_new_dislike(callback.message.video.file_id)
    await callback.message.edit_reply_markup(reply_markup=await kb.thank_for_mark(callback.message.video.file_id))


@router.callback_query(F.data == "complain")
async def complain(callback: CallbackQuery):
    await callback.answer("Мы проверим это видео")
    await mark_dangerous(callback.message.video.file_id)
    await callback.message.edit_reply_markup(reply_markup=await kb.thank_for_complain(callback.message.video.file_id))


@router.callback_query(F.data == "already_complain")
async def already_complain(callback: CallbackQuery):
    await callback.answer("Видео на проверке")


@router.callback_query(F.data == "thanks")
async def thanks(callback: CallbackQuery):
    await callback.answer("Оценку изменить нельзя")


@router.callback_query(F.data == "not_dangerous")
async def not_dangerous(callback: CallbackQuery):
    await mark_non_dangerous(callback.message.video.file_id)
    await callback.message.answer("Спасибо за помощь :)", reply_markup=await kb.admin_main())
    await callback.message.delete()


@router.callback_query(F.data == "ban_user")
async def ban_user(callback: CallbackQuery):
    await permanent_ban_user(callback.message.video.file_id)
    await callback.message.answer("Пользователь заблокирован", reply_markup=await kb.admin_main())
    await remove_video(callback.message.video.file_id)
    await callback.message.delete()


# @router.callback_query(F.data == "buy_time")
# async def choice_offer(callback: CallbackQuery):
#     await callback.message.edit_text("Выберите время", reply_markup=kb.choice_offer_kb)


# @router.callback_query(F.data == "buy_1")
# async def buy_1(callback: CallbackQuery):
#     await callback.message.answer_invoice(title="Покупка времени",
#                                           description="Если тебе не хватает времени",
#                                           payload="1 час",
#                                           currency="rub",
#                                           provider_token=PROVIDER_TOKEN,
#                                           prices=[
#                                               LabeledPrice(
#                                                   label="1 час",
#                                                   amount=6000
#                                               ),
#                                           ])
#
#
# @router.callback_query(F.data == "buy_2")
# async def buy_2(callback: CallbackQuery):
#     await callback.message.answer_invoice(title="Покупка времени",
#                                           description="Если тебе не хватает времени",
#                                           payload="2 часа",
#                                           currency="rub",
#                                           provider_token=PROVIDER_TOKEN,
#                                           prices=[
#                                               LabeledPrice(
#                                                   label="2 часа",
#                                                   amount=11000
#                                               ),
#                                           ])
#
#
# @router.callback_query(F.data == "buy_5")
# async def buy_5(callback: CallbackQuery):
#     await callback.message.answer_invoice(title="Покупка времени",
#                                           description="Если тебе не хватает времени",
#                                           payload="5 часов",
#                                           currency="rub",
#                                           provider_token=PROVIDER_TOKEN,
#                                           prices=[
#                                               LabeledPrice(
#                                                   label="5 часов",
#                                                   amount=25000
#                                               ),
#                                           ])
#
#
# @router.callback_query(F.data == "buy_15")
# async def buy_15(callback: CallbackQuery):
#     await callback.message.answer_invoice(title="Покупка времени",
#                                           description="Если тебе не хватает времени",
#                                           payload="15 часов",
#                                           currency="rub",
#                                           provider_token=PROVIDER_TOKEN,
#                                           prices=[
#                                               LabeledPrice(
#                                                   label="15 часов",
#                                                   amount=70000
#                                               ),
#                                           ])
#
#
# @router.callback_query(F.data == "buy_150")
# async def buy_150(callback: CallbackQuery):
#     await callback.message.answer_invoice(title="Покупка времени",
#                                           description="Если тебе не хватает времени",
#                                           payload="150 часов",
#                                           currency="rub",
#                                           provider_token=PROVIDER_TOKEN,
#                                           prices=[
#                                               LabeledPrice(
#                                                   label="150 часов",
#                                                   amount=600000
#                                               ),
#                                           ])


# @router.pre_checkout_query(lambda query: True)
# async def pre_checkout_query_handler(pre_checkout_query: PreCheckoutQuery):
#     await pre_checkout_query.answer(ok=True)
#     if pre_checkout_query.invoice_payload == "1 час":
#         await add_time(pre_checkout_query.from_user.id, 3600, buy=True)
#     if pre_checkout_query.invoice_payload == "2 часа":
#         await add_time(pre_checkout_query.from_user.id, 7200, buy=True)
#     if pre_checkout_query.invoice_payload == "5 часов":
#         await add_time(pre_checkout_query.from_user.id, 18000, buy=True)
#     if pre_checkout_query.invoice_payload == "15 часов":
#         await add_time(pre_checkout_query.from_user.id, 54000, buy=True)
#     if pre_checkout_query.invoice_payload == "150 часов":
#         await add_time(pre_checkout_query.from_user.id, 540000, buy=True)


# @router.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
# async def successful_payment(message: Message):
#     await message.answer("Спасибо за покупку. Время добавлено")


@router.message(FilterByMode("load"))
async def other_load_action(message: Message):
    await message.answer("Сначала закончи загрузку", reply_markup=kb.stop_load)


@router.message(FilterByMode("default"))
async def other_default_action(message: Message):

    reply_markup = await keyboard_choice(message)

    await message.answer("Я тебя не понял, /help", reply_markup=reply_markup)
