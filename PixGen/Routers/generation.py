import os

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from openai import OpenAI

from Admin.config import OPENAI_API
from Database.database import SessionLocal
from Models.models import Users
from image_instuctions import ImageParse

gen_router = Router(name=__name__)
client = OpenAI(api_key=OPENAI_API)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@gen_router.message(Command(prefix="!", commands="gen"))
async def generate(message: Message) -> None:
    try:
        db = next(get_db())
        user_model = db.query(Users).filter(Users.id == message.from_user.id).first()

        if user_model.count_gen_per_day > 0 or user_model.balance >= 0.5:

            await message.answer("Generating image...")
            response = client.images.generate(
                model="dall-e-3",
                prompt=message.text.split("gen")[1],
                size="1024x1024",
                quality="standard",
                n=1,
            )
            image_url = response.data[0].url
            photo = ImageParse.url_to_img(image_url)
            await message.answer("Sending image...")
            await message.answer_photo(photo)
            if user_model.count_gen_per_day > 0:
                user_model.count_gen_per_day = user_model.count_gen_per_day - 1
            else:
                user_model.balance = user_model.balance - 0.5
            db.add(user_model)
            db.commit()
        else:
            await message.answer("😢Sorry, but your balance is insufficient to generate the image. One image "
                                 "generation costs 0.5$")
    except:
        await message.answer("Ups.. Something went wrong")
    finally:
        os.remove('generated_img.png') if os.path.exists('generated_img.png') else None
        db.close()
