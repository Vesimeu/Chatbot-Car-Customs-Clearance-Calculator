import logging
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from states import CalculatorStates
from keyboards import get_age_keyboard, get_engine_type_keyboard, get_back_keyboard
from calculate import CustomsCalculator, WrongParamException

# Настройка логирования
logger = logging.getLogger(__name__)

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start_command, commands=['start'])
    dp.register_message_handler(cancel_command, commands=['cancel'], state='*')
    dp.register_message_handler(process_age, state=CalculatorStates.age)
    dp.register_message_handler(process_engine_type, state=CalculatorStates.engine_type)
    dp.register_message_handler(process_engine_capacity, state=CalculatorStates.engine_capacity)
    dp.register_message_handler(process_engine_power, state=CalculatorStates.engine_power)
    dp.register_message_handler(process_price, state=CalculatorStates.price)
    dp.register_callback_query_handler(back_handler, lambda c: c.data == 'back', state='*')

async def start_command(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(
        "Добро пожаловать в калькулятор таможенных платежей!\nВыберите возраст автомобиля:",
        reply_markup=get_age_keyboard()
    )
    await CalculatorStates.age.set()

async def cancel_command(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Расчёт отменён. Нажмите /start для нового расчёта.", reply_markup=types.ReplyKeyboardRemove())

async def process_age(message: types.Message, state: FSMContext):
    age = message.text
    if age not in ["до 3", "3-5"]:
        await message.answer("Пожалуйста, выберите возраст из предложенных:", reply_markup=get_age_keyboard())
        return
    await state.update_data(age=age)
    await message.answer(
        "Выберите тип двигателя:",
        reply_markup=get_engine_type_keyboard()
    )
    await CalculatorStates.engine_type.set()

async def process_engine_type(message: types.Message, state: FSMContext):
    engine_type = message.text.lower()
    if engine_type not in ["gasoline", "diesel", "electric", "hybrid"]:
        await message.answer("Пожалуйста, выберите тип двигателя из предложенных:", reply_markup=get_engine_type_keyboard())
        return
    await state.update_data(engine_type=engine_type)
    await message.answer(
        "Введите объём двигателя (см³):",
        reply_markup=get_back_keyboard()
    )
    await CalculatorStates.engine_capacity.set()

async def process_engine_capacity(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await message.answer("Выберите тип двигателя:", reply_markup=get_engine_type_keyboard())
        await CalculatorStates.engine_type.set()
        return
    try:
        engine_capacity = float(message.text)
        if engine_capacity <= 0:
            raise ValueError("Объём двигателя должен быть больше 0")
    except ValueError:
        await message.answer("Введите корректный объём двигателя (число больше 0):", reply_markup=get_back_keyboard())
        return
    await state.update_data(engine_capacity=engine_capacity)
    await message.answer(
        "Введите мощность двигателя (л.с.):",
        reply_markup=get_back_keyboard()
    )
    await CalculatorStates.engine_power.set()

async def process_engine_power(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await message.answer("Введите объём двигателя (см³):", reply_markup=get_back_keyboard())
        await CalculatorStates.engine_capacity.set()
        return
    try:
        engine_power = float(message.text)
        if engine_power <= 0:
            raise ValueError("Мощность двигателя должна быть больше 0")
    except ValueError:
        await message.answer("Введите корректную мощность двигателя (число больше 0):", reply_markup=get_back_keyboard())
        return
    await state.update_data(engine_power=engine_power)
    await message.answer(
        "Введите цену автомобиля (руб.):",
        reply_markup=get_back_keyboard()
    )
    await CalculatorStates.price.set()

async def process_price(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await message.answer("Введите мощность двигателя (л.с.):", reply_markup=get_back_keyboard())
        await CalculatorStates.engine_power.set()
        return
    try:
        price_rub = float(message.text)
        if price_rub < 10000:
            raise ValueError("Цена автомобиля должна быть не менее 10,000 руб.")
    except ValueError:
        await message.answer("Введите корректную цену автомобиля (число не менее 10,000 руб.):", reply_markup=get_back_keyboard())
        return

    data = await state.get_data()
    calculator = CustomsCalculator()
    try:
        calculator.set_vehicle_details(
            age=data['age'],
            engine_capacity=data['engine_capacity'],
            engine_power=data['engine_power'],
            engine_type=data['engine_type'],
            price_rub=price_rub,
            korean_work_rub=0,
            agent_fee_rub=0,
            vladivostok_work_rub=0,
            delivery_rub=0
        )
        results = calculator.calculate()
        response = "\n".join([f"{key}: {value:,.2f} руб." if isinstance(value, (int, float)) else f"{key}: {value}" for key, value in results.items()])
        await message.answer(f"Результаты расчёта:\n{response}", reply_markup=types.ReplyKeyboardRemove())
    except WrongParamException as e:
        await message.answer(f"Ошибка: {e}", reply_markup=types.ReplyKeyboardRemove())
    finally:
        await state.finish()
        await message.answer("Нажмите /start для нового расчёта.")

async def back_handler(callback_query: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state == CalculatorStates.age.state:
        await callback_query.message.answer("Вы уже на первом шаге. Нажмите /start для нового расчёта.")
        await state.finish()
    elif current_state == CalculatorStates.engine_type.state:
        await callback_query.message.edit_text("Выберите возраст автомобиля:", reply_markup=get_age_keyboard())
        await CalculatorStates.age.set()
    elif current_state == CalculatorStates.engine_capacity.state:
        await callback_query.message.edit_text("Выберите тип двигателя:", reply_markup=get_engine_type_keyboard())
        await CalculatorStates.engine_type.set()
    elif current_state == CalculatorStates.engine_power.state:
        await callback_query.message.edit_text("Введите объём двигателя (см³):", reply_markup=get_back_keyboard())
        await CalculatorStates.engine_capacity.set()
    elif current_state == CalculatorStates.price.state:
        await callback_query.message.edit_text("Введите мощность двигателя (л.с.):", reply_markup=get_back_keyboard())
        await CalculatorStates.engine_power.set()
    await callback_query.answer()