from aiogram import Router, Bot
from aiogram import types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.utils.markdown import hitalic

from Admin.config import TOKEN
from Database.database import SessionLocal
from Models.models import Users
from buttons import ButtonManager
from filters.is_admin import IsAdminFilter

admin_router = Router(name=__name__)
admin_router.message.filter(IsAdminFilter())
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@admin_router.message(Command(prefix='/', commands='admin'), IsAdminFilter())
async def change_user_info(message: types.Message) -> None:
    db = next(get_db())
    buttons_for_admin = ButtonManager.create_admin_buttons()
    await message.answer(text="Choose admin option:", reply_markup=buttons_for_admin)


@admin_router.message(lambda message: "User status" in message.text, IsAdminFilter())
async def get_user_status(message: types.Message) -> None:
    db = next(get_db())
    try:
        user_for_searching = int(message.text.split(":")[1])
        user_model = db.query(Users).filter(Users.id == user_for_searching).first()
        await message.answer(text="Connected to user")
        await bot.send_message(message.chat.id,
                               text=hitalic(f"🤠Your profile:\nid: {user_model.id}\nFull name: {user_model.full_name}\n"
                                            f"Can use: {user_model.count_gen_per_day} times for free\nUsername: "
                                            f"@{user_model.username}\nBalance: {user_model.balance}$"))
    except IndexError:
        await message.answer('Enter in this format "User:user_id"')


@admin_router.message(lambda message: "Upgrade" in message.text, IsAdminFilter())
async def upgrade_user_gen_count(message: types.Message) -> None:
    db = next(get_db())
    user_for_searching = int(message.text.split(":")[1])
    new_gen_count = int(message.text.split(":")[2])

    try:
        user_model = db.query(Users).filter(Users.id == user_for_searching).first()
        user_model.count_gen_per_day = new_gen_count
        db.add(user_model)
        db.commit()

        await message.answer(text="Generate number was upgraded")
    except IndexError:
        await message.answer(text=f"Enter in this format 'Upgrade:user_id:gen number'")
    finally:
        db.close()


@admin_router.message(lambda message: message.text == "User menu")
async def off_admin_menu(message: types.Message) -> None:
    await message.answer(text="Choose user options:", reply_markup=ButtonManager.markup_user)
