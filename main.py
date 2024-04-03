from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.command import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton,ReplyKeyboardRemove
from aiogram.types.input_file import FSInputFile
import asyncio
import re

TOKEN_API = '7007442319:AAFia58P8WwKSJABnGizTNbWtQZKx5TVwyU'
bot = Bot(TOKEN_API)
dp = Dispatcher()

class Form(StatesGroup):
    name = State()
    phone = State()
    comment = State()
    apply = State()

@dp.message(Command("start"))
async def set_start(message: Message, state: FSMContext):
    await message.answer(f"{message.from_user.first_name}, Добро пожаловать в компанию DamnIT")
    await message.answer("Напишите свое ФИО")
    await state.set_state(Form.name.state)

@dp.message(Form.name)
async def set_name(message: Message, state: FSMContext):
    if message.text.count(' ') != 2 or any(ch.isdigit() for ch in message.text):
        await message.answer("Введено некорректрое ФИО. Пожалуйста повторите ввод")
        return
    await state.update_data(name=message.text)
    await state.set_state(Form.phone.state)
    await message.answer("Укажите Ваш номер телефона")

@dp.message(Form.phone)
async def set_phone(message: Message, state: FSMContext):
    result = re.match(r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$',message.text)
    if not result:
        await message.answer("Введенный номер телефона некорректен. Пожалуйста повторите ввод")
        return
    await state.update_data(phone=message.text)
    await state.set_state(Form.comment.state)
    await message.answer("Напишите любой комментарий")

@dp.message(Form.comment)
async def set_comm(message: Message, state: FSMContext):
    await state.update_data(comment=message.text)
    await message.answer("Последний шаг! Ознакомься с вводными положениями")
    await message.answer_document(FSInputFile("test.pdf"))
    keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Да")]], resize_keyboard=True)
    await message.answer("Ознакомился?", reply_markup=keyboard)
    await state.set_state(Form.apply.state)

@dp.message(Form.apply)
async def set_apply(message: Message, state: FSMContext):
    if message.text != "Да":
        await message.answer("Пожалуйста нажмите на кномку принять, если Вы ознакомились.")
        return
    await message.answer("Спасибо за успешную регистрацию", reply_markup=ReplyKeyboardRemove())
    await message.answer_photo(FSInputFile("photo.jpg"))
    data = await state.get_data()
    await bot.send_message("6262559451", f"Пришла новая информация от {message.from_user.username}\n\
ФИО: {data['name']}\nТелефон: {data['phone']}\nКомментарий: {data['comment']}")
    await state.clear()

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
