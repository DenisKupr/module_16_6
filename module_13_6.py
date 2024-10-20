from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

api = ""
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

# Обычная клавиатура для главного меню
kb = ReplyKeyboardMarkup(resize_keyboard=True)
button = KeyboardButton(text='Рассчитать')
button2 = KeyboardButton(text='Информация')
kb.add(button, button2)

# Инлайн клавиатура для дополнительных опций
inline_kb = InlineKeyboardMarkup(row_width=1)
button_calories = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
button_formulas = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
inline_kb.add(button_calories, button_formulas)

class UserState(StatesGroup):
    age = State()   # Состояние для возраста
    growth = State()   # Состояние для роста
    weight = State()   # Состояние для веса

@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    await message.answer("Привет! Я бот, помогающий твоему здоровью. Выберите действие:", reply_markup=kb)

# Обработчик для кнопки 'Рассчитать'
@dp.message_handler(text="Рассчитать")
async def main_menu(message: types.Message):
    await message.answer("Выберите опцию:", reply_markup=inline_kb)

def is_formulas_callback(call: types.CallbackQuery):
    return call.data == 'formulas'

@dp.callback_query_handler(is_formulas_callback)
async def get_formulas(call: types.CallbackQuery):
    formula_text = ("Формула Миффлина-Сан Жеора для расчёта нормы калорий:\n"
                    "Для мужчин: 10 * вес (кг) + 6.25 * рост (см) - 5 * возраст (годы) + 5\n"
                    "Для женщин: 10 * вес (кг) + 6.25 * рост (см) - 5 * возраст (годы) - 161")
    await call.message.answer(formula_text)

# Обработчик inline кнопки 'Рассчитать норму калорий'
@dp.callback_query_handler(lambda call: call.data == 'calories')
async def set_age(call: types.CallbackQuery):
    await call.message.answer("Введите ваш возраст:")
    await UserState.age.set()

# Обработчик для ввода возраста
@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост:')
    await UserState.growth.set()

# Обработчик для ввода роста
@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес:')
    await UserState.weight.set()

# Обработчик для ввода веса и расчета калорий
@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    await state.update_data(weight=message.text)
    data = await state.get_data()

    age = int(data.get('age'))
    growth = int(data.get('growth'))
    weight = int(data.get('weight'))

    # Упрощенная формула Миффлина-Сан Жеора для мужчин
    bmr = 10 * weight + 6.25 * growth - 5 * age + 5
    await message.answer(f'Ваша норма калорий: {bmr} ккал/день')

    await state.finish()

# Обработчик для кнопки 'Информация'
@dp.message_handler(text="Информация")
async def information(message: types.Message):
    await message.answer("Этот бот помогает рассчитать норму калорий.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)