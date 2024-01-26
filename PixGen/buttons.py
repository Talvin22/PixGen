from aiogram import types


class ButtonManager:
    sub_status_button = types.KeyboardButton(text="My status")
    buy_sub_button = types.KeyboardButton(text="Buy subscription")
    help_button = types.KeyboardButton(text="Get help")
    back_button = types.KeyboardButton(text="Gen")
    markup_user = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [sub_status_button, buy_sub_button],
            [help_button, back_button]
        ]
    )

    @staticmethod
    def create_admin_buttons():
        sub_status_button = types.KeyboardButton(text="User status")
        change_gen_number = types.KeyboardButton(text="Upgrade gen number")
        # back_button = types.KeyboardButton(text="Gen of users") #get a picture of top generated for week
        back_button = types.KeyboardButton(text="User menu")
        markup_admin = types.ReplyKeyboardMarkup(
            resize_keyboard=True,
            keyboard=[
                [sub_status_button, change_gen_number],
                [back_button]
            ]
        )
        return markup_admin

    @classmethod
    async def create_button_menu_callback(cls, callback_query: types.CallbackQuery, text: str):
        await callback_query.message.answer(text, reply_markup=cls.markup_user)

    @staticmethod
    async def create_button_menu_exist(message: types.Message):
        await message.answer("Ups... You are already using this bot 🤗", reply_markup=ButtonManager.markup_user)

    @staticmethod
    def create_price_buttons() -> types.InlineKeyboardMarkup:
        button_pay_1 = types.InlineKeyboardButton(text="Top up for 1$", callback_data="pay_1")
        button_pay_5 = types.InlineKeyboardButton(text="Top up for 5$", callback_data="pay_5")
        button_pay_10 = types.InlineKeyboardButton(text="Top up for 10$", callback_data="pay_10")
        inline_kb = types.InlineKeyboardMarkup(inline_keyboard=[[button_pay_1, button_pay_5, button_pay_10]])
        return inline_kb
