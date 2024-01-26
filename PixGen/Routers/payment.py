from aiogram import Router, types, Bot
from aiogram.enums import ParseMode

from aiogram.types import LabeledPrice

from Admin.config import PAYMENT_TOKEN, TOKEN
from Database.database import SessionLocal
from Models.models import Users
from buttons import ButtonManager

payment_router = Router(name=__name__)
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@payment_router.message(lambda message: message.text == "Buy subscription")
async def buy_subscription_button(message: types.Message) -> None:
    await message.answer("Choose top up number:", reply_markup=ButtonManager.create_price_buttons())


@payment_router.callback_query(lambda c: c.data.startswith("pay_"))
async def handle_payment(callback_query: types.CallbackQuery) -> None:
    amount = int(callback_query.data.split("_")[1])
    price = LabeledPrice(label=f'Top up ${amount}', amount=amount * 100)

    await bot.send_invoice(
        chat_id=callback_query.from_user.id,
        title=f"Top up ${amount}",
        description="Top up PixGen balance",
        provider_token=PAYMENT_TOKEN,
        currency="USD",
        prices=[price],
        start_parameter="create_invoice",
        payload=f"pay_{amount}"
    )
    await callback_query.answer()


@payment_router.pre_checkout_query(lambda query: True)
async def pre_checkout_query(pre_check: types.PreCheckoutQuery) -> None:
    await bot.answer_pre_checkout_query(pre_check.id, ok=True)


@payment_router.message(lambda content_types: types.ContentType.SUCCESSFUL_PAYMENT)
async def payment(message: types.Message) -> None:
    print("Successful payment")
    db = next(get_db())
    payment_info = message.successful_payment
    user_model = db.query(Users).filter(Users.id == message.from_user.id).first()
    user_model.balance += payment_info.total_amount // 100
    db.add(user_model)
    db.commit()
    db.close()
    print(f"Currency: {payment_info.currency}")
    print(f"Total amount: {payment_info.total_amount // 100}")

    await bot.send_message(
        message.chat.id,
        text=f"Payment {payment_info.total_amount // 100} {payment_info.currency} was successful"
    )
