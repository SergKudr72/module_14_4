from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

from crud_functions import get_all_products



api = "???token_bot???"
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

kb = ReplyKeyboardMarkup(resize_keyboard=True)
button1 = KeyboardButton(text="Рассчитать")
button2 = KeyboardButton(text="Информация")
button3 = KeyboardButton(text="Купить")
kb.row(button1, button2)
kb.add(button3)

kb_call = InlineKeyboardMarkup()
button4 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
button5 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
kb_call.add(button4, button5)

kb_gender = InlineKeyboardMarkup()
button6 = InlineKeyboardButton(text='мужской', callback_data='man')
button7 = InlineKeyboardButton(text='женский', callback_data='woman')
kb_gender.add(button6, button7)

kb_gender_cal = InlineKeyboardMarkup()
button8 = InlineKeyboardButton(text='мужской', callback_data='man_cal')
button9 = InlineKeyboardButton(text='женский', callback_data='woman_cal')
kb_gender_cal.add(button8, button9)

kb_product = InlineKeyboardMarkup()
button10 = InlineKeyboardButton(text="Продукт 1", callback_data='product_buying')
button11 = InlineKeyboardButton(text="Продукт 2", callback_data='product_buying')
button12 = InlineKeyboardButton(text="Продукт 3", callback_data='product_buying')
button13 = InlineKeyboardButton(text="Продукт 4", callback_data='product_buying')
kb_product.row(button10, button11, button12, button13)


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.message_handler(commands=['start'])
async def start_message(message):
    await message.answer("Привет! Я бот помогающий твоему здоровью.", reply_markup=kb)


@dp.message_handler(text="Информация")
async def info_message(message):
    await message.answer("Данный бот создан для помощи в расчете необходимого количества килокалорий в сутки "
                         "для каждого конкретного человека по формуле Миффлина-Сан Жеора")


@dp.message_handler(text="Купить")
async def get_buying_list(message):
    products = get_all_products()

    for index, product in enumerate(products, start=1):
        title, description, price = product[1], product[2], product[3]
        await message.answer(f"Название: {title} | Описание: {description} | Цена: {price}")
        with open(f'product_foto/Product{index}.png', 'rb') as img:
            await message.answer_photo(img)
    await message.answer("Выберите продукт для покупки:", reply_markup=kb_product)


@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    await call.message.answer("Вы успешно приобрели продукт!")
    await call.answer()


@dp.message_handler(text="Рассчитать")
async def fsm_send_menu(message):
    await message.answer("Выберите опцию:", reply_markup=kb_call)


@dp.callback_query_handler(text='formulas')
async def get_genders_formulas(call):
    await call.message.answer('Выберите свой пол:', reply_markup=kb_gender)
    await call.answer()


@dp.callback_query_handler(text=('man', 'woman'))
async def get_formulas(call):
    if call.data == 'man':
        await call.message.answer("Формула расчета для мужчин: (10 x вес (кг)) "
                                  "+ (6,25 x рост (см)) – (5 x возраст (г)) + 5")
        await call.answer()
    elif call.data == 'woman':
        await call.message.answer("Формула расчета для женщин: (10 x вес (кг)) "
                                  "+ (6,25 x рост (см)) – (5 x возраст (г)) – 161")
        await call.answer()


@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст (лет):')
    await UserState.age.set()
    await call.answer()


@dp.message_handler(state=UserState.age)
async def fsm_set_growth(message, state):
    try:
        await state.update_data(first_age=int(message.text))
        await UserState.growth.set()
        await message.answer('Введите свой рост (см):')
    except ValueError:
        await message.answer('Введены некорректные данные по возрасту.')


@dp.message_handler(state=UserState.growth)
async def fsm_set_weight(message, state):
    try:
        await state.update_data(first_growth=int(message.text))
        await UserState.weight.set()
        await message.answer('Введите свой вес (кг):')
    except ValueError:
        await message.answer('Введены некорректные данные по росту.')


@dp.message_handler(state=UserState.weight)
async def fsm_set_weight(message, state):
    try:
        await state.update_data(first_weight=int(message.text))
        await message.answer('Выберите свой пол:', reply_markup=kb_gender_cal)
    except ValueError:
        await message.answer('Введены некорректные данные по весу.')


@dp.callback_query_handler(state=UserState.weight, text=('man_cal', 'woman_cal'))
async def fsm_send_calories(call, state):
    data = await state.get_data()
    if call.data == 'man_cal':
        result_m = round(
            10 * int(data['first_weight']) + 6.25 * int(data['first_growth']) - 5 * int(data['first_age']) + 5, 2)
        await call.message.answer(f'Ваша норма калорий для мужчин: {result_m} ккал')
        await call.answer()
        await state.finish()
    elif call.data == 'woman_cal':
        result_w = round(
            10 * int(data['first_weight']) + 6.25 * int(data['first_growth']) - 5 * int(data['first_age']) - 161, 2)
        await call.message.answer(f'Ваша норма калорий для женщин: {result_w} ккал')
        await call.answer()
        await state.finish()


@dp.message_handler()
async def all_messages(message):
    await message.answer("Введите команду /start, чтобы начать общение.")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
