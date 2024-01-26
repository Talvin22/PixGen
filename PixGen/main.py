import sys
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hitalic
from aiogram.enums import ParseMode
from sqlalchemy.exc import IntegrityError
from aiogram import types

from Admin.admin_menu import admin_router
from Models.models import Users
from Admin.config import TOKEN, OPENAI_API
from openai import OpenAI
from Models import models
from Database.database import engine, SessionLocal
from Routers.generation import gen_router
from Routers.payment import payment_router
from buttons import ButtonManager

dp = Dispatcher()
client = OpenAI(api_key=OPENAI_API)
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
models.Base.metadata.create_all(bind=engine)
dp.include_router(router=admin_router)
dp.include_router(router=gen_router)
dp.include_router(router=payment_router)


async def main() -> None:
    await dp.start_polling(bot)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@dp.message(CommandStart())
async def start_bot(message: Message) -> None:
    db = next(get_db())
    if db.query(Users).filter(Users.id == message.from_user.id).first():
        await ButtonManager.create_button_menu_exist(message)
    else:
        agree_button = types.InlineKeyboardButton(text="Agree ✅", callback_data="agree")
        inline_kb = types.InlineKeyboardMarkup(inline_keyboard=[[agree_button]])
        await message.answer(hitalic("Hey! To use the bot, you need to read the terms of use and privacy policy ☺️"),
                             reply_markup=inline_kb)


@dp.callback_query(lambda c: c.data == 'agree')
async def handle_agree(callback_query: types.CallbackQuery) -> None:
    db = next(get_db())
    try:
        if db.query(Users).filter(Users.id == callback_query.from_user.id).first():
            await ButtonManager.create_button_menu_callback(callback_query, "Ups... You are already using this "
                                                                            "bot 🤗")
        else:
            user_model = Users(id=callback_query.from_user.id,
                               full_name=callback_query.from_user.full_name,
                               username=callback_query.from_user.username)

            db.add(user_model)
            db.commit()
        await bot.send_message(chat_id=callback_query.from_user.id, text="Thank you for agreeing!")
        await callback_query.message.answer(
            hitalic('Hey\nI`m PixGen bot created to generate a pictures from your imagination.\nJust '
                    'send me your want in format: !gen + your imagination'))

        await ButtonManager.create_button_menu_callback(callback_query, "Choose option:")

    except IntegrityError as e:
        print('Got error: ', e)
    finally:
        db.close()

    await callback_query.answer(text="Welcome🥰")


@dp.message(lambda message: message.text == 'My status')
async def handle_status_button(message: types.Message) -> None:
    db = next(get_db())
    user_model = db.query(Users).filter(Users.id == message.from_user.id).first()
    if user_model:
        await bot.send_message(message.chat.id,
                               text=hitalic(f"🤠Your profile:\nid: {user_model.id}\nFull name: {user_model.full_name}\n"
                                            f"Can use: {user_model.count_gen_per_day} times for free\nUsername: "
                                            f"@{user_model.username}\nBalance: {user_model.balance}$"))
    else:
        await message.answer("User not found")


@dp.message(lambda message: message.text == "Get help" or message.text == "/help")
async def get_help(message: types.Message) -> None:
    await message.answer(text=f"🤖About generation:\n\nOne generation costs 0.5$. If your balance is less than 0.5$, "
                              "you will not be able to generate images. But all users also have access to "
                              "3 free image generation. If you did not agree to the terms of use when you started the "
                              "bot,"
                              "you will still not be able to generate images\n\n\n"
                              "💰About payment:\n\nPayment is made by a special service that allows you to increase "
                              "the security"
                              "of payment and money back in case if an accidental payment\n\n\n"
                              "📳 If you have a specific problem, please contact my developer, he will be happy to "
                              "help you - @talvin_dev")


@dp.message(lambda message: message.text == "Gen")
async def gen_button(message: types.Message) -> None:
    await message.answer(text="To generate an image, just enter the command: !gen + your want")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
